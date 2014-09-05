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

"""RunAbove image service library."""
from __future__ import absolute_import

from .base import Resource, BaseManagerWithList


class ImageManager(BaseManagerWithList):
    """Manage images available in RunAbove."""

    basepath = '/image'

    def get_by_id(self, image_id=None):
        """Get one image from a RunAbove account.

        :param image_id: ID of the image to retrieve
        """
        url = self.basepath + '/' + self._api.encode_for_api(image_id)
        image = self._api.get(url)
        return self._dict_to_obj(image)

    def _dict_to_obj(self, key):
        """Converts a dict to an image object."""
        region = self._handler.regions._name_to_obj(key['region'])
        return Image(self,
                     key['id'],
                     key.get('name'),
                     region=region)


class Image(Resource):
    """Represents one image."""

    def __init__(self, manager, id, name, region):
        self._manager = manager
        self.id = id
        self.name = name
        self.region = region

