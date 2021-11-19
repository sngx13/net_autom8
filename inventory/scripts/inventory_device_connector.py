import configparser
import os
from scrapli import Scrapli


project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(f'{project_dir}/inventory/authentication/device_credentials.ini')


def device_connect(mgmt_ip, software_version):
    if 'IOS-XE' in software_version:
        platform = 'cisco_iosxe'
    device = {
        'host': mgmt_ip,
        'auth_username': auth_config['cli_logins']['username'],
        'auth_password': auth_config['cli_logins']['password'],
        'auth_strict_key': False,
        'platform': platform
    }
    with Scrapli(** device) as conn:
        interfaces = conn.send_command('show interfaces')
        version = conn.send_command('show version')
    return {
        'interfaces': interfaces.textfsm_parse_output(),
        'version': version.textfsm_parse_output()
    }
