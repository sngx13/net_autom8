import configparser
import os
from scrapli.driver.core import IOSXEDriver


project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(f'{project_dir}/inventory/authentication/device_credentials.ini')


def device_connect(mgmt_ip):
    device = {
        'host': mgmt_ip,
        'auth_username': auth_config['cli_logins']['username'],
        'auth_password': auth_config['cli_logins']['password'],
        'auth_strict_key': False,
    }
    with IOSXEDriver(** device) as conn:
        response = conn.send_command('show interfaces')
    return response.textfsm_parse_output()
