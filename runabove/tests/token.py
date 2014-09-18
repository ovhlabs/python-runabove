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
import mock
import json

import runabove


class TestToken(unittest.TestCase):

    answer_token = '''{
      "token": {
        "catalog": [
          {
            "endpoints": [
              {
                "id": "randomendpointid1",
                "interface": "public",
                "legacy_endpoint_id": "randomlegacyid1",
                "region": "BHS-1",
                "url": "https://storage.bhs-1.runabove.io/v1/AUTH_randomprojectid"
              },
              {
                "id": "randomendpointid2",
                "interface": "public",
                "legacy_endpoint_id": "randomlegacyid2",
                "region": "SBG-1",
                "url": "https://storage.sbg-1.runabove.io/v1/AUTH_randomprojectid"
              }
            ],
            "id": "3c7237cfff4f44b7b3dbd951a49d1bec",
            "type": "object-store"
          }
        ],
        "expires_at": "2014-08-09T18:32:34.39985Z",
        "issued_at": "2014-08-08T18:32:34.399875Z",
        "methods": [
          "manager"
        ],
        "project": {
          "domain": {
            "name": "Default"
          },
          "id": "randomprojectid",
          "name": "27081924"
        },
        "roles": [
          {
            "id": "randomroleid",
            "name": "_member_"
          }
        ],
        "user": {
          "domain": {
            "name": "Default"
          },
          "name": "test@runabove.com",
          "password": "",
          "id": "randomuserid"
        }
      },
      "X-Auth-Token": "63c1sMWB1o92Vm0A-Oa82aoltuHcAtpcEvLEFOW4UBlNlSI="
    }'''

    @mock.patch('runabove.wrapper_api')
    def setUp(self, mock_wrapper):
        self.mock_wrapper = mock_wrapper
        self.token = runabove.token.TokenManager(mock_wrapper, None)

    def test_base_path(self):
        self.assertEquals(self.token.basepath, '/token')

    def test_token_existance(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_token)
        token = self.token.get()
        self.assertIsInstance(token, runabove.token.Token)

class TestTokenObject(unittest.TestCase):

    @mock.patch('runabove.token.TokenManager')
    def setUp(self, mock_tokens):
        self.mock_tokens = mock_tokens
        mock_token = json.loads(TestToken.answer_token)
        self.token = runabove.token.Token(
            self.mock_tokens,
            mock_token['X-Auth-Token'],
            mock_token['token']['user'],
            mock_token['token']['project'],
            mock_token['token']['catalog'],
            mock_token['token']['methods'],
            mock_token['token']['roles'],
            mock_token['token']['issued_at'],
            mock_token['token']['expires_at'],
        )

    def test_init(self):
        mock_token = json.loads(TestToken.answer_token)
        self.assertEqual(mock_token['X-Auth-Token'], self.token.auth_token)
        self.assertEqual(mock_token['token']['user'], self.token.user)
        self.assertEqual(mock_token['token']['roles'], self.token.roles)
        self.assertEqual(mock_token['token']['project'], self.token.project)
        self.assertEqual(mock_token['token']['catalog'], self.token.catalog)
        self.assertEqual(mock_token['token']['methods'], self.token.methods)
        self.assertEqual(mock_token['token']['issued_at'], self.token.issued_at)
        self.assertEqual(mock_token['token']['expires_at'], self.token.expires_at)

    def test_get_endpoint(self):
        mock_token = json.loads(TestToken.answer_token)
        self.assertEqual(
            mock_token['token']['catalog'][0]['endpoints'][1],
            self.token.get_endpoint('object-store', 'SBG-1')
        )

        self.assertRaises(KeyError, self.token.get_endpoint, 'object-store', 'RBX-1')
        self.assertRaises(KeyError, self.token.get_endpoint, 'compute', 'SBG-1')


if __name__ == '__main__':
    unittest.main()
