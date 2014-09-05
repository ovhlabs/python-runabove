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

"""RunAbove SSH key service library."""
from __future__ import absolute_import

from .base import Resource, BaseManagerWithList


class SSHKeyManager(BaseManagerWithList):
    """Manage the SSH keys attached to an account."""

    basepath = '/ssh'

    def get_by_name(self, region, name):
        """Get one SSH key from a RunAbove account.

        :param region: Region where the key is
        :param name: Name of the key to retrieve
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        url = self.basepath + '/' + self._api.encode_for_api(name)
        key = self._api.get(url, {'region': region_name})
        return self._dict_to_obj(key)

    def _dict_to_obj(self, key):
        """Converts a dict to an SSHKey object."""
        region = self._handler.regions._name_to_obj(key['region'])
        return SSHKey(self,
                      key['name'],
                      key.get('fingerPrint'),
                      key.get('publicKey'),
                      region)

    def create(self, region, name, public_key):
        """Register a new SSH key in a RunAbove account.

        :param region: Region where the key will be added
        :param name: Name of the key
        :param public_key: Public key value
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        content = {
            'publicKey': public_key,
            'region': region_name,
            'name': name
        }
        self._api.post(self.basepath, content)
        return self.get_by_name(region_name, name)

    def delete(self, region, key):
        """Delete an SSH key from an account.

        :param region: Region where the key is
        :param key: SSH key to be deleted
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        try:
            name = key.name
        except AttributeError:
            name = key
        url = self.basepath + '/' + self._api.encode_for_api(name)
        return self._api.delete(url, {'region': region_name})


class SSHKey(Resource):
    """Represents one SSH key."""

    def __init__(self, manager, name, finger_print, public_key, region):
        self._manager = manager
        self.name = name
        self.finger_print = finger_print
        self.public_key = public_key
        self.region = region

    def delete(self):
        """Delete the key from the account."""
        self._manager.delete(self.region, self)
