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

"""RunAbove flavor service library."""
from __future__ import absolute_import

from .base import Resource, BaseManagerWithList
from .exception import ResourceNotFoundError


class FlavorManager(BaseManagerWithList):
    """Manage flavors available in RunAbove."""

    basepath = '/flavor'

    def _dict_to_obj(self, flavor):
        """Converts a dict to a Flavor object."""
        region = self._handler.regions._name_to_obj(flavor['region'])
        return Flavor(self,
                      flavor['id'],
                      flavor.get('disk'),
                      flavor.get('name'),
                      flavor.get('ram'),
                      flavor.get('vcpus'),
                      flavor.get('type'),
                      region)

    def get_by_name(self, flavor_name):
        """Get a list of flavors named ``flavor_name``

        :param flavor_name: name of the flavors to retrieve
        """
        flavors = []
        for flavor in self.list():
            if flavor.name == flavor_name:
                flavors.append(flavor)
        return flavors

    def get_by_id(self, flavor_id):
        """Get a flavor by its id.

        :param flavor_id: ID of the flavor to retrieve
        :raises ResourceNotFoundError: Flavor does not exist
        """
        url = self.basepath + '/' + self._api.encode_for_api(flavor_id)
        flavor = self._api.get(url)
        return self._dict_to_obj(flavor)


class Flavor(Resource):
    """Represents one flavor."""

    def __init__(self, manager, flavor_id, disk,
                 name, ram, vcpus, type, region):
        self._manager = manager
        self.id = flavor_id
        self.disk = disk
        self.name = name
        self.ram = ram
        self.vcpus = vcpus
        self.type = type
        self.region = region
