import configparser
import os
from scrapli import Scrapli
from scrapli.exceptions import ScrapliException
# Models
from ..models import Device, DeviceInterfaces


project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(
    f'{project_dir}/inventory/authentication/device_credentials.ini'
)


def bulk_device_discovery(hosts):
    progress = []
    for host in hosts:
        progress.append(
            f'[+] Initiating connection to: {host.hostname}'
        )
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
            if not host.serial_number:
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
                        version_cmd = conn.send_command('show version')
                        restconf_cmd = 'show running | include restconf'
                        check_restconf_en = conn.send_command(restconf_cmd)
                        output = version_cmd.textfsm_parse_output()
                except ScrapliException:
                    progress.append(
                         f'[+] Unable to connect to: {host.hostname}'
                    )
                    return {
                        'status': 'error',
                        'details': f'[+] Unable to connect to: {host.hostname}'
                    }
                else:
                    if check_restconf_en.result:
                        host.rest_conf_enabled = True
                        progress.append(
                            '[+] Restconf is enabled on the device'
                        )
                    if not check_restconf_en.result:
                        host.rest_conf_enabled = False
                        progress.append(
                            '[+] Restconf is not enabled on the device'
                        )
                    if output:
                        for i in output:
                            software_version = i['rommon'] + ' ' + i['version']
                            host.software_version = software_version
                            host.serial_number = i['serial'][0]
                            host.hardware_model = i['hardware'][0]
                            host.device_uptime = i['uptime']
                            host.save()
                            progress.append(
                                f'[+] Device db id: {host.id} serial: {host.serial_number}'
                            )
    return {'status': 'success', 'details': progress}


def single_device_discovery(host):
    progress = []
    progress.append(
        f'[+] Initiating connection to: {host.hostname}'
    )
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
                version_cmd = conn.send_command('show version')
                restconf_cmd = 'show running | include restconf'
                check_restconf_en = conn.send_command(restconf_cmd)
                output = version_cmd.textfsm_parse_output()
        except ScrapliException:
            progress.append(
                f'[+] Unable to connect to: {host.hostname}'
            )
            return {
                'status': 'error',
                'details': f'[+] Unable to connect to: {host.hostname}'
            }
        else:
            if check_restconf_en.result:
                host.rest_conf_enabled = True
                progress.append(
                    '[+] Restconf is enabled on the device'
                )
            if not check_restconf_en.result:
                host.rest_conf_enabled = False
                progress.append(
                    '[+] Restconf is not enabled on the device'
                )
            if output:
                for i in output:
                    software_version = i['rommon'] + ' ' + i['version']
                    host.software_version = software_version
                    host.serial_number = i['serial'][0]
                    host.hardware_model = i['hardware'][0]
                    host.device_uptime = i['uptime']
                    host.save()
                    progress.append(
                        f'[+] Device db id: {host.id} serial: {host.serial_number}'
                    )
                return {'status': 'success', 'details': progress}


def device_initiate_discovery(device_id=None):
    if device_id:
        host = Device.objects.get(pk=device_id)
        discovery_progress = single_device_discovery(host)
        if discovery_progress['status'] == 'success':
            discovery_progress.update(
                {'message': 'Rediscovery task completed successfully!'}
            )
            return discovery_progress
        else:
            return discovery_progress
    else:
        hosts = Device.objects.all()
        discovery_progress = bulk_device_discovery(hosts)
        if discovery_progress['status'] == 'success':
            discovery_progress.update(
                {'message': 'Discovery task completed successfully!'}
            )
            return discovery_progress
        else:
            return discovery_progress
