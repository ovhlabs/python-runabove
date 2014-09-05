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

class TestAccount(unittest.TestCase):

    answer_account = '''{
        "email": "test@runabove.com",
        "accountIdentifier": "test@runabove.com",
        "firstname": "Test",
        "country": "US",
        "city": null,
        "area": null,
        "cellNumber": "+99.999999999",
        "name": "Test",
        "address": null,
        "postalCode": null
    }'''

    answer_balance = '''{
        "currentUsages": [
            {
                "projectId": "randomlongstring",
                "currentTotal": 192.39
            },
            {
                "projectId": "randomlongstring2",
                "currentTotal": 1
            }
        ],
        "creditLeft": 200
    }'''

    @mock.patch('runabove.wrapper_api')
    def setUp(self, mock_wrapper):
        self.mock_wrapper = mock_wrapper
        self.account = runabove.account.AccountManager(mock_wrapper, None)

    def test_base_path(self):
        self.assertEqual(self.account.basepath, '/me')

    def test_account_existance(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_account)
        account = self.account.get()
        self.assertIsInstance(account, runabove.account.Account)

    def test_load_balance(self):
        self.mock_wrapper.get.return_value = json.loads(self.answer_balance)
        balance = self.account._load_balance()
        self.assertIsInstance(balance, tuple)
        self.assertTrue(len(balance) == 2)
        self.assertEqual(balance[0], 193.39)
        self.assertEqual(balance[1], 200)


class TestAccountObject(unittest.TestCase):

    @mock.patch('runabove.account.AccountManager')
    def setUp(self, mock_accounts):
        self.mock_accounts = mock_accounts
        self.account = runabove.account.Account(
            self.mock_accounts,
            'test@runabove.com',
            'Test',
            'Test',
            None,
            None,
            None,
            None,
            'US',
            'test@runabove.com',
            '+99.999999999'
        )

    def test_current_total(self):
        self.mock_accounts._load_balance.return_value = (193.39, 200)
        self.assertEqual(self.account.current_total, 193.39)
        self.mock_accounts._load_balance.assert_called_once()

    def test_credit_left(self):
        self.mock_accounts._load_balance.return_value = (193.39, 200)
        self.assertEqual(self.account.credit_left, 200)
        self.mock_accounts._load_balance.assert_called_once()

if __name__ == '__main__':
    unittest.main()
