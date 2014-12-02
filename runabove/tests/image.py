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


class TestImage(unittest.TestCase):

    answer_list = '''[
        {
            "id": "fedora",
            "name": "Fedora 20",
            "region": "BHS-1",
            "visibility": "public"
        },
        {
            "id": "centos",
            "name": "CentOS 6",
            "region": "BHS-1",
            "visibility": "private"
        }
    ]'''

    answer_one = '''{
        "id": "Pfdq813FxcFel78954aFEfcpaW21",
        "name": "ra-snapshot",
        "status": "active",
        "creationDate": "2014-04-15T12:10:05Z",
        "minDisk": 240,
        "minRam": 0,
        "visibility": "private",
        "region": "BHS-1"
    }'''

    @mock.patch('runabove.wrapper_api')
    @mock.patch('runabove.client')
    def setUp(self, mock_wrapper, mock_client):
        self.mock_wrapper = mock_wrapper
        self.mock_client = mock_client
        self.mock_client.regions = runabove.region.RegionManager(mock_wrapper,
                                                                 mock_client)
        self.images = runabove.image.ImageManager(mock_wrapper, mock_client)

    def test_base_path(self):
        self.assertEqual(self.images.basepath, '/image')

    def test_list(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        image_list = self.images.list()
        self.mock_wrapper.get.assert_called_once_with(self.images.basepath)
        self.assertIsInstance(image_list, list)
        self.assertEqual(len(image_list), 2)
        for image in image_list:
            self.assertIsInstance(image, runabove.image.Image)

    def test_list_by_region(self):
        region_name = 'BHS-1'
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        image_list = self.images.list_by_region(region_name)
        self.mock_wrapper.get.assert_called_once_with(
            self.images.basepath,
            {'region': region_name}
        )
        self.assertIsInstance(image_list, list)
        self.assertEqual(len(image_list), 2)
        for image in image_list:
            self.assertIsInstance(image, runabove.image.Image)
            self.assertEqual(image.region.name, 'BHS-1')

    def test_get_by_name(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        f = self.images.get_by_name('Fedora 20')
        self.assertEquals(1, len(f))
        self.assertIsInstance(f[0], runabove.image.Image)

    def test_get_by_name_404(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_list)
        f = self.images.get_by_name('non-existent-image')
        self.assertEquals([], f)

    def test_find_by_image_id(self):
        the_id = "Pfdq813FxcFel78954aFEfcpaW21"
        self.mock_wrapper.get.return_value = json.loads(self.answer_one)
        image = self.images.get_by_id(the_id)
        self.mock_wrapper.get.assert_called_once_with(
            self.images.basepath + '/' +\
                self.images._api.encode_for_api(the_id)
        )
        self.assertIsInstance(image, runabove.image.Image)
        self.assertEqual(image.id, the_id)

if __name__ == '__main__':
    unittest.main()
