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

"""RunAbove instance service library."""
from __future__ import absolute_import

from .base import Resource, BaseManagerWithList


class InstanceManager(BaseManagerWithList):
    """Manage instances for a RunAbove account."""

    basepath = '/instance'

    def get_by_id(self, instance_id):
        """Get one instance from a RunAbove account.

        :param instance_id: ID of the instance to retrieve
        """
        url = self.basepath + '/' + self._api.encode_for_api(instance_id)

        instance = self._api.get(url)
        return self._en_dict_to_obj(instance)

    def _load_vnc(self, instance):
        """Load the VNC link to an instance.

        :param instance: Instance to get VNC console from
        """
        try:
            instance_id = instance.id
        except AttributeError:
            instance_id = instance
        url = self.basepath + '/' + instance_id + '/vnc'
        vnc = self._api.get(url)
        return vnc['url']

    def _dict_to_obj(self, ins):
        """Converts a dict to an instance object."""
        region = self._handler.regions._name_to_obj(ins['region'])
        return Instance(self,
                        ins.get('instanceId'),
                        ins.get('name'),
                        ins.get('ip'),
                        region,
                        ins.get('flavorId'),
                        ins.get('imageId'),
                        ins.get('keyName'),
                        ins.get('status'),
                        ins.get('created'))

    def _en_dict_to_obj(self, ins):
        """Converts an enhanced dict to an instance object.

        The enhanced dict got with the GET of one instance allows
        to build the flavor, image and SSH key objects directly
        without making a call for each of them. However SSH key
        is not mandatory so can be None.
        """
        try:
            ssh_key_name = ins['sshKey']['name']
            ssh_key = self._handler.ssh_keys._dict_to_obj(ins['sshKey'])
        except TypeError:
            ssh_key_name = None
            ssh_key = None
        region = self._handler.regions._name_to_obj(ins['region'])
        flavor = self._handler.flavors._dict_to_obj(ins['flavor'])
        image = self._handler.images._dict_to_obj(ins['image'])
        return Instance(self,
                        ins['instanceId'],
                        ins.get('name'),
                        ins.get('ipv4'),
                        region,
                        ins['flavor']['id'],
                        ins['image']['id'],
                        ssh_key_name,
                        ins.get('status'),
                        ins.get('created'),
                        ips=ins.get('ips'),
                        flavor=flavor,
                        image=image,
                        ssh_key=ssh_key)

    def create(self, region, name, flavor, image, ssh_key=None):
        """Launch a new instance inside a region with a public key.

        :param region: Name or object region of the new instance
        :param name: Name of the new instance
        :param flavor: ID or object flavor used for this Instance
        :param image: ID or object image for the instance
        :param ssh_key: Name or object SSH key to install
        """
        try:
            region_name = region.name
        except AttributeError:
            region_name = region
        try:
            flavor_id = flavor.id
        except AttributeError:
            flavor_id = flavor
        try:
            image_id = image.id
        except AttributeError:
            image_id = image
        content = {
            'flavorId': flavor_id,
            'imageId': image_id,
            'name': name,
            'region': region_name
        }
        if ssh_key:
            try:
                content['sshKeyName'] = ssh_key.name
            except AttributeError:
                content['sshKeyName'] = ssh_key
        instance_id = self._api.post(self.basepath, content)['instanceId']
        return self.get_by_id(instance_id)

    def rename(self, instance, new_name):
        """Rename an existing instance.

        :param instance: instance_id or Instance object to be deleted
        :param new_name: new name of instance
        """
        content = {
            'name': new_name
        }
        try:
            id = instance.id
        except AttributeError:
            id = instance
        url = self.basepath + '/' + self._api.encode_for_api(id)
        self._api.put(url, content)

    def delete(self, instance):
        """Delete an instance from an account.

        :param instance: instance_id or Instance object to be deleted
        """
        try:
            id = instance.id
        except AttributeError:
            id = instance
        url = self.basepath + '/' + self._api.encode_for_api(id)
        self._api.delete(url)


class Instance(Resource):
    """Represents one instance."""

    def __init__(self, manager, id, name, ip, region, flavor_id, image_id,
                 ssh_key_name, status, created, ips=None,
                 flavor=None, image=None, ssh_key=None):
        self._manager = manager
        self.id = id
        self.name = name
        self.ip = ip
        self.created = created
        self.status = status
        self.region = region
        self._flavor_id = flavor_id
        self._flavor = flavor
        self._image_id = image_id
        self._image = image
        self._ssh_key_name = ssh_key_name
        self._ssh_key = ssh_key
        self._vnc = None
        self._ips = ips

    @property
    def flavor(self):
        """Lazy loading of flavor object."""
        if not self._flavor:
            self._flavor = self._manager._handler.\
                flavors.get_by_id(self._flavor_id)
        return self._flavor

    @property
    def image(self):
        """Lazy loading of image object."""
        if not self._image:
            self._image = self._manager._handler.\
                images.get_by_id(self._image_id)
        return self._image

    @property
    def ssh_key(self):
        """Lazy loading of ssh_key object."""
        if not self._ssh_key_name:
            return None
        if not self._ssh_key:
            self._ssh_key = self._manager._handler.\
                ssh_keys.get_by_name(self.region, self._ssh_key_name)
        return self._ssh_key

    @property
    def ips(self):
        """Lazy loading of the list of IPs."""
        if self._ips is None:
            self._ips = self._manager.get_by_id(self.id)._ips
        return self._ips

    @property
    def vnc(self):
        """Lazy loading of VNC link."""
        if not self._vnc:
            self._vnc = self._manager._load_vnc(self)
        return self._vnc

    def delete(self):
        """Delete instance represented by this object from the account."""
        self._manager.delete(self)

    def rename(self, new_name):
        """Rename instance represented by this object."""
        self._manager.rename(self, new_name)
        self.name = new_name
