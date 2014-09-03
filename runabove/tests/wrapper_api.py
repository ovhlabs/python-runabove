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

import unittest
import time
import json
import hashlib

import mock
from mock import patch
import httpretty
from httpretty import register_uri, GET, POST, DELETE, PUT

from runabove.wrapper_api import WrapperApi
from runabove.exception import APIError, BadParametersError,\
                               ResourceNotFoundError, NetworkError,\
                               ResourceAlreadyExistsError

class TestWrapperApi(unittest.TestCase):

    application_key = 'GpG8f61qtOcWmb0e'
    application_secret = 'fE42V43gAB5dpqURV8RPNq9U5rU1J8er'
    consumer_key = 'pW4Xn9s8MDpwfGD8s2DXpoXp3ESkCSY'
    base_url = 'https://api.runabove.com/1.0'
    fake_time = 1404395889.467238

    def setUp(self):
        self.time_patch = patch('time.time', return_value=self.fake_time)
        self.time_patch.start()
        httpretty.enable()
        self.api = WrapperApi(self.application_key,
                              self.application_secret,
                              self.consumer_key)
        self.api._time_delta = 0
        self.actual_base_url = WrapperApi.base_url

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()
        self.time_patch.stop()

    def test_constructor(self):
        self.assertEquals(self.api.application_key, self.application_key)
        self.assertEquals(self.api.consumer_key, self.consumer_key)
        self.assertEquals(self.api.application_secret, self.application_secret)

    def test_base_url(self):
        self.assertEquals(self.api.base_url, self.base_url)

    def test_time_delta(self):
        self.api._time_delta = None
        fake_server_time = '1404395895'
        register_uri(
            GET,
            self.actual_base_url + '/time',
            body=fake_server_time
        )
        time_delta = self.api.time_delta()
        self.assertEquals(time_delta, 6)
        self.assertEquals(self.api._time_delta, 6)

    def test_time_delta_with_bad_answer(self):
        self.api._time_delta = None
        fake_server_time = 'NotAnUTCTimestamp'
        register_uri(
            GET,
            self.actual_base_url + '/time',
            body=fake_server_time
        )
        with self.assertRaises(APIError):
            self.api.time_delta()

    def _request_credentials(self, redirection=None, status=200):
        access_rules = [{'method': 'GET', 'path': '/storage'}]
        response = {
            'validationUrl': 'https://api.runabove.com/login/qdfwb',
            'consumerKey': '63C4VMs4MDpwfGDj4KQEnTjbkvjSJCSY',
            'state': 'pendingTest'
        }
        if not status == 200:
            response = {'message': 'Error'}
        register_uri(
            POST,
            self.actual_base_url + '/auth/credential',
            content_type='application/json',
            status=status,
            body=json.dumps(response)
        )
        res = self.api.request_credentials(access_rules, redirection)
        self.assertEquals(self.api.consumer_key, response['consumerKey'])
        self.assertEquals(
            httpretty.last_request().headers['content-type'],
            'application/json'
        )
        self.assertEquals(
            httpretty.last_request().headers['X-Ra-Application'],
            self.application_key
        )
        self.assertEquals(
            httpretty.last_request().parsed_body['redirection'],
            redirection
        )
        self.assertEquals(
            httpretty.last_request().parsed_body['accessRules'],
            access_rules
        )

    def test_request_credentials_without_redirection(self):
        self._request_credentials()

    def test_request_credentials_with_redirection(self):
        self._request_credentials(redirection='http://test.net')

    def test_request_credentials_with_error(self):
        with self.assertRaises(APIError):
            self._request_credentials(status=500)

    def _raw_call(self, path='/test', method='get', content='',
                  status=200, response=None):
        select_method = {
            'get': GET,
            'post': POST,
            'delete' : DELETE,
            'put': PUT
        }
        if not status == 200:
            response = {'message': 'Error'}
        body = ''
        if content:
            body = json.dumps(content)
        register_uri(
            select_method[method],
            self.actual_base_url + path,
            content_type='application/json',
            status=status,
            body=json.dumps(response)
        )
        s1 = hashlib.sha1()
        s1.update(
            "+".join([
                self.application_secret,
                self.consumer_key,
                method.upper(),
                self.base_url + path,
                body,
                '1404395889'
            ]).encode())
        sig = "$1$" + s1.hexdigest()
        result = self.api.raw_call(method, path, content)
        self.assertEquals(
            httpretty.last_request().method,
            method.upper()
        )
        self.assertEquals(
            httpretty.last_request().headers['content-type'],
            'application/json'
        )
        self.assertEquals(
            httpretty.last_request().headers['X-Ra-Application'],
            self.application_key
        )
        self.assertEquals(
            httpretty.last_request().headers['X-Ra-Consumer'],
            self.consumer_key
        )
        self.assertEquals(
            httpretty.last_request().headers['X-Ra-Timestamp'],
            '1404395889'
        )
        self.assertEquals(
            httpretty.last_request().headers['X-Ra-Signature'],
            sig
        )
        self.assertEquals(result, response)
        if content:
            self.assertEquals(
                httpretty.last_request().parsed_body,
                content
            )

    def test_raw_call_without_consumer_key(self):
        self.api.consumer_key = None
        with self.assertRaises(BadParametersError):
            self._raw_call()

    def test_raw_call_with_error_404(self):
        with self.assertRaises(ResourceNotFoundError):
            self._raw_call(status=404)

    def test_raw_call_with_error_400(self):
        with self.assertRaises(BadParametersError):
            self._raw_call(status=400)

    def test_raw_call_with_error_409(self):
        with self.assertRaises(ResourceAlreadyExistsError):
            self._raw_call(status=409)

    def test_raw_call_with_error_500(self):
        with self.assertRaises(APIError):
            self._raw_call(status=500)

    def test_raw_call_get(self):
        self._raw_call()

    def test_raw_call_get_with_content(self):
        self._raw_call(content='{"test": 1}')

    def test_raw_call_get_with_response(self):
        self._raw_call(response='{"test": 1}')

    def test_raw_call_put(self):
        self._raw_call(method='put')

    def test_raw_call_put_with_content(self):
        self._raw_call(method='put', content='{"test": 1}')

    def test_raw_call_put_with_response(self):
        self._raw_call(method='put', response='{"test": 1}')

    def test_raw_call_post(self):
        self._raw_call(method='post')

    def test_raw_call_post_with_content(self):
        self._raw_call(method='post', content='{"test": 1}')

    def test_raw_call_post_with_response(self):
        self._raw_call(method='post', response='{"test": 1}')

    def test_raw_call_delete(self):
        self._raw_call(method='delete')

    def test_raw_call_delete_with_content(self):
        self._raw_call(method='delete', content='{"test": 1}')

    def test_raw_call_delete_with_response(self):
        self._raw_call(method='delete', response='{"test": 1}')

    def test_raw_call_with_invalid_answer(self):
        path = '/test'
        register_uri(
            GET,
            self.actual_base_url + path,
            content_type='application/json',
            body='Not A Valid "JSON" answer from API'
        )
        with self.assertRaises(APIError):
            self.api.raw_call('get', path)

    def _external_call(self, method):
        patcher = mock.patch('runabove.wrapper_api.WrapperApi.raw_call')
        self.api.raw_call = patcher.start()
        select_method = {
            'get': self.api.get,
            'post': self.api.post,
            'delete' : self.api.delete,
            'put': self.api.put
        }
        select_method[method]('/test', None)
        self.api.raw_call.assert_called_once_with(
            method,
            '/test',
            None
        )
        patcher.stop()

    def test_get(self):
        self._external_call('get')

    def test_post(self):
        self._external_call('post')

    def test_delete(self):
        self._external_call('delete')

    def test_put(self):
        self._external_call('put')

    def test_encode_for_api_without_modification(self):
        string = 'StringThatDoesNotNeedModification'
        result = self.api.encode_for_api(string)
        self.assertEquals(result, string)

    def test_encode_for_api_with_modification(self):
        string = 'String/That/Needs/Modification'
        expected = 'String%2fThat%2fNeeds%2fModification'
        result = self.api.encode_for_api(string)
        self.assertEquals(result, expected)

if __name__ == '__main__':
    unittest.main()
