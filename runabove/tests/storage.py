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

import unittest
import json
import mock
import runabove

from sys import version_info

if version_info[0] >= 3:
    unicode = str  # Python 3 str replaces unicode

class TestContainerManager(unittest.TestCase):
    """Test storage using RunAbove API.

    To play with objects we use swiftclient and we trust it's
    tested properly :)
    """

    name  = 'test2'
    region = 'SBG-1'
    answer_list = '''[
        {
            "totalObjects": 5,
            "name": "test",
            "stored": 1024,
            "region": "SBG-1"
        },
        {
            "totalObjects": 0,
            "name": "test2",
            "stored": 0,
            "region": "SBG-1"
        }
    ]'''

    answer_one = '''{
        "totalObjects": 0,
        "name": "test2",
        "stored": 0,
        "region": "SBG-1"
    }'''

    answer_token = '''{
      "token": {
        "catalog": [
          {
            "endpoints": [
              {
                "id": "af64asqa26fda457c0e974f3f",
                "interface": "public",
                "legacy_endpoint_id": "fa56f4as64c9a8f4asdf496",
                "region": "SBG-1",
                "url": "https://network.compute.sbg-1.runabove.io/"
              },
              {
                "id": "5af5d46as48q911zs654fd69fc84",
                "interface": "public",
                "legacy_endpoint_id": "q984fSDFsa4654164asd98f42c",
                "region": "BHS-1",
                "url": "https://network.compute.bhs-1.runabove.io/"
              }
            ],
            "id": "022012d24e3c446948qwef6as135c68j7uy97",
            "type": "network"
          },
          {
            "endpoints": [
              {
                "id": "asf489a4f541q4f985s1f631a89a7ffd",
                "interface": "public",
                "legacy_endpoint_id": "f7a1afas65qfsASDc1456qf6",
                "region": "BHS-1",
                "url": "https://storage.bhs-1.runabove.io/v1/AUTH_fRs614a"
              },
              {
                "id": "aq98465ASDG46543dfag46eg86eg1s32",
                "interface": "public",
                "legacy_endpoint_id": "fAFASd73251aplnxzq9899eb68c7",
                "region": "SBG-1",
                "url": "https://storage.sbg-1.runabove.io/v1/AUTH_4f6sa5df"
              }
            ],
            "id": "3c7237csdfasd45f4615a654dc9awd4f",
            "type": "object-store"
          }
        ],
        "expires_at": "2014-07-05T10:40:02.799784Z",
        "issued_at": "2014-07-04T10:40:02.799807Z"
      },
      "X-Auth-Token": "mbRArjDDI6fpZQRaxg98USPsz1fuK3Jl17ZHxb"
    }'''

    answer_token_empty = '''{
      "token": {
        "catalog": [],
        "expires_at": "2014-07-05T10:40:02.799784Z",
        "issued_at": "2014-07-04T10:40:02.799807Z"
      },
      "X-Auth-Token": "mbRArjDDI6fpZQRaxg98USPsz1fuK3Jl17ZHxb"
    }'''

    @mock.patch('runabove.wrapper_api')
    @mock.patch('runabove.client')
    def setUp(self, mock_wrapper, mock_client):
        self.mock_wrapper = mock_wrapper
        self.mock_client = mock_client
        self.mock_client.regions = runabove.region.RegionManager(mock_wrapper,
                                                                 mock_client)
        self.containers = runabove.storage.ContainerManager(mock_wrapper,
                                                            mock_client)

    def test_base_path(self):
        self.assertEqual(self.containers.basepath, '/storage')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        container_list = self.containers.list()
        self.mock_wrapper.get.assert_called_once_with(self.containers.basepath)
        self.assertIsInstance(container_list, list)
        self.assertEqual(len(container_list), 2)
        for container in container_list:
            self.assertIsInstance(container, runabove.storage.Container)

    def test_list_by_region(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        container_list = self.containers.list_by_region(self.region)
        self.mock_wrapper.get.assert_called_once_with(
            self.containers.basepath,
            {'region': self.region}
        )
        self.assertIsInstance(container_list, list)
        self.assertEqual(len(container_list), 2)
        for container in container_list:
            self.assertIsInstance(container, runabove.storage.Container)
            self.assertIsInstance(container.region, runabove.region.Region)
            self.assertEqual(container.region.name, self.region)

    @mock.patch('swiftclient.client.Connection')
    def test_get_swift_client(self, mock_swiftclient):
        mock_get_token = self.containers._handler.tokens.get
        mock_get_token.return_value.auth_token = 'token'
        mock_get_token.return_value.endpoint = 'http://url'

        swift = self.containers._get_swift_client('REGION-1')
        mock_get_token.assert_called_once_with()
        mock_get_token.return_value.get_endpoint.assert_called_once_with('object-store', 'REGION-1')
        self.assertIsInstance(swift, dict)
        self.assertEqual(['client', 'endpoint'], sorted(swift.keys()))

    @mock.patch('swiftclient.client.Connection')
    def test_swift_call(self, mock_swiftclient):
        swifts = {
            'BHS-1': {
                'client' : mock_swiftclient,
                'endpoint' : 'http://endpoint'
            }
        }
        self.containers._swifts = swifts
        self.containers._swift_call('BHS-1', 'put_container')

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_get_by_name(self, mock_swift_call):
        container = self.containers.get_by_name(self.region, self.name)
        mock_swift_call.assert_called_once_with(
            self.region,
            'head_container',
            self.name
        )
        self.assertIsInstance(container, runabove.storage.Container)
        self.assertEqual(container.name, self.name)

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_delete(self, mock_swift_call):
        self.containers.delete(self.region, self.name)
        mock_swift_call.assert_called_once_with(
            self.region,
            'delete_container',
            self.name
        )

    @mock.patch('runabove.storage.ContainerManager.get_by_name')
    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_create_public(self, mock_swift_call, mock_get_by_name):
        self.containers.create(self.region, self.name, public=True)
        mock_swift_call.assert_called_once_with(
            self.region,
            'put_container',
            self.name,
            headers={'X-Container-Read': '.r:*,.rlistings'}
        )
        mock_get_by_name.assert_called_once_with(self.region, self.name)

    @mock.patch('runabove.storage.ContainerManager.get_by_name')
    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_create_private(self, mock_swift_call, mock_get_by_name):
        self.containers.create(self.region, self.name)
        mock_swift_call.assert_called_once_with(
            self.region,
            'put_container',
            self.name,
            headers={}
        )
        mock_get_by_name.assert_called_once_with(self.region, self.name)

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_set_public(self, mock_swift_call):
        self.containers.set_public(self.region, self.name)
        mock_swift_call.assert_called_once_with(
            self.region,
            'post_container',
            self.name,
            headers = {'X-Container-Read': '.r:*,.rlistings'}
        )

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_set_public_with_private(self, mock_swift_call):
        self.containers.set_public(self.region, self.name, public=False)
        mock_swift_call.assert_called_once_with(
            self.region,
            'post_container',
            self.name,
            headers = {'X-Container-Read': ''}
        )

    @mock.patch('runabove.storage.ContainerManager.set_public')
    def test_set_private(self, mock_set_public):
        self.containers.set_private(self.region, self.name)
        mock_set_public.assert_called_once_with(
            self.region,
            self.name,
            public=False
        )

    def test_get_region_url(self):
        swifts = {
            'BHS-1': {
                'endpoint' : 'http://endpoint'
            }
        }
        self.containers.swifts = swifts
        url = self.containers.get_region_url('BHS-1')
        self.assertEqual(url, 'http://endpoint')

    def test_get_region_url_not_found(self):
        self.containers._swifts = {}
        with self.assertRaises(runabove.exception.ResourceNotFoundError):
            self.containers.get_region_url('BHS-1')

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_copy_object(self, mock_swift_call):
        self.containers.copy_object(self.region, self.name, 'Test')
        headers = {
            'X-Copy-From': '/' + self.name + '/Test',
            'content-length': 0
        }
        mock_swift_call.assert_called_once_with(
            self.region,
            'put_object',
            self.name,
            'Test',
            None,
            headers=headers
        )

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_copy_object_other_container(self, mock_swift_call):
        self.containers.copy_object(self.region, self.name, 'Test',
                                    to_container='test1')
        headers = {
            'X-Copy-From': '/' + self.name + '/Test',
            'content-length': 0
        }
        mock_swift_call.assert_called_once_with(
            self.region,
            'put_object',
            'test1',
            'Test',
            None,
            headers=headers
        )

    @mock.patch('runabove.storage.ContainerManager._get_swift_client')
    def test_swifts(self, mock_get_swift_client):
        mock_get_swift_client.return_value = {}
        swifts = self.containers.swifts
        mock_get_swift_client.assert_called_once()
        self.assertIsInstance(swifts, dict)


class TestContainer(unittest.TestCase):

    container_name = 'MyTestContainer'

    answer_list = '''[
        [""],
        [
            {
                "name": "obj1",
                "bytes": 20,
                "last_modified": "Thu, 31 Jul 2014 07:57:30 GMT",
                "content_type": "image/png"
            },
            {
                "name": "obj2",
                "bytes": 26,
                "last_modified": "Thu, 31 Jul 2014 07:58:30 GMT",
                "content_type": "image/png"
            }
        ]
    ]'''

    answer_head_object = {
        'content-length': '0',
        'accept-ranges': 'bytes',
        'last-modified': 'Thu, 31 Jul 2014 07:57:30 GMT',
        'connection': 'close',
        'etag': 'd41d8cd99f00b204e9800998ecf8427f',
        'x-timestamp': '1406793450.95376',
        'x-trans-id': 'txbcbed42b0efd46a7aace3-0054da0217',
        'date': 'Thu, 31 Jul 2014 08:45:11 GMT',
        'content-type': 'application/octet-stream'
    }

    answer_get_object = (
        {
            'content-length': '0',
            'accept-ranges': 'bytes',
            'last-modified': 'Thu, 31 Jul 2014 07:57:30 GMT',
            'connection': 'close',
            'etag': 'd41d8cd99f00b204e9800998ecf8427f',
            'x-timestamp': '1406793450.95376',
            'x-trans-id': 'txbcbed42b0efd46a7aace3-0054da0217',
            'date': 'Thu, 31 Jul 2014 08:45:11 GMT',
            'content-type': 'application/octet-stream'
        },
        'data'
    )

    @mock.patch('runabove.region.Region')
    @mock.patch('runabove.storage.ContainerManager')
    def setUp(self, mock_containers, mock_region):
        self.mock_containers = mock_containers
        self.mock_region = mock_region
        self.container = runabove.storage.Container(
            self.mock_containers,
            self.container_name,
            self.mock_region,
            meta=None
        )

    def test_list_objects(self):
        answer = json.loads(self.answer_list)
        self.mock_containers._swift_call.return_value = answer
        object_list = self.container.list_objects()
        self.mock_containers._swift_call.assert_called_once_with(
            self.mock_region.name,
            'get_container',
            self.container_name,
            full_listing=True
        )
        self.assertIsInstance(object_list, list)
        self.assertEqual(len(object_list), 2)
        for obj in object_list:
            self.assertIsInstance(obj, runabove.storage.ObjectStored)

    def _get_object_by_name(self, download=False):
        swift_answer = self.answer_head_object
        call = 'head_object'
        if download:
            swift_answer = self.answer_get_object
            call = 'get_object'
        self.mock_containers._swift_call.return_value = swift_answer
        obj = self.container.get_object_by_name('TestObj', download)
        self.mock_containers._swift_call.assert_called_once_with(
            self.mock_region.name,
            call,
            self.container_name,
            'TestObj'
        )
        self.assertIsInstance(obj, runabove.storage.ObjectStored)
        if download:
            self.assertEqual(obj._data, 'data')
        else:
            self.assertEqual(obj._data, None)

    def test_get_object_by_name_without_download(self):
        self._get_object_by_name()

    def test_get_object_by_name_with_download(self):
        self._get_object_by_name(download=True)

    def test_delete(self):
        self.container.delete()
        self.mock_containers.delete.assert_called_once_with(
            self.mock_region,
            self.container
        )

    def test_delete_object(self):
        self.container.delete_object('Test')
        self.mock_containers._swift_call.assert_called_once_with(
            self.mock_region,
            'delete_object',
            self.container.name,
            'Test'
        )

    @mock.patch('runabove.storage.Container.get_object_by_name')
    def test_create_object(self, mock_get_object_by_name):
        obj = self.container.create_object('Test', 'content')
        self.mock_containers._swift_call.assert_called_once_with(
            self.mock_region.name,
            'put_object',
            self.container.name,
            'Test',
            'content',
            headers=None
        )

    @mock.patch('runabove.storage.ObjectStored')
    def test_copy(self, mock_obj):
        to_container = 'CopyTo'
        new_object_name = 'NewName'
        self.container.copy_object(mock_obj, to_container, new_object_name)
        self.mock_containers.copy_object.assert_called_once_with(
            self.mock_region.name,
            self.container,
            mock_obj,
            to_container,
            new_object_name
        )

    def test_set_public(self):
        self.container.set_public()
        self.mock_containers.set_public.assert_called_once_with(
            self.mock_region.name,
            self.container
        )

    def test_set_private(self):
        self.container.set_private()
        self.mock_containers.set_private.assert_called_once_with(
            self.mock_region.name,
            self.container
        )

    def test_url(self):
        base_url = 'https://url-of-endpoint'
        self.mock_containers.get_region_url.return_value = base_url
        url = self.container.url
        self.mock_containers.get_region_url.assert_called_once_with(
            self.mock_region.name
        )
        self.assertEqual(url, base_url + '/' + self.container_name)

    @mock.patch('runabove.storage.Container')
    def test_get_meta(self, mock_cnt):
        fake_meta = {'X-meta': 'meta'}
        mock_cnt._meta = fake_meta
        self.mock_containers.get_by_name.return_value = mock_cnt
        meta = self.container.meta
        self.mock_containers.get_by_name.assert_called_once_with(
            self.mock_region.name,
            self.container.name,
            list_objects=False
        )
        self.assertEqual(meta, fake_meta)

    def test_set_meta(self):
        fake_meta = {'X-meta': 'meta'}
        self.container.meta = fake_meta


class TestObjectStored(unittest.TestCase):

    obj_name = 'MyTestObject'

    @mock.patch('runabove.storage.Container')
    def setUp(self, mock_container):
        self.mock_container = mock_container
        self.obj = runabove.storage.ObjectStored(
            self.mock_container,
            self.obj_name
        )

    @mock.patch('runabove.storage.ObjectStored')
    def test_data(self, mock_obj):
        fake_data = 'SomeData'
        mock_obj._data = fake_data
        self.mock_container.get_object_by_name.return_value = mock_obj
        data = self.obj.data
        self.mock_container.get_object_by_name.assert_called_once_with(
            self.obj.name,
            download=True
        )
        self.assertEqual(data, fake_data)

    @mock.patch('runabove.storage.ObjectStored')
    def test_get_meta(self, mock_obj):
        fake_meta = {'X-meta': 'meta'}
        mock_obj._meta = fake_meta
        self.mock_container.get_object_by_name.return_value = mock_obj
        meta = self.obj.meta
        self.mock_container.get_object_by_name.assert_called_once_with(
            self.obj.name,
            download=False
        )
        self.assertEqual(meta, fake_meta)

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_set_meta(self, mock_swift_call):
        fake_meta = {'X-meta': 'meta'}
        self.obj.meta = fake_meta

    @mock.patch('runabove.storage.ObjectStored')
    def test_data_already_downloaded(self, mock_obj):
        fake_data = 'SomeData'
        self.obj._data = fake_data
        data = self.obj.data
        self.mock_container.get_object_by_name.assert_not_called()
        self.assertEqual(data, fake_data)

    def test_url(self):
        base_url = 'https://url-of-endpoint/containerName'
        self.mock_container.url = base_url
        url = self.obj.url
        self.assertEqual(url, base_url + '/' + self.obj_name)

    def test_delete(self):
        self.obj.delete()
        self.mock_container.delete_object.assert_called_once_with(
            self.obj
        )

    def test_copy(self):
        to_container = 'CopyTo'
        new_object_name = 'NewName'
        self.obj.copy(to_container, new_object_name)
        self.mock_container.copy_object.assert_called_once_with(
            self.obj,
            to_container,
            new_object_name
        )

if __name__ == '__main__':
    unittest.main()
