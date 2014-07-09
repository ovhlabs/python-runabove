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
import mock
import json

import runabove


class TestInstance(unittest.TestCase):

    instance_id = '8c687d5d-a1c7-4670-aca8-65acfb23ab44'
    answer_list = '''[
        {
            "instanceId": "8c687d5d-a1c7-4670-aca8-65acfb23ab44",
            "name": "Test1",
            "ip": "192.168.0.1",
            "flavorId": "ab35df0e-4632-48b2-b6a5-c1f1d922bd43",
            "imageId": "82a56d09-882d-48cc-82ce-eef59820879f",
            "keyName": "",
            "status": "ACTIVE",
            "created": "2014-06-01T09:13:15Z",
            "region": "BHS-1"
        },
        {
            "instanceId": "6736e98e-d40c-408d-8198-8a20d21124f3",
            "name": "Test2",
            "ip": "192.168.0.1",
            "flavorId": "ab35df0e-4632-48b2-b6a5-c1f1d922bd43",
            "imageId": "6915107b-e40d-4fd7-95f5-5e2bd5c106d3",
            "keyName": "MyTestKey",
            "status": "ACTIVE",
            "created": "2014-06-20T10:10:38Z",
            "region": "BHS-1"
        }
    ]'''

    answer_one = '''{
        "instanceId": "8c687d5d-a1c7-4670-aca8-65acfb23ab44",
        "name": "Test",
        "ipv4": "192.168.0.3",
        "created": "2014-06-01T09:13:15Z",
        "status": "ACTIVE",
        "flavor": {
            "id": "ab35df0e-4632-48b2-b6a5-c1f1d922bd43",
            "disk": 240,
            "name": "pci2.d.c1",
            "ram": 16384,
            "vcpus": 6,
            "region": "BHS-1"
        },
        "image": {
            "id": "82a56d09-882d-48cc-82ce-eef59820879f",
            "name": "Debian 7",
            "region": "BHS-1"
        },
        "sshKey": null,
        "region": "BHS-1"
    }'''

    answer_create_with_key = '''{
        "instanceId": "8c687d5d-a1c7-4670-aca8-65acfb23ab44",
        "name": "Test",
        "ipv4": "",
        "created": "2014-07-02T14:02:39Z",
        "status": "BUILD",
        "flavor": {
            "id": "4245b91e-d9cf-4c9d-a109-f6a32da8a5cc",
            "disk": 240,
            "name": "pci2.d.r1",
            "ram": 28672,
            "vcpus": 4,
            "region": "BHS-1"
        },
        "image": {
            "id": "82a56d09-882d-48cc-82ce-eef59820879f",
            "name": "Debian 7",
            "region": "BHS-1"
        },
        "sshKey": {
            "publicKey": "ssh-rsa very-strong-key key-comment",
            "name": "MyTestKey",
            "fingerPrint": "aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa",
            "region": "BHS-1"
        },
        "region": "BHS-1"
    }'''

    answer_create_without_key = '''{
        "instanceId": "8c687d5d-a1c7-4670-aca8-65acfb23ab44",
        "name": "Test",
        "ipv4": "",
        "created": "2014-07-02T14:02:39Z",
        "status": "BUILD",
        "flavor": {
            "id": "4245b91e-d9cf-4c9d-a109-f6a32da8a5cc",
            "disk": 240,
            "name": "pci2.d.r1",
            "ram": 28672,
            "vcpus": 4,
            "region": "BHS-1"
        },
        "image": {
            "id": "82a56d09-882d-48cc-82ce-eef59820879f",
            "name": "Debian 7",
            "region": "BHS-1"
        },
        "sshKey": null,
        "region": "BHS-1"
    }'''

    @mock.patch('runabove.wrapper_api')
    @mock.patch('runabove.client')
    def setUp(self, mock_wrapper, mock_client):
        self.mock_wrapper = mock_wrapper
        self.instances = runabove.instance.InstanceManager(mock_wrapper,
                                                           mock_client)

    def test_base_path(self):
        self.assertEquals(self.instances.basepath, '/instance')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        instance_list = self.instances.list()
        self.mock_wrapper.get.assert_called_once_with(
            self.instances.basepath
        )
        self.assertIsInstance(instance_list, list)
        self.assertTrue(len(instance_list) > 0)

    def test_get_by_id(self):
        self.mock_wrapper.encode_for_api.return_value = self.instance_id
        self.mock_wrapper.get.return_value = json.loads(self.answer_one)
        instance = self.instances.get_by_id(self.instance_id)
        self.mock_wrapper.get.assert_called_once_with(
            self.instances.basepath + '/' + self.instance_id
        )
        self.assertIsInstance(instance, runabove.instance.Instance)

    def test_create_with_key(self):
        name = "Test"
        image_id = "82a56d09-882d-48cc-82ce-eef59820879f"
        flavor_id = "4245b91e-d9cf-4c9d-a109-f6a32da8a5cc"
        region_name = "BHS-1"
        public_key = "ssh-rsa very-strong-key key-comment"
        content = {
            'flavorId': flavor_id,
            'imageId': image_id,
            'name': name,
            'region': region_name,
            'sshKeyName': public_key
        }
        self.mock_wrapper.post.return_value = json.loads(
            self.answer_create_with_key
        )
        self.mock_wrapper.get.return_value = json.loads(
            self.answer_create_with_key
        )
        self.mock_wrapper.encode_for_api.return_value = self.instance_id
        instance = self.instances.create(
            region_name,
            name,
            flavor_id,
            image_id,
            public_key
        )
        self.mock_wrapper.post.assert_called_once_with(
            self.instances.basepath,
            content
        )
        self.mock_wrapper.get.assert_called_once_with(
            self.instances.basepath + '/' + self.instance_id
        )

    def test_create_without_key(self):
        name = "Test"
        image_id = "82a56d09-882d-48cc-82ce-eef59820879f"
        flavor_id = "4245b91e-d9cf-4c9d-a109-f6a32da8a5cc"
        region_name = "BHS-1"
        content = {
            'flavorId': flavor_id,
            'imageId': image_id,
            'name': name,
            'region': region_name
        }
        self.mock_wrapper.post.return_value = json.loads(
            self.answer_create_without_key
        )
        self.mock_wrapper.get.return_value = json.loads(
            self.answer_create_without_key
        )
        self.mock_wrapper.encode_for_api.return_value = self.instance_id
        self.instances.create(
            region_name,
            name,
            flavor_id,
            image_id
        )
        self.mock_wrapper.post.assert_called_once_with(
            self.instances.basepath,
            content
        )
        self.mock_wrapper.get.assert_called_once_with(
            self.instances.basepath + '/' + self.instance_id
        )

    def test_rename_vm(self):
        name = 'MyTestInstanceWithNewName'
        self.mock_wrapper.encode_for_api.return_value = self.instance_id
        content = {"name": name}
        self.instances.rename(self.instance_id, name)
        self.mock_wrapper.put.assert_called_once_with(
            self.instances.basepath + '/' + self.instance_id,
            content
        )

    def test_delete(self):
        self.mock_wrapper.encode_for_api.return_value = self.instance_id
        self.instances.delete(self.instance_id)
        self.mock_wrapper.delete.assert_called_once_with(
            self.instances.basepath + '/' + self.instance_id
        )

    def test_load_vnc(self):
        url = "https://vnc-url"
        self.mock_wrapper.get.return_value = json.loads('''{
            "type": "novnc",
            "url": "%s"
        }''' % url)
        vnc = self.instances._load_vnc(self.instance_id)
        self.mock_wrapper.get.assert_called_once_with(
            self.instances.basepath + '/' + self.instance_id + '/vnc'
        )
        self.assertEquals(vnc, url)

class TestInstanceObject(unittest.TestCase):

    @mock.patch('runabove.instance.InstanceManager')
    def setUp(self, mock_instances):
        self.mock_instances = mock_instances
        self.instance = runabove.instance.Instance(
            self.mock_instances,
            '9c687d5d-a1c7-4670-aca8-65acfb23ab44',
            'MyTestInstance',
            '192.168.0.1',
            'BHS-1',
            'fc4c428d-c88b-4027-b35d-2ca176a8bd1a',
            'b37437ea-e8de-474b-9628-54f563a3fd1e',
            'MyTestKey',
            'ACTIVE',
            '2014-07-01T09:13:15Z'
        )

    def test_delete_object(self):
        self.instance.delete()
        self.mock_instances.delete.assert_called_once_with(self.instance)

    def test_rename_object(self):
        name = 'MyTestInstanceWithNewName'
        self.instance.rename(name)
        self.mock_instances.rename.assert_called_once_with(self.instance, name)

    def test_get_vnc_link(self):
        self.instance.vnc
        self.mock_instances.vnc.assert_called_once()

    def test_get_flavor(self):
        self.instance.flavor
        self.mock_instances._handler.flavors.get_by_id.assert_called_once_with(
            self.instance._flavor_id
        )

    def test_get_image(self):
        self.instance.image
        self.mock_instances._handler.images.get_by_id.assert_called_once_with(
            self.instance._image_id
        )

    def test_get_ssh_key(self):
        self.instance.ssh_key
        self.mock_instances._handler.ssh_keys.get_by_name.\
        assert_called_once_with(
                self.instance.region,
                self.instance._ssh_key_name
        )

    def test_get_ssh_key_empty(self):
        self.instance._ssh_key_name = None
        self.assertEquals(self.instance.ssh_key, None)

    def test_get_ips(self):
        self.instance.ips
        self.mock_instances.get_by_id.assert_called_once_with(
            self.instance.id
        )


if __name__ == '__main__':
    unittest.main()
