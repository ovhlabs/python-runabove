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

from runabove import Runabove
from runabove.exception import APIError

from novaclient.client import Client as NovaClient
from neutronclient.neutron.client import Client as NeutronClient
from swiftclient.client import Connection as SwiftClient

# Set your credentials here
application_key = "<application key>"
application_secret = "<application secret>"
consumer_key = "<consumer key>"
region = 'SBG-1' # or 'BHS-1'

def get_novaclient(token, region_name):
    """Instanciate a python novaclient.Client() object with proper
    credentials

    param: region_name: name of the region
    raises: ImportError: when novaclient is not available
    raises: KeyError: when no matching endpoint is found
    """
    return NovaClient('2',
        auth_token=token.auth_token,
        auth_url=token.get_endpoint('identity', region_name)['url'],
        tenant_id=token.project['id'],
        region_name=region_name)

def get_neutronclient(token, region_name):
    """Instanciate a python neutronclient.Client() object with proper
    credentials

    param: region_name: name of the region
    raises: ImportError: when neutronclient is not available
    raises: KeyError: when no matching endpoint is found
    """
    return NeutronClient('2.0',
        token=token.auth_token,
        tenant_name=token.project['name'],
        endpoint_url=token.get_endpoint('network', region_name)['url'])

def get_swiftclient(token, region_name):
    """Instanciate a python switfclient.Connection() object with proper
    credentials

    param: region_name: name of the region
    raises: ImportError: when swiftclient is not available
    raises: KeyError: when no matching endpoint is found
    """
    return SwiftClient(
        preauthurl=token.get_endpoint('object-store', 'SBG-1')['url'],
        preauthtoken=token.auth_token)

if __name__ == "__main__":
    # create a RunAbove client
    run = Runabove(application_key, application_secret, consumer_key)

    # get a token
    token = run.tokens.get()

    # demo: novaclient --> list VMs
    nova = get_novaclient(token, region)
    print "--------- VM list -----------"
    for server in nova.servers.list():
        print ' -', server.name
    print ""

    # demo: swiftclient --> list containers
    swift = get_swiftclient(token, region)
    print "----- Container list --------"
    for container in swift.get_account()[1]:
        print ' -', container['name']
    print ""

    # demo: neutronclient --> list networks
    neutron = get_neutronclient(token, region)
    print "------- Network list --------"
    for network in neutron.list_networks(fields='name')['networks']:
        print ' -', network['name']
    print ""

