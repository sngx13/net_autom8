import configparser
import os
import requests
import urllib3
from datetime import datetime
from django.utils import timezone
from netaddr import IPAddress
# Models
from ..models import Device, DeviceInterfaces


# Disable invalid cert warning
urllib3.disable_warnings()
# Auth
project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(
    f'{project_dir}/inventory/authentication/device_credentials.ini'
)
# Headers
headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
}
# Keep track of poller progress
progress = []


def rest_device_info(host, http_client):
    try:
        yang_model = 'Cisco-IOS-XE-device-hardware-oper:device-hardware-data'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        if data.status_code == requests.codes.ok:
            progress.append(
                f'[+] Obtaining YANG output from: {yang_model}'
            )
            device_data = data.json()[yang_model]
            for hw in device_data['device-hardware']['device-inventory']:
                if hw['hw-type'] == 'hw-type-chassis':
                    hardware_model = hw['part-number']
                    serial_number = hw['serial-number']
                    description = hw['hw-description']
            sw_data = device_data['device-hardware']['device-system-data']
            device_current_time = datetime.strptime(
                sw_data['current-time'][0:19],
                '%Y-%m-%dT%H:%M:%S'
            ).replace(microsecond=0)
            device_boot_time = datetime.strptime(
                sw_data['boot-time'][0:19],
                '%Y-%m-%dT%H:%M:%S'
            ).replace(microsecond=0)
            device_uptime = device_current_time - device_boot_time
            ios_type = sw_data['rommon-version'].replace('ROMMON', '')
            code_version = sw_data['software-version'].split(',')[2]
            software_version = ios_type + ' ' + code_version
            device_obj = Device.objects.get(pk=host.id)
            device_obj.hardware_model = hardware_model
            device_obj.serial_number = serial_number
            device_obj.description = description
            device_obj.software_version = software_version
            device_obj.device_uptime = device_uptime
            device_obj.last_polled = timezone.now()
            device_obj.save()
            progress.append(
                f'[+] Updating {host.hostname} - DB object:{device_obj.id}'
            )
            return {'status': 'success'}
        else:
            return {'status': 'failure'}
    except Exception as error:
        return {'status': 'error', 'details': str(error)}


def rest_interface_info(host, http_client):
    try:
        if DeviceInterfaces.objects.filter(device_id=host.id):
            progress.append(
                f'[+] Deleting old interface DB entries for {host.hostname}'
            )
            DeviceInterfaces.objects.filter(device_id=host.id).delete()
        yang_intf_plain = 'ietf-interfaces:interfaces'
        yang_intf_state = 'ietf-interfaces:interfaces-state'
        data_intf_plain = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_intf_plain}'
        )
        data_intf_state = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_intf_state}'
        )
        if data_intf_plain.status_code and data_intf_state.status_code == requests.codes.ok:
            progress.append(
                f'[+] Obtaining YANG output from: {yang_intf_plain} and {yang_intf_state}'
            )
            for intf_plain in data_intf_plain.json()[yang_intf_plain]['interface']:
                for intf_state in data_intf_state.json()[yang_intf_state]['interface']:
                    if intf_plain['name'] == intf_state['name']:
                        intf_name = intf_plain['name']
                        intf_desc = intf_plain['description']
                        intf_type = intf_plain['type']
                        intf_phys = intf_state['phys-address']
                        intf_admin_status = intf_state['admin-status']
                        intf_oper_status = intf_state['oper-status']
                        try:
                            ipv4_address = intf_plain['ietf-ip:ipv4']['address'][0]['ip']
                            ipv4_subnet_mask = IPAddress(
                                intf_plain['ietf-ip:ipv4']['address'][0]['netmask']
                            ).netmask_bits()
                        except KeyError:
                            ipv4_address = ''
                            ipv4_subnet_mask = ''
                        interfaces_obj = DeviceInterfaces(
                            device_id=host,
                            name=intf_name,
                            description=intf_desc,
                            interface_type=intf_type,
                            ipv4_address=ipv4_address,
                            ipv4_subnet_mask=ipv4_subnet_mask,
                            admin_status=intf_admin_status,
                            oper_status=intf_oper_status,
                            phys_address=intf_phys
                        )
                        interfaces_obj.save()
                        progress.append(
                            f'[+] DB entry {interfaces_obj.id} created for: {intf_name}'
                        )
            return {'status': 'success'}
        else:
            return {'status': 'failure'}
    except Exception as error:
        return {'status': 'error', 'details': str(error)}


def device_initiate_poller():
    progress.clear()
    poller_result = {}
    hosts = Device.objects.all()
    for host in hosts:
        if host.username and host.password:
            username = host.username
            password = host.password
        else:
            username = auth_config['cli_logins']['username']
            password = auth_config['cli_logins']['password']
        try:
            with requests.Session() as http_client:
                http_client.auth = (username, password)
                http_client.headers = headers
                http_client.verify = False
                progress.append(
                    f'[+] Performing device poll of: {host.hostname}'
                )
                device_info = rest_device_info(host, http_client)
                interface_info = rest_interface_info(host, http_client)
                if device_info['status'] and interface_info['status'] == 'success':
                    poller_result['status'] = 'success'
                    progress.append(
                        f'>>> Polling of {host.hostname} completed successfully <<<'
                    )
                else:
                    progress.append(
                        f'[+] REST API call to: {host.hostname} has failed'
                    )
                    progress.append(
                        f'>>> Polling of {host.hostname} failed to complete <<<'
                    )
                    poller_result['status'] = 'failure'
        except Exception as error:
            return {'status': 'error', 'details': str(error)}
    poller_result.update(
        {
            'details': progress,
            'message': 'Polling task completed successfully'
        }
    )
    return poller_result
