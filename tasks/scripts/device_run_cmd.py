import configparser
import os
from scrapli import Scrapli
from scrapli.exceptions import ScrapliException
# Models
from inventory.models import Device


# Auth
project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(
    f'{project_dir}/tasks/authentication/device_credentials.ini'
)

# Keep track of task progress
progress = []


def cli_command_runner(device_id, command):
    progress.clear()
    host = Device.objects.get(id=device_id)
    if 'Cisco' in host.vendor:
        platform = 'cisco_iosxe'
        if host.username and host.password:
            username = host.username
            password = host.password
            progress.append(
                '[+] Found existing login details'
            )
        else:
            username = auth_config['cli_logins']['username']
            password = auth_config['cli_logins']['password']
            progress.append(
                '[+] Using hardcoded logins'
            )
        device = {
            'host': host.mgmt_ip,
            'auth_username': username,
            'auth_password': password,
            'auth_strict_key': False,
            'platform': platform,
            'ssh_config_file': '/etc/ssh/ssh_config'
        }
        try:
            with Scrapli(**device) as conn:
                progress.append(
                    f'[+] Discovering: {host.hostname}@{host.mgmt_ip}'
                )
                unformated_output = conn.send_command(command)
                formated_output = unformated_output.textfsm_parse_output()
                return {'status': 'success', 'details': formated_output}
        except ScrapliException:
            progress.append(
                f'[+] Unable to connect to: {host.hostname}'
            )
            return {'status': 'failure'}
