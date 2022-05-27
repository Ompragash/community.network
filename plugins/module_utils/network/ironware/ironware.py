#
# Copyright (c) 2017, Paul Baker <paul@paulbaker.id.au>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list, EntityCollection
from ansible.module_utils.connection import Connection, exec_command

_DEVICE_CONFIG = None
_CONNECTION = None

command_spec = {
    'command': dict(key=True),
    'prompt': dict(),
    'answer': dict()
}


def check_args(module):
    pass


def get_connection(module):
    global _CONNECTION
    if _CONNECTION:
        return _CONNECTION
    _CONNECTION = Connection(module._socket_path)

    return _CONNECTION


def to_commands(module, commands):
    if not isinstance(commands, list):
        raise AssertionError('argument must be of type <list>')

    transform = EntityCollection(module, command_spec)
    commands = transform(commands)

    for index, item in enumerate(commands):
        if module.check_mode and not item['command'].startswith('show'):
            module.warn('only show commands are supported when using check '
                        'mode, not executing `%s`' % item['command'])

    return commands


def run_commands(module, commands, check_rc=True):
    connection = get_connection(module)

    commands = to_commands(module, to_list(commands))

    responses = list()

    for cmd in commands:
        out = connection.get(**cmd)
        responses.append(to_text(out, errors='surrogate_then_replace'))

    return responses


def get_config(module, source='running', flags=None):
    global _DEVICE_CONFIG
    if source == 'running' and flags is None and _DEVICE_CONFIG is not None:
        return _DEVICE_CONFIG
    else:
        conn = get_connection(module)
        out = conn.get_config(source=source, flags=flags)
        cfg = to_text(out, errors='surrogate_then_replace').strip()
        if source == 'running' and flags is None:
            _DEVICE_CONFIG = cfg
        return cfg


def load_config(module, config):
    conn = get_connection(module)
    conn.edit_config(config)
