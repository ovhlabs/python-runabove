#!/usr/bin/env python
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

from __future__ import unicode_literals, print_function
from os import path
import sys
import time

from runabove import Runabove
from runabove.exception import APIError

# Python 3 renamed raw_input to input
if not 'raw_input' in dir(__builtins__):
    raw_input = input

# You can enter your crendentials here if you have them,
# otherwise leave it empty to learn how to get them.
application_key = None
application_secret = None
consumer_key = None

def sizeof_fmt(num):
    """Display bytes as human readable."""
    if num == 0:
        return '0 byte'
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')

def file_get_contents(filename):
    """Get the content of a file."""
    with file(filename) as f:
        s = f.read()
    return s

def pick_in_list(list_name, obj_list):
    """Generic function to ask the user to choose from a list."""
    print('\n%ss available' % list_name)
    for num, i in enumerate(obj_list):
        print('\t%d) %s' % (num+1, i.name))
    try:
        selected_num = raw_input('\nPlease select a %s number [1]: ' %
                                 list_name.lower())
        selected_num = int(selected_num) - 1
        selected = obj_list[selected_num]
    except (ValueError, IndexError):
        selected = obj_list[0]
    print('Using %s %s.' % (list_name.lower(), selected.name))
    return selected

# Check if the user has application credentials
if not application_key or not application_secret:
    print('\nTo use RunAbove SDK you need to register an application')
    choice = raw_input('Would you like to register one? (y/N): ')
    if choice.lower() != 'y':
        print('Not creating an application, aborting')
        sys.exit(0)
    else:
        print('\nYou can do it here https://api.runabove.com/createApp')
        print('When you are done enter here your Application Key and Secret')
        application_key = raw_input('\nApplication Key: ')
        application_secret = raw_input('Application Secret: ')

# Create an instance of RunAbove SDK interface
run = Runabove(application_key,
               application_secret,
               consumer_key=consumer_key)

# Check if the user has a Consumer Key
if not run.get_consumer_key():
    print('\nEach user using your application needs a Consumer Key.')
    choice = raw_input('\nWould you like to get one? (y/N): ')
    if choice.lower() != 'y':
        print('Not requesting a Consumer Key, aborting')
        sys.exit(0)
    else:
        print('\nYou can get it here %s' % run.get_login_url())
        raw_input('\nWhen you are logged, press Enter ')
        print('Your consumer key is: %s' % run.get_consumer_key())

# Get information about the account
acc = run.account.get()
print('\nHi %s,' % acc.first_name)

# Get the list of running instances
instances = run.instances.list()
print('\nYou have %d instance(s) running' % len(instances))
for i in instances:
    print('\t- [%s] %s (%s, %s)' % (i.region.name, i.name, i.ip, i.image.name))

# Get the list of containers
containers = run.containers.list()
print('\nYou have %d container(s)' % len(containers))
for c in containers:
    if c.is_public:
        print('\t- [%s] %s (public, %s)' % (c.region.name, c.name,
                                            sizeof_fmt(c.size)))
    else:
        print('\t- [%s] %s (private, %s)' % (c.region.name, c.name,
                                             sizeof_fmt(c.size)))

# Ask the user to select one region
region = pick_in_list('Region', run.regions.list())

# Get the list of SSH keys in the selected region
ssh_keys = run.ssh_keys.list_by_region(region)
if ssh_keys:
    print('\nYou have %d SSH key(s) in %s' % (len(ssh_keys), region.name))
    for s in ssh_keys:
        print('\t- [%s] %s (%s)' % (s.region.name, s.name, s.finger_print))
else:
    print('\nYou have no SSH key in %s' % region.name)
    # Ask the user to create an SSH key
    choice = raw_input('\nWould you like to add one? (y/N): '
                       % region.name)
    if choice.lower() == 'y':
        ssh_key_path = path.expanduser('~/.ssh/id_rsa.pub')
        if not path.isfile(ssh_key_path):
            print('You don\'t have a key in ~/.ssh/id_rsa.pub, aborting.')
        else:
            ssh_key_name = raw_input('Name of the SSH key: ')
            ssh_key_content = file_get_contents(ssh_key_path)
            try:
                run.ssh_keys.create(region, ssh_key_name, ssh_key_content)
                print('Key added to %s' % region.name)
            except APIError as e:
                print('Couldn\'t add the SSH key to RunAbove. %s' % e)

# Ask the user to create an instance if he has a key
if run.ssh_keys.list_by_region(region):
    choice = raw_input('\nWould you like to create an instance in %s? (y/N): '
                       % region.name)
    if choice.lower() == 'y':
        image = pick_in_list('Image', run.images.list_by_region(region))
        flavor = pick_in_list('Flavor', run.flavors.list_by_region(region))
        ssh_key = pick_in_list('SSH key', run.ssh_keys.list_by_region(region))
        instance_name = raw_input('\nName of the instance: ')
        instance = run.instances.create(region, instance_name,
                                        flavor, image, ssh_key)
        print('\nInstance created')
        print('Waiting for instance to be ready...')

        while not instance.status == 'ACTIVE':
            time.sleep(10)
            instance = run.instances.get_by_id(instance.id)

        print('Instance launched')
        print('\t-  IP: %s' % instance.ip)
        print('\t- VNC: %s' % instance.vnc)
        print('\t- SSH: ssh admin@%s' % instance.ip)
        choice = raw_input('\nWould you like to delete the instance? (y/N): ')
        if choice.lower() == 'y':
            instance.delete()
            print('Instance deleted')
