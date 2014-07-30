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

class TestRunabove(unittest.TestCase):

    application_key = 'test_apkey'
    application_secret = 'test_apsecret'
    consumer_key = 'test_conkey'
    access_rules = [
        {'method': 'GET', 'path': '/*'},
        {'method': 'POST', 'path': '/*'},
        {'method': 'PUT', 'path': '/*'},
        {'method': 'DELETE', 'path': '/*'}
    ]

    @mock.patch('runabove.wrapper_api')
    def setUp(self, mock_wrapper):
        self.mock_wrapper = mock_wrapper
        self.client = runabove.Runabove(self.application_key,
                                        self.application_secret,
                                        consumer_key=self.consumer_key)
        self.client._api = self.mock_wrapper

    def _get_login_url(self, access_rules=None, redirect_url=None):
        return_value = {"validationUrl": "runabove.com"}
        if not access_rules:
            access_rules = self.access_rules
        self.mock_wrapper.request_credentials.return_value = return_value
        login_url = self.client.get_login_url(access_rules, redirect_url)
        self.mock_wrapper.request_credentials.assert_called_once_with(
            access_rules,
            redirect_url
        )
        self.assertEquals(login_url, return_value['validationUrl'])

    def test_get_login_url(self):
        self._get_login_url()

    def test_get_login_url_with_access_rules(self):
        access_rules = [
            {'method': 'GET', 'path': '/me'}
        ]
        self._get_login_url(access_rules)

    def test_get_login_url_with_redirect(self):
        redirect_url = 'http://app.using.runabove.sdk.com/'
        self._get_login_url(redirect_url=redirect_url)

    def test_get_login_url_with_redirect_and_access_rules(self):
        redirect_url = 'http://app.using.runabove.sdk.com/'
        access_rules = [
            {'method': 'GET', 'path': '/me'}
        ]
        self._get_login_url(access_rules, redirect_url)

    def test_get_consumer_key(self):
        self.mock_wrapper.consumer_key = self.consumer_key
        self.assertEquals(self.client.get_consumer_key(),
                          self.consumer_key)

    def test_existance_of_flavors_manager(self):
        manager = self.client.flavors
        self.assertIsInstance(manager, runabove.flavor.FlavorManager)

    def test_existance_of_regions_manager(self):
        manager = self.client.regions
        self.assertIsInstance(manager, runabove.region.RegionManager)

    def test_existance_of_ssh_keys_manager(self):
        manager = self.client.ssh_keys
        self.assertIsInstance(manager, runabove.ssh_key.SSHKeyManager)

    def test_existance_of_images_manager(self):
        manager = self.client.images
        self.assertIsInstance(manager, runabove.image.ImageManager)

    def test_existance_of_instances_manager(self):
        manager = self.client.instances
        self.assertIsInstance(manager, runabove.instance.InstanceManager)

    def test_existance_of_storage_service(self):
        service = self.client.containers
        self.assertIsInstance(service, runabove.storage.ContainerManager)

if __name__ == '__main__':
    unittest.main()
