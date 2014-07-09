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
        self.assertEquals(self.containers.basepath, '/storage')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        container_list = self.containers.list()
        self.mock_wrapper.get.assert_called_once_with(self.containers.basepath)
        self.assertIsInstance(container_list, list)
        self.assertEquals(len(container_list), 2)
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
        self.assertEquals(len(container_list), 2)
        for container in container_list:
            self.assertIsInstance(container, runabove.storage.Container)
            self.assertIsInstance(container.region, runabove.region.Region)
            self.assertEquals(container.region.name, self.region)

    def test_get_by_name(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_one)
        container = self.containers.get_by_name(self.region, self.name)
        self.mock_wrapper.get.assert_called_once_with(
            self.containers.basepath + '/' +
            self.containers._api.encode_for_api(self.name),
            {'region': self.region}
        )
        self.assertIsInstance(container, runabove.storage.Container)
        self.assertEquals(container.name, self.name)

    def test_get_endpoint(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_token)
        result = self.containers._get_endpoints()
        self.mock_wrapper.get.assert_called_once_with('/token')
        self.assertIsInstance(result, tuple)
        self.assertEquals(len(result), 2)
        for endpoint in result[0]:
            self.assertIsInstance(endpoint, dict)
            self.assertIsInstance(endpoint['url'], unicode)
            self.assertIsInstance(endpoint['region'], unicode)

    def test_get_endpoint_without_object_storage(self):
        self.mock_wrapper.get.return_value = json.loads(
            self.answer_token_empty
        )
        with self.assertRaises(runabove.exception.ResourceNotFoundError):
            result = self.containers._get_endpoints()
            self.mock_wrapper.get.assert_called_once_with('/token')

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

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_copy_object(self, mock_swift_call):
        self.containers.copy_object(self.region, self.name, 'Test')
        mock_swift_call.assert_called_once_with(
            self.region,
            'put_object',
            self.name,
            'Test',
            None,
            headers = {'X-Copy-From': '/' + self.name + '/Test'},
            content_length=0,
            content_type=None
        )

    @mock.patch('runabove.storage.ContainerManager._swift_call')
    def test_copy_object_other_container(self, mock_swift_call):
        self.containers.copy_object(self.region, self.name, 'Test',
                                    to_container='test1')
        mock_swift_call.assert_called_once_with(
            self.region,
            'put_object',
            'test1',
            'Test',
            None,
            headers = {'X-Copy-From': '/' + self.name + '/Test'},
            content_length=0,
            content_type=None
        )

    @mock.patch('runabove.storage.ContainerManager._get_swift_clients')
    def test_swifts(self, mock_get_swift_clients):
        mock_get_swift_clients.return_value = []
        swifts = self.containers.swifts
        mock_get_swift_clients.assert_called_once()
        self.assertIsInstance(swifts, list)


class TestContainer(unittest.TestCase):

    @mock.patch('runabove.storage.ContainerManager')
    def setUp(self, mock_containers):
        self.mock_containers = mock_containers
        self.container = runabove.storage.Container(
            self.mock_containers,
            'MyTestContainer',
            1024,
            5,
            'BHS-1'
        )

    def test_delete(self):
        self.container.delete()
        self.mock_containers.delete.assert_called_once_with(
            'BHS-1',
            self.container
        )

    def test_delete_object(self):
        self.container.delete_object('Test')
        self.mock_containers._swift_call.assert_called_once_with(
            'BHS-1',
            'delete_object',
            self.container.name,
            'Test'
        )


if __name__ == '__main__':
    unittest.main()
