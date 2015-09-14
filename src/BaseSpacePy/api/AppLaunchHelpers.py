"""
A collection of methods to help derive and prepare the launch json objects consumed by BaseSpaceAPI.launchApp

There are three object groups:

1. AppSessionMetaData. This reads the appsession from an existing app run and provides methods to extract details
    about these app sessions so that more apps of the same type can be launched
2. LaunchSpecifcation. One an app launch is understood, it can be turned into an AppSpecification, that understands
    the properties needed to launch an app, their types and other details about them.
3. LaunchPayload. Given a LaunchSpecification, this object hodls an individual group of argument for a specific launch
    there are various convenience methods to extract useful information from those payloads.
"""

import abc

# items in this list should not be added to the inferred properties
import copy
import json
import os

from BaseMountInterface import BaseMountInterface
from BaseSpaceAPI import BaseSpaceAPI

api = BaseSpaceAPI()
API_VERSION = api.version

SKIP_PROPERTIES = ["app-session-name"]

# if these strings are in the property names, we should not try to capture default values for them.
BS_ENTITIES = ["sample", "project", "appresult", "file"]
BS_ENTITY_LIST_NAMES = ["Samples", "Projects", "AppResults", "Files"]

LAUNCH_HEADER = {
    "StatusSummary": "AutoLaunch",
    "AutoStart": True,
}


class AppSessionMetaData(object):
    """
    Class to help extract information from an appsession.
    This is an abstract base class without two concrete implementations:
    1. AppSessionMetaDataSDK: Working on an appsession that has been derived via an SDK call (a Python object)
    2. AppSessionMetaDataRaw: Working on a raw appsession (a .json object)

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, appsession_metadata):
        """

        :param appsession_metadata: metadata from an appsession. This could be a dict or an SDK object
        """
        self.asm = appsession_metadata

    def get_refined_appsession_properties(self):
        appsession_properties = self.get_properties()
        properties = []
        defaults = {}
        for as_property in appsession_properties:
            property_name = str(self.unpack_bs_property(as_property, "Name"))
            property_type = str(self.unpack_bs_property(as_property, "Type"))
            if not property_name.startswith("Input"):
                continue
            if property_name.count(".") != 1:
                continue
            property_basename = property_name.split(".")[-1]
            if property_basename in SKIP_PROPERTIES:
                continue
            if property_basename in BS_ENTITY_LIST_NAMES:
                continue
            this_property = {
                "Name": property_name,
                "Type": property_type,
            }
            properties.append(this_property)
            bald_type = property_type.translate(None, "[]")
            if bald_type in BS_ENTITIES:
                continue
            if property_type.endswith("[]"):
                default_var = self.unpack_bs_property(as_property, "Items")
                # this slightly odd logic is because of a BaseSpace bug. From Kent Ho:
                """
                2.       For string array types of properties (string[]), for some reason, when you post with an array of length x,
                the AppSession.json created has the same array but of length x+1 (with the first array element appended at the end an extra time).
                For example, if you post ["1"], it becomes ["1","1"] or if you post ["1","2"], it becomes ["1","2","1"].
                This could really mess up mapping or what not if people rely on the length of the array to assign settings
                to samples or what not within the native app, and it's weird behavior that's unexpected.
                """
                if len(default_var) == 1:
                    defaults[property_basename] = default_var
                else:
                    defaults[property_basename] = default_var[:-1]
            else:
                default_var = self.unpack_bs_property(as_property, "Content")
                defaults[property_basename] = default_var
        properties = self._trim_properties_app_results(properties)
        return properties, defaults

    @staticmethod
    @abc.abstractmethod
    def unpack_bs_property(bs_property, attribute):
        return

    @staticmethod
    @abc.abstractmethod
    def get_properties(self):
        return

    @staticmethod
    def _trim_properties_app_results(properties):
        """
        special trimming to deal with file properties
        if there is a file property, we don't need any appresult properties, since they are taken care of by the file entries
        """
        has_file = any([prop["Type"] == "file" for prop in properties])
        if has_file:
            new_properties = [prop for prop in properties if prop["Type"].translate(None, "[]") != "appresult"]
        else:
            new_properties = properties
        return new_properties


class AppSessionMetaDataSDK(AppSessionMetaData):
    def get_properties(self):
        return self.asm.Properties.Items

    def get_app_name(self):
        return self.asm.Application.Name

    def get_app_id(self):
        return self.asm.Application.Id

    @staticmethod
    def unpack_bs_property(bs_property, attribute):
        return getattr(bs_property, attribute)


class AppSessionMetaDataRaw(AppSessionMetaData):
    def get_properties(self):
        return self.asm["Response"]["Properties"]["Items"]

    def get_app_name(self):
        return self.asm["Response"]["Application"]["Name"]

    def get_app_id(self):
        return self.asm["Response"]["Application"]["Id"]

    @staticmethod
    def unpack_bs_property(bs_property, attribute):
        return bs_property[attribute]


class LaunchSpecificationException(Exception):
    pass


class LaunchSpecification(object):
    """
    Class to help work with a BaseSpace app launch specification, which includes the properties and any defaults
    """

    def __init__(self, properties, defaults):
        self.properties = properties
        self.property_lookup = dict((self.clean_name(property_["Name"]), property_) for property_ in self.properties)
        self.defaults = defaults

    @staticmethod
    def clean_name(parameter_name):
        """
        strip off the Input. prefix, which is needed by the launch payload but gets in the way otherwise
        :param parameter_name: parameter name to clean
        :return: cleaned name
        """
        prefix, cleaned_name = parameter_name.split(".")
        assert prefix == "Input"
        return cleaned_name

    def resolve_list_variables(self, var_dict):
        """
        ensure each variable has the right list type
        :param var_dict: dictionary of variable/value pairs for an app launch
        :return: (nothing)
        :raises: AppLaunchException if the listiness of a variable doesn't match its parameter
        """
        for varname in var_dict:
            varval = var_dict[varname]
            if self.is_list_property(varname) and not isinstance(varval, list):
                var_dict[varname] = [varval]
                # raise AppLaunchException("non-list property specified for list parameter")
            if not self.is_list_property(varname) and isinstance(varval, list):
                raise LaunchSpecificationException("list property specified for non-list parameter")

    @staticmethod
    def make_sample_attribute_entry(sampleid, wrapped_sampleid, sample_attributes):
        """
        Augment each sample with an attribute
        this only permits homogenous attributes - samples must all have the same

        :param sampleid: bald sample id
        :param wrapped_sampleid: sample id wrapped as an API reference
        :param sample_attributes: dict of key/value pairs of attributes to attach
        :return:
        """
        this_sample_attributes = [
            {
                "Key": "FieldId",
                "Values": [
                    "sample-id"
                ]
            },
            {
                "Key": "ResourceType",
                "Values": [
                    "sample"
                ]
            },
            {
                "Key": "ResourceId",
                "Values": [
                    sampleid
                ]
            },
            {
                "Key": "ResourceHref",
                "Values": [
                    wrapped_sampleid
                ]
            },
        ]
        for attribute_name in sample_attributes:
            attribute_value = sample_attributes[attribute_name]
            attribute_entry = {
                "Key": "Input.%s" % attribute_name,
                "Values": [
                    attribute_value
                ]
            }
            this_sample_attributes.append(attribute_entry)
        return this_sample_attributes

    def populate_properties(self, var_dict, sample_attributes={}):
        """
        Uses the base properties of the object and an instantiation of those properties (var_dict)
        build a dictionary that represents the launch payload

        sample_attributes is to tag each sample with an attribute and maps an attribute name to its value
        it will cause a map[] object to be added to the properties specifying each sample
        and giving it the attribute provided in sample_attributes
        note that these can't be heterogeneous - they will be applied to every sample!

        :param var_dict (dict): mapping (cleaned) property name to its value
        :param sample_attributes (dict): mapping containing key/value attribues to be applied to every sample
        """
        populated_properties = copy.copy(self.properties)
        if sample_attributes:
            all_sample_attributes = {
                "Type": "map[]",
                "Name": "Input.sample-id.attributes",
                "items": []
            }
        for property_ in populated_properties:
            property_name = self.clean_name(property_["Name"])
            property_type = property_["Type"]
            bald_type = str(property_type).translate(None, "[]")
            property_value = var_dict[property_name]
            processed_value = ""
            if bald_type in BS_ENTITIES:
                if "[]" in property_type:
                    processed_value = []
                    for one_val in property_value:
                        wrapped_value = "%s/%ss/%s" % (API_VERSION, bald_type, one_val)
                        processed_value.append(wrapped_value)
                        if sample_attributes and bald_type == "sample":
                            one_sample_attributes = self.make_sample_attribute_entry(one_val, wrapped_value,
                                                                                     sample_attributes)
                            all_sample_attributes["items"].append(one_sample_attributes)
                else:
                    processed_value = "%s/%ss/%s" % (API_VERSION, bald_type, property_value)
                    if sample_attributes and bald_type == "sample":
                        one_sample_attributes = self.make_sample_attribute_entry(property_value, processed_value,
                                                                                 sample_attributes)
                        sample_attributes["Items"].append(one_sample_attributes)
            if not processed_value:
                processed_value = property_value
            if "[]" in property_type:
                property_["items"] = processed_value
            else:
                property_["Content"] = processed_value
        if sample_attributes:
            populated_properties.append(all_sample_attributes)
        return populated_properties

    def get_variable_requirements(self):
        """
        :return: get all the cleaned up properties for this launch specification
        """
        return set((self.clean_name(property_["Name"]) for property_ in self.properties))

    def get_minimum_requirements(self):
        """
        get the minimum requirements the user needs to specify
        this is all the properties minus those that have a default value
        because of the way the templates are derived, this should be a list of BaseSpace entities
        :return: sorted list of the minimum requirements
        """
        all_variables = self.get_variable_requirements()
        all_defaults = set(self.defaults.keys())
        minimum_vars = list(all_variables - all_defaults)
        minimum_vars.sort()
        return minimum_vars

    def get_property_type(self, property_name):
        """
        get the type for a property
        :param property_name (str):
        :return: type (str)
        """
        if property_name in self.property_lookup:
            return self.property_lookup[property_name]["Type"]
        else:
            raise LaunchSpecificationException("asking for type for unknown variable: %s" % property_name)

    def get_property_bald_type(self, property_name):
        """
        same as get_property_type, but strip off any list specifier
        """
        return str(self.get_property_type(property_name)).translate(None, "[]")

    def is_list_property(self, property_name):
        """
        is a given property a list property
        :param property_name:
        :return: (bool)
        """
        return "[]" in self.get_property_type(property_name)

    def count_list_properties(self):
        """
        How many list properties are there in the minimum requirements list
        :return: (int)
        """
        return [self.is_list_property(property_name) for property_name in self.get_minimum_requirements()].count(True)

    def make_launch_json(self, user_supplied_vars, launch_name, sample_attributes={}, agent_id=""):
        """
        build the launch payload (a json blob as a string) based on the supplied mapping from property name to value

        this is the main entry point for the object and most of the work of making the launch json is done here
        or in populate_properties
        :param user_supplied_vars: dict of property_name -> value
        :param launch_name: name for the launch
        :param sample_attributes: dict of key -> value to be attached to every sample
        :param agent_id: an AgentId to be attached to the launch, if specifed
        """
        # build basic headers
        launch_dict = copy.copy(LAUNCH_HEADER)
        launch_dict["Name"] = launch_name
        if agent_id:
            launch_dict["AgentId"] = agent_id
        supplied_var_names = set(user_supplied_vars.keys())
        required_vars = set(self.get_minimum_requirements())
        if required_vars - supplied_var_names:
            raise LaunchSpecificationException(
                "Compulsory variable(s) missing! (%s)" % str(required_vars - supplied_var_names))
        if supplied_var_names - (self.get_variable_requirements() | {"LaunchName"}):
            print "warning! unused variable(s) specified: (%s)" % str(
                supplied_var_names - self.get_variable_requirements())
        all_vars = copy.copy(self.defaults)
        all_vars.update(user_supplied_vars)
        self.resolve_list_variables(all_vars)
        properties_dict = self.populate_properties(all_vars, sample_attributes)
        launch_dict["Properties"] = properties_dict
        return json.dumps(launch_dict)

    def format_property_information(self):
        lines = ["\t".join(["Name", "Type", "Default"])]
        minimum_requirements = self.get_minimum_requirements()
        for property_ in sorted(self.properties):
            property_name = self.clean_name(property_["Name"])
            if property_name in minimum_requirements:
                continue
            property_type = property_["Type"]
            output = [property_name, property_type]
            if property_name in self.defaults:
                output.append(str(self.defaults[property_name]))
            lines.append("\t".join(output))
        return "\n".join(lines)

    def dump_property_information(self):
        """
        dump all properties with their type and any default value
        for verbose usage information output
        """
        print self.format_property_information()

    def format_minimum_requirements(self):
        minimum_requirements = self.get_minimum_requirements()
        description = ["%s (%s)" % (varname, self.get_property_type(varname)) for varname in minimum_requirements]
        return " ".join(description)

class LaunchPayload(object):
    """
    Helper class to faciliate users making the user_supplied_vars dictionary
    that needs to be passed into LaunchSpecification.make_launch_json()
    in previous iterations, we would just manage that as a dict mapping property names to literal string values
    but this class has some methods to make it more convenient, including automatically generating launch names
    and mapping BaseMount paths to the API reference strings the launch needs
    """

    LAUNCH_NAME = "LaunchName"

    def __init__(self, launch_spec, args, configoptions):
        """
        :param launch_spec (LaunchSpecification)
        :param args (list) list or arguments to the app launch. These could be BaseSpace IDs or BaseMount paths
        :param configoptions (dict) key->value mapping for additional option values, such as genome-id
        the ordering of args has to match the ordering of the sorted minimum requirements
        It might be better to use a dict, but ultimately call order has to match at some point
        """
        self._launch_spec = launch_spec
        self._args = args
        self._configoptions = configoptions

    def _find_all_entity_names(self, entity_type):
        """
        get all the entity names for a particular entity type
        used to make useful launch names
        :param entity_type: the entity type to look for
        :return: list of entity names
        """
        entity_names = []
        varnames = self._launch_spec.get_minimum_requirements()
        for i, varname in enumerate(varnames):
            arg = self._args[i]
            if self._launch_spec.get_property_bald_type(varname) == entity_type:
                if not self._launch_spec.is_list_property(varname):
                    arg = [arg]
                for entry in arg:
                    if os.path.exists(entry):
                        bmi = BaseMountInterface(entry)
                        entity_names.append(bmi.name)
        return entity_names

    def derive_launch_name(self, app_name):
        """
        makes a launch name for this payload based on the entities used in the launch
        :param app_name: name of app
        :return: useful name for app launch
        """
        if self.LAUNCH_NAME in self._configoptions:
            return self._configoptions[self.LAUNCH_NAME]
        else:
            launch_names = self._find_all_entity_names("sample")
            if not launch_names:
                launch_names = self._find_all_entity_names("appresult")
            if len(launch_names) > 3:
                contracted_names = launch_names[:3] + ["%dmore" % (len(launch_names) - 3)]
                launch_instance_name = "+".join(contracted_names)
            else:
                launch_instance_name = "+".join(launch_names)
            return "%s : %s" % (app_name, launch_instance_name)

    def is_valid_basespace_id(self, varname, basespace_id):
        """
        This is not really needed if users are specifying inputs as BaseMount paths,
        because in these cases validation happens elsewhere

        To validate other kinds of ID, we should (TODO!) resolve the type based on the varname
        and use the SDK to look it up.
        """
        return True

    def to_basespace_id(self, param_name, varval):
        """
        Checks if a value for a parameter looks like a BaseMount path and tries to convert it into a BaseSpace ID

        :param param_name: name of the parameter
        :param varval: value of parameter

        :return basespaceid
        """
        if varval.startswith("/") and not os.path.exists(varval):
            raise LaunchSpecificationException("Parameter looks like a path, but does not exist: %s" % varval)
        if os.path.exists(varval):
            bmi = BaseMountInterface(varval)
            spec_type = self._launch_spec.get_property_bald_type(param_name)
            basemount_type = bmi.type
            if spec_type != basemount_type:
                raise LaunchSpecificationException(
                    "wrong type of BaseMount path selected: %s needs to be of type %s" % (varval, spec_type))
            bid = bmi.id
        else:
            bid = varval
        assert self.is_valid_basespace_id(param_name, bid)
        return bid

    def get_args(self):
        """
        perform mapping from BaseMount paths to BaseSpace IDs for all arguments
        also resolves the ordering and flattens them into a dict ready to create a launch payload
        """
        arg_map = {}
        params = self._launch_spec.get_minimum_requirements()
        for i, param_name in enumerate(params):
            arg = self._args[i]
            if isinstance(arg, list):
                arg_map[param_name] = [self.to_basespace_id(param_name, arg_part) for arg_part in arg]
            else:
                arg_map[param_name] = self.to_basespace_id(param_name, arg)
        return arg_map

    def get_all_variables(self):
        """
        both constants and arguments
        """
        all_vars = copy.copy(self._configoptions)
        all_vars.update(self.get_args())
        return all_vars
