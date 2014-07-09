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

"""RunAbove base class definition library."""


class BaseManager(object):
    """Basic manager type providing common operations.

    Managers interact with a particular type ressource (instances,
    images, etc.) and provide CRUD operations for them.
    """
    def __init__(self, wrapper_api, runabove_handler):
        """Build a manager with reference to the API.

        :param wrapper_api: client of RunAbove API
        :param runabove_handler: reference to RunAbove user interface
        """
        self._api = wrapper_api
        self._handler = runabove_handler

class BaseManagerWithList(BaseManager):
    """Manager with list and list_by_region methods."""

    def list(self):
        """Get a list of objects in an account."""
        objs = []
        for obj in self._api.get(self.basepath):
            objs.append(self._dict_to_obj(obj))
        return objs

    def list_by_region(self, region):
        """Get a list of objects in a region."""
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        content = {'region': region_name}
        objs = []
        for obj in self._api.get(self.basepath, content):
            objs.append(self._dict_to_obj(obj))
        return objs



class Resource(object):
    """Base class for resource (obj, flavor, etc.)."""

