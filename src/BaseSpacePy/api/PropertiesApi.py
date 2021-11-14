from __future__ import absolute_import

import re  # noqa: F401
import six
from BaseSpacePy.api.APIClient import APIClient


class PropertiesApi(object):
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = APIClient()
        self.api_client = api_client

    def get_v2_biosamples_id_properties(self, id, **kwargs):  # noqa: E501
        """get_v2_biosamples_id_properties  # noqa: E501

        List properties for a resource  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_properties(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param int propertieslimit: Limit the # of properties returned
        :param int propertyitemslimit: Limit the # of property items returned per property
        :param list[str] propertyfilters: Filter by property name
        :param str showhiddenitems: Show Hidden projects and Datasets
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2PropertyCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_id_properties_with_http_info(id, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_id_properties_with_http_info(id, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_id_properties_with_http_info(self, id, **kwargs):  # noqa: E501
        """get_v2_biosamples_id_properties  # noqa: E501

        List properties for a resource  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_properties_with_http_info(id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param int propertieslimit: Limit the # of properties returned
        :param int propertyitemslimit: Limit the # of property items returned per property
        :param list[str] propertyfilters: Filter by property name
        :param str showhiddenitems: Show Hidden projects and Datasets
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2PropertyCompactList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'propertieslimit', 'propertyitemslimit', 'propertyfilters', 'showhiddenitems', 'sortby', 'offset', 'limit', 'sortdir']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_id_properties" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `get_v2_biosamples_id_properties`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []
        if 'propertieslimit' in params:
            query_params.append(('propertieslimit', params['propertieslimit']))  # noqa: E501
        if 'propertyitemslimit' in params:
            query_params.append(('propertyitemslimit', params['propertyitemslimit']))  # noqa: E501
        if 'propertyfilters' in params:
            query_params.append(('propertyfilters', params['propertyfilters']))  # noqa: E501
            collection_formats['propertyfilters'] = 'csv'  # noqa: E501
        if 'showhiddenitems' in params:
            query_params.append(('showhiddenitems', params['showhiddenitems']))  # noqa: E501
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
            '/biosamples/{id}/properties', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2PropertyCompactList',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_v2_biosamples_id_properties_name(self, id, name, **kwargs):  # noqa: E501
        """get_v2_biosamples_id_properties_name  # noqa: E501

        Get property information  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_properties_name(id, name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param str name: Property name (required)
        :param int propertyitemslimit: Limit the # of property items returned per property
        :param str showhiddenitems: Hidden filter
        :return: V2Property
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_id_properties_name_with_http_info(id, name, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_id_properties_name_with_http_info(id, name, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_id_properties_name_with_http_info(self, id, name, **kwargs):  # noqa: E501
        """get_v2_biosamples_id_properties_name  # noqa: E501

        Get property information  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_properties_name_with_http_info(id, name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param str name: Property name (required)
        :param int propertyitemslimit: Limit the # of property items returned per property
        :param str showhiddenitems: Hidden filter
        :return: V2Property
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'name', 'propertyitemslimit', 'showhiddenitems']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_id_properties_name" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `get_v2_biosamples_id_properties_name`")  # noqa: E501
        # verify the required parameter 'name' is set
        if self.api_client.client_side_validation and ('name' not in params or
                                                       params['name'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `name` when calling `get_v2_biosamples_id_properties_name`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501
        if 'name' in params:
            path_params['name'] = params['name']  # noqa: E501

        query_params = []
        if 'propertyitemslimit' in params:
            query_params.append(('propertyitemslimit', params['propertyitemslimit']))  # noqa: E501
        if 'showhiddenitems' in params:
            query_params.append(('showhiddenitems', params['showhiddenitems']))  # noqa: E501

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
            '/biosamples/{id}/properties/{name}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2Property',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def get_v2_biosamples_id_properties_name_items(self, id, name, **kwargs):  # noqa: E501
        """get_v2_biosamples_id_properties_name_items  # noqa: E501

        Get property item details  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_properties_name_items(id, name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param str name: Property name (required)
        :param str showhiddenitems: Hidden filter
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2PropertyItemList
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.get_v2_biosamples_id_properties_name_items_with_http_info(id, name, **kwargs)  # noqa: E501
        else:
            (data) = self.get_v2_biosamples_id_properties_name_items_with_http_info(id, name, **kwargs)  # noqa: E501
            return data

    def get_v2_biosamples_id_properties_name_items_with_http_info(self, id, name, **kwargs):  # noqa: E501
        """get_v2_biosamples_id_properties_name_items  # noqa: E501

        Get property item details  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.get_v2_biosamples_id_properties_name_items_with_http_info(id, name, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str id: (required)
        :param str name: Property name (required)
        :param str showhiddenitems: Hidden filter
        :param str sortby: The field(s) used to sort the result set
        :param int offset: The starting offset to read
        :param int limit: The maximum number of items to return
        :param str sortdir: The sort direction for the result set
        :return: V2PropertyItemList
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'name', 'showhiddenitems', 'sortby', 'offset', 'limit', 'sortdir']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_v2_biosamples_id_properties_name_items" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `get_v2_biosamples_id_properties_name_items`")  # noqa: E501
        # verify the required parameter 'name' is set
        if self.api_client.client_side_validation and ('name' not in params or
                                                       params['name'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `name` when calling `get_v2_biosamples_id_properties_name_items`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501
        if 'name' in params:
            path_params['name'] = params['name']  # noqa: E501

        query_params = []
        if 'showhiddenitems' in params:
            query_params.append(('showhiddenitems', params['showhiddenitems']))  # noqa: E501
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
            '/biosamples/{id}/properties/{name}/items', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V2PropertyItemList',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
