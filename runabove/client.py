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

"""RunAbove SDK interface for users."""
from __future__ import absolute_import

from .wrapper_api import WrapperApi
from .flavor import FlavorManager
from .region import RegionManager
from .ssh_key import SSHKeyManager
from .image import ImageManager
from .instance import InstanceManager
from .storage import ContainerManager
from .account import AccountManager


class Runabove(object):
    """SDK interface to get cloud services from RunAbove."""

    access_rules = [
        {'method': 'GET', 'path': '/*'},
        {'method': 'POST', 'path': '/*'},
        {'method': 'PUT', 'path': '/*'},
        {'method': 'DELETE', 'path': '/*'}
    ]

    def __init__(self, application_key, application_secret, consumer_key=None):
        """Create the main interface of the SDK.

        :param application_key: key of your RunAbove api's application
        :param application_secret: password of your RunAbove api's application
        """
        self._api = WrapperApi(application_key,
                               application_secret,
                               consumer_key)
        self.flavors = FlavorManager(self._api, self)
        self.regions = RegionManager(self._api, self)
        self.ssh_keys = SSHKeyManager(self._api, self)
        self.images = ImageManager(self._api, self)
        self.instances = InstanceManager(self._api, self)
        self.account = AccountManager(self._api, self)
        self.containers = ContainerManager(self._api, self)

    def get_login_url(self, access_rules=None, redirect_url=None):
        """Get the URL to identify and login a customer.

        RunAbove API uses a remote connection to avoid storing passwords inside
        third party program. So the authentication is in two steps:
        First the app has to get a login URL and show it to the customer.
        Then, the customer must login with his account using this URL and the
        consumer key will be validated by the API.

        :param access_rules: List of access required by the application
        :param redirect_url: URL where user will be redirected after signin
        :raises ApiException: Error send by api
        """
        if isinstance(access_rules, list):
            self.access_rules = access_rules
        credentials = self._api.request_credentials(self.access_rules,
                                                    redirect_url)
        return credentials['validationUrl']

    def get_consumer_key(self):
        """Get the current consumer key to communicate with the API."""

        return self._api.consumer_key
