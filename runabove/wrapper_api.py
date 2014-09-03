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

"""
This module provides a simple python wrapper over the RunAbove API
It handles requesting credential, signing queries...
"""
from __future__ import absolute_import

import requests
import hashlib
import time
import json

try:
    from urllib import quote as urllib_quote
except ImportError:  # Python 3
    from urllib.parse import quote as urllib_quote

from .exception import APIError, ResourceNotFoundError, BadParametersError, \
    ResourceAlreadyExistsError, NetworkError


class WrapperApi:
    """Simple wrapper class for RunAbove API."""

    base_url = "https://api.runabove.com/1.0"

    def __init__(self, application_key, application_secret, consumer_key=None):
        """Construct a new wrapper instance.

        :param application_key: your application key given by RunAbove
        on application registration
        :param application_secret: your application secret given by RunAbove
        on application registration
        :param consumer_key: the consumer key you want to use, if any,
        given after a credential request
        """
        self.application_key = application_key
        self.application_secret = application_secret
        self.consumer_key = consumer_key
        self._time_delta = None

    def time_delta(self):
        """Get the delta between this computer and RunAbove cluster."""
        if self._time_delta is None:
            try:
                server_time = int(requests.get(self.base_url + "/time").text)
            except ValueError:
                raise APIError(msg='Impossible to get time from RunAbove')
            self._time_delta = server_time - int(time.time())
        return self._time_delta

    def request_credentials(self, access_rules, redirect_url=None):
        """Request a Consumer Key to the API.

        That key will need to be validated with the link
        returned in the answer.

        :param access_rules: list of dictionaries listing the
         accesses your application will need. Each dictionary
         must contain two keys : method, of the four HTTP methods,
         and path, the path you will need access for,
         with * as a wildcard
        :param redirect_url: url where you want the user to be
         redirected to after he successfully validates
         the consumer key

        :raises APIError: Error send by api
        """
        target_url = self.base_url + "/auth/credential"
        params = {"accessRules": access_rules}
        params["redirection"] = redirect_url
        query_data = json.dumps(params)
        q = requests.post(
            target_url,
            headers={
                "X-Ra-Application": self.application_key,
                "Content-type": "application/json"
            },
            data=query_data)
        res = json.loads(q.text)
        if q.status_code < 100 or q.status_code >= 300:
            raise APIError(res['message'])
        self.consumer_key = str(res['consumerKey'])
        return res

    def raw_call(self, method, path, content=None):
        """Sign a given query and return its result.

        :param method: the HTTP method of the request (get/post/put/delete)
        :param path: the url you want to request
        :param content: the object you want to send in your request
         (will be automatically serialized to JSON)

        :raises APIError: Error send by api
        """
        target_url = self.base_url + path
        now = str(int(time.time()) + self.time_delta())

        body = ""
        if content:
            body = json.dumps(content)

        if not self.consumer_key:
            raise BadParametersError(msg='Cannot call API without'
                                         'Consumer Key')

        s1 = hashlib.sha1()
        s1.update(
            "+".join([
                self.application_secret,
                self.consumer_key,
                method.upper(),
                target_url,
                body,
                now
            ]).encode())
        sig = "$1$" + s1.hexdigest()
        query_headers = {
            "X-Ra-Application": self.application_key,
            "X-Ra-Timestamp": now,
            "X-Ra-Consumer": self.consumer_key,
            "X-Ra-Signature": sig,
            "Content-type": "application/json"
        }
        req = getattr(requests, method.lower())
        result = req(target_url, headers=query_headers, data=body)

        if result.text:
            try:
                json_result = json.loads(result.text)
            except ValueError:
                raise APIError('API response is not valid')
        else:
            json_result = {}

        if result.status_code == 404:
            raise ResourceNotFoundError(msg=json_result.get('message'))
        if result.status_code == 400:
            raise BadParametersError(msg=json_result.get('message'))
        if result.status_code == 409:
            raise ResourceAlreadyExistsError(msg=json_result.get('message'))
        if result.status_code == 0:
            raise NetworkError()
        if result.status_code < 100 or result.status_code >= 300:
            raise APIError(msg=json_result.get('message'))

        return json_result

    def encode_for_api(self, string_to_encode):
        """Make sure the URI in correctly encoded.

        Runabove api need to encode "/" to %2F because slash
        are used into URI to distinct two ressources.

        :param string_to_encode: original string_to_encode
        """
        return urllib_quote(string_to_encode).replace('/', '%2f')

    def get(self, path, content=None):
        """Helper method that wraps a GET call to raw_call.

        :param path: path ask inside api
        :param content: object content to send with this request

        :raises APIError: Error send by api
        """
        return self.raw_call("get", path, content)

    def put(self, path, content):
        """Helper method that wraps a PUT call to raw_call.

        :param path: path ask inside api
        :param content: object content to send with this request

        :raises APIError: Error send by api
        """
        return self.raw_call("put", path, content)

    def post(self, path, content):
        """Helper method that wraps a POST call to raw_call.

        :param path: path ask inside api
        :param content: object content to send with this request

        :raises APIError: Error send by api
        """
        return self.raw_call("post", path, content)

    def delete(self, path, content=None):
        """Helper method that wraps a DELETE call to raw_call.

        :param path: path ask inside api
        :param content: object content to send with this request

        :raises APIError: Error send by api
        """
        return self.raw_call("delete", path, content)
