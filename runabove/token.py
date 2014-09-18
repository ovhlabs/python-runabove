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

"""RunAbove token service library."""
from __future__ import absolute_import

from datetime import datetime

from .base import Resource, BaseManager
from .exception import ResourceNotFoundError


class TokenManager(BaseManager):
    """Manage flavors available in RunAbove."""

    basepath = '/token'

    def get(self):
        """Get an OpenStack API Token."""
        res = self._api.get(self.basepath)
        return self._dict_to_obj(res)

    def _iso8601_to_datetime(self, iso8601):
        """Parse iso8601 formated date into a datetime object

        param: iso8601: iso8601 formated date, ZULU timezone (UTC)
        raises: ValueError: when date is of an incompatible format or not ZULU.
        """
        return datetime.strptime(iso8601, "%Y-%m-%dT%H:%M:%S.%fZ")

    def _dict_to_obj(self, token):
        """Converts a dict to a Token object."""
        return Token(self,
                     token['X-Auth-Token'],
                     token['token']['user'],
                     token['token']['project'],
                     token['token']['catalog'],
                     token['token']['methods'],
                     token['token']['roles'],
                     self._iso8601_to_datetime(token['token']['issued_at']),
                     self._iso8601_to_datetime(token['token']['expires_at']))


class Token(Resource):
    """Represents an OpenStack token."""

    def __init__(self, manager, auth_token, user, project,
                 catalog, methods, roles, issued_at, expires_at):
        """Build a token object. `issued_at` and `expires_at` should be well
        formated `datetime.datetime` instances."""
        self._manager = manager
        self.auth_token = auth_token
        self.user = user
        self.project = project
        self.catalog = catalog
        self.methods = methods
        self.roles = roles
        self.issued_at = issued_at
        self.expires_at = expires_at

    def get_endpoint(self, endpoint_type, region_name):
        """Find and return corresponding endpoint from `self.catalog`

        param: endpoint_type: endpoint type (identity, compute, network, ...)
        param: region_name: name of the region
        raises: KeyError: when not matching endpoint is found
        """
        for entry in self.catalog:
            if entry['type'] != endpoint_type:
                continue
            for endpoint in entry['endpoints']:
                if endpoint['region'] == region_name:
                    return endpoint

        raise KeyError("No endpoint matching type=%s, region=%s found" %
                       (endpoint_type, region_name))

