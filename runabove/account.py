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

"""RunAbove account service library."""
from __future__ import absolute_import

from .base import Resource, BaseManager
from .exception import ResourceNotFoundError


class AccountManager(BaseManager):
    """Manage the account attached to the user."""

    basepath = '/me'

    def get(self):
        """Get information about an account."""
        res = self._api.get(self.basepath)
        return self._dict_to_obj(res)

    def _load_balance(self):
        """Loads information about balance.

        Sums total of all projects, so no usage per project.
        """
        balance = self._api.get(self.basepath + '/balance')
        total_usage = 0
        for project in balance['currentUsages']:
            total_usage += project['currentTotal']
        return (total_usage, balance['creditLeft'])

    def _dict_to_obj(self, key):
        """Converts a dict to an Account object."""
        return Account(self,
                       key.get('accountIdentifier'),
                       key.get('firstname'),
                       key.get('name'),
                       key.get('address'),
                       key.get('city'),
                       key.get('postalCode'),
                       key.get('area'),
                       key.get('country'),
                       key.get('email'),
                       key.get('cellNumber'))


class Account(Resource):
    """Represents one account."""

    def __init__(self, manager, account_id, first_name, last_name, address,
                 city, postal_code, area, country, email, phone):
        self._manager = manager
        self.account_id = account_id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.city = city
        self.postal_code = postal_code
        self.area = area
        self.country = country
        self.email = email
        self.phone = phone
        self._current_total = None
        self._credit_left = None

    @property
    def current_total(self):
        """Lazy loading of balance information."""
        if not self._current_total:
            self._current_total = self._manager._load_balance()[0]
            self._credit_left = self._manager._load_balance()[1]
        return self._current_total

    @property
    def credit_left(self):
        """Lazy loading of balance information."""
        if not self._credit_left:
            self._current_total = self._manager._load_balance()[0]
            self._credit_left = self._manager._load_balance()[1]
        return self._credit_left
