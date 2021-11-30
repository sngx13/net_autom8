import configparser
import requests
import os
import urllib3
from scrapli import Scrapli
# Models
from ..models import Device, DeviceInterfaces
# Scripts
from .device_actions import restconf_get_interfaces
from .device_actions import scrapli_get_interfaces
from .device_actions import restconf_get_hw_information
from .device_actions import scrapli_get_hw_information


urllib3.disable_warnings()

project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(
    f'{project_dir}/inventory/authentication/device_credentials.ini'
)


def bulk_device_discovery(hosts):
    progress = []
    for host in hosts:
        if 'Cisco' in host.vendor:
            platform = 'cisco_iosxe'
            if host.username and host.password:
                username = host.username
                password = host.password
            else:
                username = auth_config['cli_logins']['username']
                password = auth_config['cli_logins']['password']
            if not host.serial_number:
                device = {
                    'host': host.mgmt_ip,
                    'auth_username': username,
                    'auth_password': password,
                    'auth_strict_key': False,
                    'platform': platform
                }
                try:
                    with Scrapli(**device) as conn:
                        progress.append(
                            f'[+] Discovering: {host.hostname}@{host.mgmt_ip}'
                        )
                        version_cmd = conn.send_command('show version')
                        restconf_cmd = 'show running | include restconf'
                        check_restconf_en = conn.send_command(restconf_cmd)
                        if check_restconf_en.result:
                            host.rest_conf_enabled = True
                        if not check_restconf_en.result:
                            host.rest_conf_enabled = False
                        output = version_cmd.textfsm_parse_output()
                        if output:
                            for i in output:
                                sw_version = i['rommon'] + ' ' + i['version']
                                host.software_version = sw_version
                                host.serial_number = i['serial'][0]
                                host.hardware_model = i['hardware'][0]
                                host.save()
                                progress.append(
                                    f'[+] Updating DB entry for: {host.hostname}'
                                    + f' S/N: {host.serial_number}'
                                    + f' & HW: {host.hardware_model}'
                                )
                except Exception as error:
                    progress.append({'status': 'error', 'message': str(error)})
                    return {'status': 'error', 'message': str(error)}
    return progress


def single_device_discovery(host):
    progress = []
    if 'Cisco' in host.vendor:
        platform = 'cisco_iosxe'
        if host.username and host.password:
            username = host.username
            password = host.password
        else:
            username = auth_config['cli_logins']['username']
            password = auth_config['cli_logins']['password']
        device = {
                    'host': host.mgmt_ip,
                    'auth_username': username,
                    'auth_password': password,
                    'auth_strict_key': False,
                    'platform': platform
                }
        try:
            with Scrapli(**device) as conn:
                progress.append(
                    f'[+] Discovering: {host.hostname}@{host.mgmt_ip}'
                )
                version_cmd = conn.send_command('show version')
                restconf_cmd = 'show running | include restconf'
                check_restconf_en = conn.send_command(restconf_cmd)
                if check_restconf_en.result:
                    host.rest_conf_enabled = True
                if not check_restconf_en.result:
                    host.rest_conf_enabled = False
                output = version_cmd.textfsm_parse_output()
                if output:
                    for i in output:
                        sw_version = i['rommon'] + ' ' + i['version']
                        host.software_version = sw_version
                        host.serial_number = i['serial'][0]
                        host.hardware_model = i['hardware'][0]
                        host.save()
                        progress.append(
                            f'[+] Updating DB entry for: {host.hostname}'
                            + f' S/N: {host.serial_number}'
                            + f' & HW: {host.hardware_model}'
                        )
        except Exception as error:
            progress.append({'status': 'error', 'message': str(error)})
            return {'status': 'error', 'message': str(error)}
    return progress


def device_run_discovery(device_id=None):
    if device_id:
        host = Device.objects.get(pk=device_id)
        discovery_progress = single_device_discovery(host)
        return {
            'status': 'success',
            'message': 'Rediscovery task completed successfully!',
            'details': discovery_progress
        }
    else:
        hosts = Device.objects.all()
        discovery_progress = bulk_device_discovery(hosts)
        return {
            'status': 'success',
            'message': 'Discovery task completed successfully!',
            'details': discovery_progress
        }


def device_get_details_via_ssh(device_id):
    host = Device.objects.get(pk=device_id)
    if 'Cisco' in host.vendor:
        platform = 'cisco_iosxe'
    if host.username and host.password:
        username = host.username
        password = host.password
    else:
        username = auth_config['cli_logins']['username']
        password = auth_config['cli_logins']['password']
    device = {
        'host': host.mgmt_ip,
        'auth_username': username,
        'auth_password': password,
        'auth_strict_key': False,
        'platform': platform
    }
    try:
        scrapli_get_interfaces(host, device)
        return {
            'interfaces': DeviceInterfaces.objects.filter(device_id=device_id),
            'version': scrapli_get_hw_information(host, device),
        }
    except Exception as error:
        return {'status': 'error', 'message': str(error)}


def device_get_details_via_rest(device_id):
    host = Device.objects.get(pk=device_id)
    if host.username and host.password:
        username = host.username
        password = host.password
    else:
        username = auth_config['cli_logins']['username']
        password = auth_config['cli_logins']['password']
    try:
        with requests.Session() as http_client:
            http_client.auth = (username, password)
            http_client.headers = {'Accept': 'application/yang-data+json'}
            http_client.verify = False
            restconf_get_interfaces(host, http_client)
            return {
                'interfaces': DeviceInterfaces.objects.filter(
                    device_id=device_id
                ),
                'version': restconf_get_hw_information(host, http_client)
            }
    except Exception as error:
        return {'status': 'error', 'message': str(error)}
