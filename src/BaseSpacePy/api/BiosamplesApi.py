from __future__ import absolute_import

import re  # noqa: F401
import six
from BaseSpacePy.api.APIClient import APIClient


class BiosamplesApi(object):
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = APIClient()
        self.api_client = api_client

    def get_v2_biosamples(self, **kwargs):  # noqa: E501
        """Get a list of biosamples  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] biosamplename: Only return biosamples with the given BioSampleName(s)
        :param list[str] include: Sub elements to include in the response
        :param list[str] propertynamestartswith:
        :param list[str] status: Only return biosamples with the given Status(es)
        :param list[str] labstatus: Only return biosamples with the given LabStatus(es)
        :param list[str] projectid: Only return biosamples with the specified default projects or datasets in those projects
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2BiologicalSampleCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_with_http_info(**kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_with_http_info(self, **kwargs):  # noqa: E501
        """Get a list of biosamples  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param list[str] biosamplename: Only return biosamples with the given BioSampleName(s)
        :param list[str] include: Sub elements to include in the response
        :param list[str] propertynamestartswith:
        :param list[str] status: Only return biosamples with the given Status(es)
        :param list[str] labstatus: Only return biosamples with the given LabStatus(es)
        :param list[str] projectid: Only return biosamples with the specified default projects or datasets in those projects
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2BiologicalSampleCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['biosamplename', 'include', 'propertynamestartswith', 'status', 'labstatus', 'projectid', 'sortby', 'offset', 'limit', 'sortdir']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'biosamplename' in params:
            query_params.append(('biosamplename', params['biosamplename']))  # noqa: E501
            collection_formats['biosamplename'] = 'csv'  # noqa: E501
        if 'include' in params:
            query_params.append(('include', params['include']))  # noqa: E501
            collection_formats['include'] = 'csv'  # noqa: E501
        if 'propertynamestartswith' in params:
            query_params.append(('propertynamestartswith', params['propertynamestartswith']))  # noqa: E501
            collection_formats['propertynamestartswith'] = 'csv'  # noqa: E501
        if 'status' in params:
            query_params.append(('status', params['status']))  # noqa: E501
            collection_formats['status'] = 'csv'  # noqa: E501
        if 'labstatus' in params:
            query_params.append(('labstatus', params['labstatus']))  # noqa: E501
            collection_formats['labstatus'] = 'csv'  # noqa: E501
        if 'projectid' in params:
            query_params.append(('projectid', params['projectid']))  # noqa: E501
            collection_formats['projectid'] = 'csv'  # noqa: E501
        if 'sortby' in params:
            query_params.append(('sortby', params['sortby']))  # noqa: E501
        if 'offset' in params:
            query_params.append(('offset', params['offset']))  # noqa: E501
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501
        if 'sortdir' in params:
            query_params.append(('sortdir', params['sortdir']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # # HTTP header `Accept`
        # header_params['Accept'] = self.api_client.select_header_accept(
        #     ['application/json'])  # noqa: E501
        #
        # # HTTP header `Content-Type`
        # header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
        #     ['application/json'])  # noqa: E501

        # AttributeError: 'APIClient' object has no attribute 'select_header_accept'
        # YF - I comment code above to this:
        header_params['Accept'] = 'application/json'
        header_params['Content-Type'] = 'application/json'

        resourcePath = '/biosamples'
        method = 'GET'

        # Authentication setting
        #auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.callAPI(resourcePath, method, query_params, None, header_params)
        # return self.api_client.call_api(
        #     '/biosamples', 'GET',
        #     path_params,
        #     query_params,
        #     header_params,
        #     body=body_params,
        #     post_params=form_params,
        #     files=local_var_files,
        #     response_type='V2BiologicalSampleCompactList',  # noqa: E501
        #     auth_settings=auth_settings,
        #     async_req=params.get('async_req'),
        #     _return_http_data_only=params.get('_return_http_data_only'),
        #     _preload_content=params.get('_preload_content', True),
        #     _request_timeout=params.get('_request_timeout'),
        #     collection_formats=collection_formats)

    def get_v2_biosamples_biosampleid_labrequeues(self, biosampleid, **kwargs):  # noqa: E501
        """Get a list of a biosample’s lab requeues  # noqa: E501

        All lab requeues, from each of the types, are listed here. A pool lab requeue will show up on the list of lab requeues for all biosamples that make up the pool.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_biosampleid_labrequeues(biosampleid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str biosampleid: Biosample ID (required)
        :param str type: Specify which type of lab requeue to be listed e.g. NewBioSampleLibrary, AdditionalYieldOfLibraryPool, or AdditionalYieldOfFinishedLibrary.
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2LabRequeueCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_biosampleid_labrequeues_with_http_info(biosampleid, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_biosampleid_labrequeues_with_http_info(biosampleid, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_biosampleid_labrequeues_with_http_info(self, biosampleid, **kwargs):  # noqa: E501
        """Get a list of a biosample’s lab requeues  # noqa: E501

        All lab requeues, from each of the types, are listed here. A pool lab requeue will show up on the list of lab requeues for all biosamples that make up the pool.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_biosampleid_labrequeues_with_http_info(biosampleid, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str biosampleid: Biosample ID (required)
        :param str type: Specify which type of lab requeue to be listed e.g. NewBioSampleLibrary, AdditionalYieldOfLibraryPool, or AdditionalYieldOfFinishedLibrary.
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2LabRequeueCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['biosampleid', 'type', 'sortby', 'offset', 'limit', 'sortdir']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_biosampleid_labrequeues" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'biosampleid' is set
        if self.api_client.client_side_validation and ('biosampleid' not in params or
                                                       params['biosampleid'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `biosampleid` when calling `get_v2_biosamples_biosampleid_labrequeues`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'biosampleid' in params:
            path_params['biosampleid'] = params['biosampleid']  # noqa: E501

        query_params = []
        if 'type' in params:
            query_params.append(('type', params['type']))  # noqa: E501
        if 'sortby' in params:
            query_params.append(('sortby', params['sortby']))  # noqa: E501
        if 'offset' in params:
            query_params.append(('offset', params['offset']))  # noqa: E501
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501
        if 'sortdir' in params:
            query_params.append(('sortdir', params['sortdir']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.call_api(
            '/biosamples/{biosampleid}/labrequeues', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2LabRequeueCompactList',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_v2_biosamples_id(self, id, **kwargs):  # noqa: E501
        """Get information about a biosample  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param list[str] include: Sub elements to include in the response
        :return: V2BiologicalSample
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_id_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_id_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_id_with_http_info(self, id, **kwargs):  # noqa: E501
        """Get information about a biosample  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param list[str] include: Sub elements to include in the response
        :return: V2BiologicalSample
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'include']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `get_v2_biosamples_id`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []
        if 'include' in params:
            query_params.append(('include', params['include']))  # noqa: E501
            collection_formats['include'] = 'csv'  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.call_api(
            '/biosamples/{id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2BiologicalSample',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_v2_biosamples_id_libraries(self, id, **kwargs):  # noqa: E501
        """Get a list of a biosample’s libraries  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_libraries(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param list[str] include: Sub elements to include in the response: LibraryIndex, YieldInformation
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2LibraryCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_id_libraries_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_id_libraries_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_id_libraries_with_http_info(self, id, **kwargs):  # noqa: E501
        """Get a list of a biosample’s libraries  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_libraries_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param list[str] include: Sub elements to include in the response: LibraryIndex, YieldInformation
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2LibraryCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'include', 'sortby', 'offset', 'limit', 'sortdir']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_id_libraries" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `get_v2_biosamples_id_libraries`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []
        if 'include' in params:
            query_params.append(('include', params['include']))  # noqa: E501
            collection_formats['include'] = 'csv'  # noqa: E501
        if 'sortby' in params:
            query_params.append(('sortby', params['sortby']))  # noqa: E501
        if 'offset' in params:
            query_params.append(('offset', params['offset']))  # noqa: E501
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501
        if 'sortdir' in params:
            query_params.append(('sortdir', params['sortdir']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.call_api(
            '/biosamples/{id}/libraries', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2LibraryCompactList',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_v2_biosamples_id_runlanesummaries(self, id, **kwargs):  # noqa: E501
        """Get information about biosample’s lane mapping  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_runlanesummaries(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2RunLaneSummaryList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_id_runlanesummaries_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_id_runlanesummaries_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_id_runlanesummaries_with_http_info(self, id, **kwargs):  # noqa: E501
        """Get information about biosample’s lane mapping  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_runlanesummaries_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2RunLaneSummaryList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'sortby', 'offset', 'limit', 'sortdir']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_id_runlanesummaries" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `get_v2_biosamples_id_runlanesummaries`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []
        if 'sortby' in params:
            query_params.append(('sortby', params['sortby']))  # noqa: E501
        if 'offset' in params:
            query_params.append(('offset', params['offset']))  # noqa: E501
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501
        if 'sortdir' in params:
            query_params.append(('sortdir', params['sortdir']))  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.call_api(
            '/biosamples/{id}/runlanesummaries', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2RunLaneSummaryList',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_v2_biosamples_bulkupdate(self, **kwargs):  # noqa: E501
        """Update the default project of many biosamples  # noqa: E501

        Setting a new default project of a biosample will redirect newly created datasets to the new project.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_v2_biosamples_bulkupdate(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param V2PostBioSamplesBulkUpdateRequest payload:
        :return: IBiologicalSampleCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.post_v2_biosamples_bulkupdate_with_http_info(**kwargs)  # noqa: E501
        else:
            (data) = self.post_v2_biosamples_bulkupdate_with_http_info(**kwargs)  # noqa: E501
            return data

    def post_v2_biosamples_bulkupdate_with_http_info(self, **kwargs):  # noqa: E501
        """Update the default project of many biosamples  # noqa: E501

        Setting a new default project of a biosample will redirect newly created datasets to the new project.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_v2_biosamples_bulkupdate_with_http_info(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param V2PostBioSamplesBulkUpdateRequest payload:
        :return: IBiologicalSampleCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['payload']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_v2_biosamples_bulkupdate" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'payload' in params:
            body_params = params['payload']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.call_api(
            '/biosamples/bulkupdate', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='IBiologicalSampleCompactList',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def post_v2_biosamples_id(self, id, **kwargs):  # noqa: E501
        """Update a Biosample  # noqa: E501

        Setting a new default project of a biosample will redirect newly created datasets to the new project. The biosample status may transition between any of the possible statuses. Setting a biosample to canceled will automatically cancel all analyses in progress for that biosample.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_v2_biosamples_id(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param V2UpdateBiologicalSampleRequest payload:
        :return: V2BiologicalSample
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.post_v2_biosamples_id_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.post_v2_biosamples_id_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def post_v2_biosamples_id_with_http_info(self, id, **kwargs):  # noqa: E501
        """Update a Biosample  # noqa: E501

        Setting a new default project of a biosample will redirect newly created datasets to the new project. The biosample status may transition between any of the possible statuses. Setting a biosample to canceled will automatically cancel all analyses in progress for that biosample.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.post_v2_biosamples_id_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: Biosample ID (required)
        :param V2UpdateBiologicalSampleRequest payload:
        :return: V2BiologicalSample
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'payload']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_v2_biosamples_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `post_v2_biosamples_id`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'payload' in params:
            body_params = params['payload']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = ['api_key', 'basespace_auth']  # noqa: E501

        return self.api_client.call_api(
            '/biosamples/{id}', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2BiologicalSample',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)


if __name__ == '__main__':
    api_client = APIClient(AccessToken='xx', apiServerAndVersion='https://api.basespace.illumina.com/v2')
    api = BiosamplesApi(api_client)
    bio_samples_list = api.get_v2_biosamples()
    print(bio_samples_list)
