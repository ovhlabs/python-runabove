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

import runabove
import unittest
import mock
import json


class TestSshKey(unittest.TestCase):

    answer_list = '''[
        {
            "publicKey": "ssh-rsa very-strong-key1 key-comment",
            "name": "TestKey1",
            "fingerPrint": "aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:a1",
            "region": "BHS-1"
        },
        {
            "publicKey": "ssh-rsa very-strong-key2 key-comment",
            "name": "TestKey2",
            "fingerPrint": "aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:a2",
            "region": "BHS-1"
        }
    ]'''

    answer_one  = '''{
        "publicKey": "ssh-rsa very-strong-key1 key-comment",
        "name": "TestKey1",
        "fingerPrint": "aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:a1",
        "region": "BHS-1"
    }'''

    @mock.patch('runabove.wrapper_api')
    @mock.patch('runabove.client')
    def setUp(self, mock_wrapper, mock_client):
        self.mock_wrapper = mock_wrapper
        self.mock_client = mock_client
        self.mock_client.regions = runabove.region.RegionManager(mock_wrapper,
                                                                 mock_client)
        self.ssh_keys = runabove.ssh_key.SSHKeyManager(mock_wrapper,
                                                       mock_client)

    def test_base_path(self):
        self.assertEqual(self.ssh_keys.basepath, '/ssh')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        ssh_key_list = self.ssh_keys.list()
        self.mock_wrapper.get.assert_called_once_with(
            self.ssh_keys.basepath
        )
        self.assertIsInstance(ssh_key_list, list)
        self.assertTrue(len(ssh_key_list) > 0)

    def test_list_by_region(self):
        region_name = 'BHS-1'
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        ssh_key_list = self.ssh_keys.list_by_region(region_name)
        self.mock_wrapper.get.assert_called_once_with(
            self.ssh_keys.basepath,
            {'region': region_name}
        )
        self.assertIsInstance(ssh_key_list, list)
        self.assertTrue(len(ssh_key_list) > 0)
        for ssh_key in ssh_key_list:
            self.assertIsInstance(ssh_key, runabove.ssh_key.SSHKey)
            self.assertEqual(ssh_key.region.name, region_name)

    def test_get_by_name(self):
        region_name = 'BHS-1'
        name = "TestKey1"
        self.mock_wrapper.encode_for_api.return_value = name
        self.mock_wrapper.get.return_value = json.loads(self.answer_one)
        ssh_key = self.ssh_keys.get_by_name(region_name, name)
        self.mock_wrapper.get.assert_called_once_with(
            self.ssh_keys.basepath + '/' + name,
            {'region': region_name}
        )
        self.assertEqual(ssh_key.name, name)

    def test_create_ssh_key(self):
        region_name = 'BHS-1'
        name = "TestKey1"
        public_key = "ssh-rsa very-strong-key1 key-comment"
        content = {
            "name": name,
            "publicKey": public_key,
            "region": region_name
        }
        self.mock_wrapper.get.return_value = json.loads(self.answer_one)
        self.ssh_keys.create(region_name, name, public_key)
        self.mock_wrapper.post.assert_called_once_with(
            self.ssh_keys.basepath, content
        )

    def test_delete(self):
        region_name = 'BHS-1'
        name = "TestKey1"
        self.mock_wrapper.encode_for_api.return_value = name
        self.ssh_keys.delete(region_name, name)
        self.mock_wrapper.delete.assert_called_once_with(
            self.ssh_keys.basepath + '/' + name,
            {'region': region_name}
        )


class TestSSHKeyObject(unittest.TestCase):

    @mock.patch('runabove.ssh_key.SSHKeyManager')
    def setUp(self, mock_ssh_keys):
        self.mock_ssh_keys = mock_ssh_keys
        self.ssh_key = runabove.ssh_key.SSHKey(
            self.mock_ssh_keys,
            'MyTestKey',
            'aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa:aa',
            'ssh-rsa very-strong-key key-comment',
            'BHS-1'
        )

    def test_delete_object(self):
        self.ssh_key.delete()
        self.mock_ssh_keys.delete.assert_called_once_with(
            self.ssh_key.region,
            self.ssh_key
        )

if __name__ == '__main__':
    unittest.main()
