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

class TestRegion(unittest.TestCase):

    answer_list = '["BHS-1", "SBG-1"]'

    @mock.patch('runabove.wrapper_api')
    @mock.patch('runabove.client')
    def setUp(self, mock_wrapper, mock_client):
        self.mock_wrapper = mock_wrapper
        self.regions = runabove.region.RegionManager(mock_wrapper, mock_client)

    def test_base_path(self):
        self.assertEquals(self.regions.basepath, '/region')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        region_list = self.regions.list()
        self.mock_wrapper.get.assert_called_once_with(self.regions.basepath)
        self.assertIsInstance(region_list, list)
        self.assertTrue(len(region_list) > 0)
        for region in region_list:
            self.assertIsInstance(region, runabove.region.Region)

    def test_get_by_name(self):
        region_name = 'SBG-1'
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        region = self.regions.get_by_name(region_name)
        self.mock_wrapper.get.assert_called_once_with(self.regions.basepath)
        self.assertIsInstance(region, runabove.region.Region)
        self.assertEquals(region.name, region_name)

    def test_get_by_name_404(self):
        with self.assertRaises(runabove.exception.ResourceNotFoundError):
            self.regions.get_by_name('RBX-404')

if __name__ == '__main__':
    unittest.main()
