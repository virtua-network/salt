# -*- coding: utf-8 -*-
'''
Management of Windows system information
========================================

.. versionadded:: 2014.1.0

This state is used to manage system information such as the computer name and
description.

.. code-block:: yaml

    ERIK-WORKSTATION:
      system.computer_name: []

    This is Erik's computer, don't touch!:
      system.computer_desc: []
'''

from __future__ import absolute_import

# Import python libs
import logging

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'system'


def __virtual__():
    '''
    This only supports Windows
    '''
    if salt.utils.is_windows() and 'system.get_computer_desc' in __salt__:
        return __virtualname__
    return False


def computer_desc(name):
    '''
    Manage the computer's description field

    name
        The desired computer description
    '''
    # Just in case someone decides to enter a numeric description
    name = str(name)

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Computer description already set to \'{0}\''.format(name)}

    before_desc = __salt__['system.get_computer_desc']()

    if before_desc == name:
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = ('Computer description will be changed to \'{0}\''
                          .format(name))
        return ret

    result = __salt__['system.set_computer_desc'](name)
    if result['Computer Description'] == name:
        ret['comment'] = ('Computer description successfully changed to \'{0}\''
                          .format(name))
        ret['changes'] = {'old': before_desc, 'new': name}
    else:
        ret['result'] = False
        ret['comment'] = ('Unable to set computer description to '
                          '\'{0}\''.format(name))
    return ret

computer_description = salt.utils.alias_function(computer_desc, 'computer_description')


def computer_name(name):
    '''
    Manage the computer's name

    name
        The desired computer name
    '''
    # Just in case someone decides to enter a numeric description
    name = str(name)

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Computer name already set to \'{0}\''.format(name)}

    before_name = __salt__['system.get_computer_name']()
    pending_name = __salt__['system.get_pending_computer_name']()

    if before_name == name and pending_name is None:
        return ret
    elif pending_name == name.upper():
        ret['comment'] = ('The current computer name is \'{0}\', but will be '
                          'changed to \'{1}\' on the next reboot'
                          .format(before_name, name))
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Computer name will be changed to \'{0}\''.format(name)
        return ret

    result = __salt__['system.set_computer_name'](name)
    if result is not False:
        after_name = result['Computer Name']['Current']
        after_pending = result['Computer Name'].get('Pending')
        if ((after_pending is not None and after_pending == name) or
                (after_pending is None and after_name == name)):
            ret['comment'] = 'Computer name successfully set to \'{0}\''.format(name)
            if after_pending is not None:
                ret['comment'] += ' (reboot required for change to take effect)'
        ret['changes'] = {'old': before_name, 'new': name}
    else:
        ret['result'] = False
        ret['comment'] = 'Unable to set computer name to \'{0}\''.format(name)
    return ret


def hostname(name):
    '''
    .. versionadded:: 2016.3.0

    Manage the hostname of the computer

    name
        The hostname to set
    '''
    ret = {
        'name': name,
        'changes': {},
        'result': True,
        'comment': ''
    }

    current_hostname = __salt__['system.get_hostname']()

    if current_hostname.upper() == name.upper():
        ret['comment'] = "Hostname is already set to '{0}'".format(name)
        return ret

    out = __salt__['system.set_hostname'](name)

    if out:
        ret['comment'] = "The current hostname is '{0}', " \
                         "but will be changed to '{1}' on the next reboot".format(current_hostname, name)
        ret['changes'] = {'hostname': name}
    else:
        ret['result'] = False
        ret['comment'] = 'Unable to set hostname'

    return ret


def join_domain(name, username=None, password=None, account_ou=None,
                account_exists=False, restart=False):

    '''
    Checks if a computer is joined to the Domain.
    If the computer is not in the Domain, it will be joined.

    name:
        The name of the Domain.

    username:
        Username of an account which is authorized to join computers to the
        specified domain. Need to be either fully qualified like user@domain.tld
        or simply user.

    password:
        Password of the account to add the computer to the Domain.

    account_ou:
        The DN of the OU below which the account for this computer should be
        created when joining the domain,
        e.g. ou=computers,ou=departm_432,dc=my-company,dc=com.

    account_exists:
        Needs to be set to True to allow re-using an existing computer account.

    restart:
        Needs to be set to True to restart the computer after a successful join.

    .. code-block::yaml
        join_to_domain:
          system.join_domain:
            - name: mydomain.local.com
            - username: myaccount@mydomain.local.com
            - password: mysecretpassword
            - restart: True
    '''

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Computer already added to \'{0}\''.format(name)}

    # Set name to domain, needed for the add to domain module.
    domain = name

    current_domain_dic = __salt__['system.get_domain_workgroup']()
    if 'Domain' in current_domain_dic:
        current_domain = current_domain_dic['Domain']
    elif 'Workgroup' in current_domain_dic:
        current_domain = 'Workgroup'
    else:
        current_domain = None

    if domain == current_domain:
        ret['comment'] = 'Computer already added to \'{0}\''.format(name)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Computer will be added to \'{0}\''.format(name)
        return ret

    result = __salt__['system.join_domain'](domain, username, password,
                                            account_ou, account_exists,
                                            restart)
    if result is not False:
        ret['comment'] = 'Computer added to \'{0}\''.format(name)
    else:
        ret['comment'] = 'Computer failed to join \'{0}\''.format(name)
        ret['result'] = False
    return ret
