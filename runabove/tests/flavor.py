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

class TestFlavor(unittest.TestCase):

    answer_list = '''[
        {
            "id": "4245b91e-d9cf-4c9d-a109-f6a32da8a5cc",
            "disk": 200,
            "name": "pci2.d.r1",
            "ram": 28672,
            "vcpus": 4,
            "region": "BHS-1",
            "type": "ra.d"
        },
        {
            "id": "ab35df0e-4632-48b2-b6a5-c1f1d922bd43",
            "disk": 240,
            "name": "pci2.d.c1",
            "ram": 16384,
            "vcpus": 6,
            "region": "BHS-1",
            "type": "ra.d"
        }
    ]'''

    answer_one = '''{
        "id": "4245b91e-d9cf-4c9d-a109-f6a32da8a5cc",
        "disk": 200,
        "name": "ra.intel.ssd.xl2",
        "ram": 28672,
        "vcpus": 4,
        "region": "BHS-1",
        "type": ""
    }'''

    @mock.patch('runabove.wrapper_api')
    @mock.patch('runabove.client')
    def setUp(self, mock_wrapper, mock_client):
        self.mock_wrapper = mock_wrapper
        self.flavors = runabove.flavor.FlavorManager(mock_wrapper, mock_client)

    def test_base_path(self):
        self.assertEqual(self.flavors.basepath, '/flavor')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        flavor_list = self.flavors.list()
        self.mock_wrapper.get.assert_called_once_with(self.flavors.basepath)
        for flavor in flavor_list:
            self.assertIsInstance(flavor, runabove.flavor.Flavor)

    def test_list_by_region(self):
        region_name = 'BHS-1'
        content = {'region': region_name}
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        flavor_list = self.flavors.list_by_region(region_name)
        self.mock_wrapper.get.assert_called_once_with(
            self.flavors.basepath,
            content
        )
        for flavor in flavor_list:
            self.assertIsInstance(flavor, runabove.flavor.Flavor)

    def test_get_by_name(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        f = self.flavors.get_by_name('pci2.d.r1')
        self.assertEquals(1, len(f))
        self.assertIsInstance(f[0], runabove.flavor.Flavor)

    def test_get_by_name_404(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        f = self.flavors.get_by_name('non-existent-flavor')
        self.assertEquals([], f)

    def test_get_by_id(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_one)
        f = self.flavors.get_by_id('4245b91e-d9cf-4c9d-a109-f6a32da8a5cc')
        self.assertIsInstance(f, runabove.flavor.Flavor)

if __name__ == '__main__':
    unittest.main()
