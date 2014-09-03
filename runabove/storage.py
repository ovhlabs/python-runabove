# -*- encoding: utf-8 -*-
#
# Copyright (c) 2014, OVH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Except as contained in this notice, the name of OVH and or its trademarks
# (and among others RunAbove) shall not be used in advertising or otherwise to
# promote the sale, use or other dealings in this Software without prior
# written authorization from OVH.

"""RunAbove Object Storage service library."""
from __future__ import absolute_import

import functools
import mimetypes

try:
    from urllib import quote as urllib_quote
except ImportError:  # Python 3
    from urllib.parse import quote as urllib_quote

import swiftclient

from .base import Resource, BaseManagerWithList
from .exception import APIError, ResourceNotFoundError


class ContainerManager(BaseManagerWithList):
    """Manage containers available in RunAbove."""

    basepath = '/storage'
    _swifts = {}

    def get_by_name(self, region, container_name):
        """Get a container by its name.

        As two containers with the same name can exist in two
        different regions we need to limit the search to one region.
        :param container_name: Name of the container to retrieve
        :raises ResourceNotFoundError: Container does not exist
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        content = {'region': region_name}
        url = self.basepath + '/' + self._api.encode_for_api(container_name)
        res = self._api.get(url, content)
        return self._en_dict_to_obj(res, region_name)

    def _dict_to_obj(self, container):
        """Converts a dict to a container object."""
        region = self._handler.regions._name_to_obj(container['region'])
        return Container(self,
                         container['name'],
                         container.get('stored'),
                         container.get('totalObjects'),
                         region)

    def _en_dict_to_obj(self, container, region_name):
        """Converts a dict to a container object."""
        region = self._handler.regions._name_to_obj(region_name)
        return Container(self,
                         container['name'],
                         container.get('stored'),
                         container.get('totalObjects'),
                         region,
                         public=container.get('public'))

    def _get_endpoints(self):
        """Get the OpenStack endpoint for storage in each region."""
        tokens = self._api.get('/token')
        catalog = tokens['token']['catalog']
        for service in catalog:
            if service['type'] != 'object-store':
                continue
            return service['endpoints'], tokens['X-Auth-Token']

        raise ResourceNotFoundError(msg='No Object Storage endpoint')

    def _get_swift_clients(self):
        """Get the swift client for each region."""
        endpoints, token = self._get_endpoints()
        swifts = {}
        for endpoint in endpoints:
            s = swiftclient.client.Connection(preauthurl=endpoint['url'],
                                              preauthtoken=token)
            swifts[endpoint['region']] = {
                    'client': s,
                    'endpoint': endpoint['url']
            }
        return swifts

    def _swift_call(self, region, action, *args, **kwargs):
        """Wrap calls to swiftclient to allow retry."""
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        retries = 0
        while retries < 3:
            swift = self.swifts[region_name]['client']
            call = getattr(swift, action.lower())
            try:
                return call(*args, **kwargs)
            except swiftclient.exceptions.ClientException as e:
                if e.http_status == 401:
                    # Token is invalid, regenerate swift clients
                    self._swifts = None
                if e.http_status == 404:
                    raise ResourceNotFoundError(msg=e.msg)
                else:
                   raise e
        raise APIError(msg='Impossible to get a valid token')

    def create(self, region, container_name, public=False):
        """Create a new container in a region.

        :param region: Region where the container will be created
        :param container_name: Name of the container to create
        :param public: Make the containers public if True
        """
        if public:
            headers = {'X-Container-Read': '.r:*,.rlistings'}
        else:
            headers = {}
        self._swift_call(region, 'put_container',
                         container_name, headers=headers)
        return self.get_by_name(region, container_name)

    def delete(self, region, container):
        """Delete a container.

        :param region: Region where the container will be deleted
        :param container: Container to delete
        """
        try:
            container_name = container.name
        except AttributeError:
            container_name = container
        self._swift_call(region, 'delete_container', container_name)

    def set_public(self, region, container, public=True):
        """Set a container publicly available.

        :param region: Region where the container is
        :param container: Container to make public
        :param public: Set container private if False
        """
        try:
            container_name = container.name
        except AttributeError:
            container_name = container
        if public:
            headers = {'X-Container-Read': '.r:*,.rlistings'}
        else:
            headers = {'X-Container-Read': ''}
        self._swift_call(region, 'post_container',
                         container_name, headers=headers)

    def set_private(self, region, container):
        """Set a container to private.

        :param region: Region where the container is
        :param container: Container to make private
        """
        self.set_public(region, container, public=False)

    def get_region_url(self, region):
        """Get the URL endpoint for storage in a region.

        :param region: Region to get the endpoint for
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        try:
            return self.swifts[region_name]['endpoint']
        except KeyError:
            raise ResourceNotFoundError(msg='Region does not exist')

    def copy_object(self, region, from_container, stored_object,
                    to_container=None, new_object_name=None):
        """Copy an object from a container to another one.

        Containers must be in the same region. Both containers may be
        the same. Content-Type is read from the original object if
        available, otherwise it is guessed with file name, defaults to
        None if impossible to guess.

        :param region: Region where the containers are
        :param from_container: Container where the original object is
        :param stored_object: Object to copy
        :param to_container: Container where the object will be copied
            to. If None copy into the same container.
        :param new_object_name: Name of the new object. If None new name
            is taken from the original name.
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        try:
            from_container_name = from_container.name
        except AttributeError:
            from_container_name = from_container
        try:
            stored_object_name = stored_object.name
            content_type = stored_object.content_type
        except AttributeError:
            stored_object_name = stored_object
            content_type = mimetypes.guess_type(stored_object_name)[0]
        if to_container:
            try:
                to_container_name = to_container.name
            except AttributeError:
                to_container_name = to_container
        else:
            to_container_name = from_container_name
        if not new_object_name:
            new_object_name = stored_object_name
        original_location = '/%s/%s'%(from_container_name, stored_object_name)
        headers = {'X-Copy-From': original_location}
        self._swift_call(region_name,
                         'put_object',
                         to_container_name,
                         new_object_name,
                         None,
                         headers=headers,
                         content_length=0,
                         content_type=content_type)

    @property
    def swifts(self):
        """Lazy load of one swift client per region."""
        if not self._swifts:
            self._swifts = self._get_swift_clients()
        return self._swifts

class Container(Resource):
    """Represents one container."""

    def __init__(self, manager, name, size,
                 number_objects, region, public=None):
        self._manager = manager
        self.name = name
        self.size = size
        self.number_objects = number_objects
        self.region = region
        self._is_public = public

    @property
    def is_public(self):
        """Lazy loading of public state."""
        if self._is_public is None:
            self._is_public = self._manager.\
                get_by_name(self.region.name, self.name)._is_public
        return self._is_public

    def delete(self):
        """Delete the container."""
        self._manager.delete(self.region, self)

    def _dict_to_obj(self, obj):
        """Converts a dict to a ObjectStored object."""
        return ObjectStored(self,
                            obj.get('name'),
                            obj.get('bytes'),
                            obj.get('last_modified'),
                            obj.get('content_type'))

    def _en_dict_to_obj(self, name, info, data=None):
        """Converts a dict to a ObjectStored object."""
        return ObjectStored(self,
                            name,
                            info.get('content-length'),
                            info.get('last-modified'),
                            info.get('content-type'),
                            data=data)

    def list_objects(self):
        """List objects of a container."""
        res = self._manager._swift_call(self.region.name,
                                        'get_container',
                                        self.name,
                                        full_listing=True)
        objs = []
        for obj in res[1]:
            objs.append(self._dict_to_obj(obj))
        return objs

    def get_object_by_name(self, object_name, download=False):
        """Get an object stored by its name.

        Does not download the content of the object by default.
        :param object_name: Name of the object to create
        :param download: If True download also the object content
        """
        if download:
            call = 'get_object'
        else :
            call = 'head_object'
        res = self._manager._swift_call(self.region.name,
                                        call,
                                        self.name,
                                        object_name)

        try:
            return self._en_dict_to_obj(object_name, res[0], data=res[1])
        except KeyError:
            return self._en_dict_to_obj(object_name, res)

    def delete_object(self, object_stored):
        """Delete an object from a container.

        :param object_stored: the object to delete
        """
        try:
            object_name = object_stored.name
        except AttributeError:
            object_name = object_stored
        self._manager._swift_call(self.region,
                                  'delete_object',
                                  self.name,
                                  object_name)

    def create_object(self, object_name, content, content_type=None):
        """Upload an object to a container.

        :param object_name: Name of the object to create
        :param content: Content to upload, can be a string or a file-like
            object
        :param content_type: Content-type of the object, if None it will be
            computed with the extension of object name
        """
        if not content_type:
            content_type = mimetypes.guess_type(object_name)[0]
        self._manager._swift_call(self.region.name,
                                  'put_object',
                                  self.name,
                                  object_name,
                                  content,
                                  content_type=content_type)
        return self.get_object_by_name(object_name)

    def copy_object(self, stored_object, to_container=None,
                    new_object_name=None):
        """Copy an object from a container to another one.

        Containers must be in the same region. Both containers may be
        the same. Content-Type is read from the original object if
        available, otherwise it is guessed with file name, defaults to
        None if impossible to guess.

        :param stored_object: Object to copy
        :param to_container: Container where the object will be copied
            to. If None copy into the same container.
        :param new_object_name: Name of the new object. If None new name
            is taken from the original name.
        """
        self._manager.copy_object(self.region.name, self, stored_object,
                                  to_container, new_object_name)

    def set_public(self):
        """Set the container public."""
        self._manager.set_public(self.region.name, self)

    def set_private(self):
        """Set the container private."""
        self._manager.set_private(self.region.name, self)

    @property
    def url(self):
        """Get the URL to access a container."""
        region_endpoint = self._manager.get_region_url(self.region.name)
        container_name = urllib_quote(self.name).replace('/', '%2f')
        return '%s/%s' % (region_endpoint, container_name)


class ObjectStored(Resource):
    """Represents one swift object."""

    def __init__(self, container, name, size, last_modified,
                 content_type, data=None):
        self.container = container
        self.name = name
        self.size = size
        self.last_modified = last_modified
        self.content_type = content_type
        self._data = data

    @property
    def data(self):
        """Lazy loading of content of an object."""
        if not self._data:
            self._data  = self.container.get_object_by_name(
                    self.name,
                    download=True
                )._data
        return self._data

    @property
    def url(self):
        """Get the URL of an object."""
        object_name = urllib_quote(self.name)
        return '%s/%s' % (self.container.url, object_name)

    def delete(self):
        """Delete the object."""
        self.container.delete_object(self)

    def copy(self, to_container=None, new_object_name=None):
        """Copy an object from a container to another one.

        Containers must be in the same region. Both containers may be
        the same. Content-Type is read from the original object if
        available, otherwise it is guessed with file name, defaults to
        None if impossible to guess.

        :param to_container: Container where the object will be copied
            to. If None copy into the same container.
        :param new_object_name: Name of the new object. If None new name
            is taken from the original name.
        """
        self.container.copy_object(self, to_container, new_object_name)
