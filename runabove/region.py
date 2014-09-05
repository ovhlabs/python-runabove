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

"""RunAbove region service library."""
from __future__ import absolute_import

from .base import Resource, BaseManager
from .exception import ResourceNotFoundError


class RegionManager(BaseManager):
    """Manage regions available in RunAbove."""

    basepath = '/region'

    def list(self):
        """Get list of regions available."""

        res = self._api.get(self.basepath)
        regions = []
        for region_name in res:
            regions.append(Region(self, region_name))
        return regions

    def _name_to_obj(self, region_name):
        """Makes a region object by a name.

        It does not check if the region actually exists.
        """
        return Region(self, region_name)

    def get_by_name(self, region_name):
        """Get a region by its name.

        :param region_name: Name of the region to retrieve
        :raises ResourceNotFoundError: Region does not exist
        """
        regions = self.list()
        for region in regions:
            if region.name == region_name:
                return region
        raise ResourceNotFoundError(msg='Region %s does not exist'
                                        % region_name)


class Region(Resource):
    """Represents one region."""

    def __init__(self, manager, name):
        self._manager = manager
        self.name = name
