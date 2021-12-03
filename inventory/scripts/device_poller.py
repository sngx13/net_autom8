import configparser
import os
import re
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

# Regex parser for interfaces
if_parser = re.compile('([a-zA-Z]+)([0-9]+)')
# List of common interfaces for matching ones found on device
common_intfs = [
    'FastEthernet',
    'GigabitEthernet',
    'Ten-GigabitEthernet',
    'Tunnel',
    'Loopback'
]
# Keep track of poller progress
poller_progress = []


def rest_device_info(host, http_client):
    try:
        yang_model = 'Cisco-IOS-XE-device-hardware-oper:device-hardware-data'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        poller_progress.append(
            f'[+] Obtaining YANG output from: {yang_model}'
        )
        if data.status_code == requests.codes.ok:
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
            poller_progress.append(
                f'[+] Updating {host.hostname} - DB object:{device_obj.id}'
            )
            return {'status': 'success'}
    except Exception as error:
        return {'status': 'error', 'details': str(error)}


def rest_interface_info(host, http_client):
    try:
        poller_progress.append(
            f'[+] Deleting old interface DB entries for {host.hostname}'
        )
        DeviceInterfaces.objects.filter(device_id=host.id).delete()
        yang_model = 'Cisco-IOS-XE-interfaces-oper:interfaces'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        poller_progress.append(
            f'[+] Obtaining YANG output from: {yang_model}'
        )
        if data.status_code == requests.codes.ok:
            interface_data = data.json()[yang_model]
            for interface in interface_data['interface']:
                # Exclude any interfaces other than Ethernet,Loopback,Tunnel
                if if_parser.match(interface['name']).group(1) in common_intfs:
                    # Interface type e.g: Ethernet/Loopback/Tunnel
                    if 'csmacd' in interface['interface-type']:
                        speed = interface['ether-state']['negotiated-port-speed'].replace('speed-', '')
                        duplex = interface['ether-state']['negotiated-duplex-mode'].replace('-duplex', '')
                        interface_type = 'ethernet'
                    elif 'loopback' in interface['interface-type']:
                        speed = 'N/A'
                        duplex = 'N/A'
                        interface_type = 'loopback'
                    elif 'tunnel' in interface['interface-type']:
                        speed = 'N/A'
                        duplex = 'N/A'
                        interface_type = 'tunnel'
                    # Admin status
                    if 'if-state-up' in interface['admin-status']:
                        admin_status = 'up'
                    elif 'if-state-down' in interface['admin-status']:
                        admin_status = 'down'
                    # Operational status
                    if 'ready' in interface['oper-status']:
                        oper_status = 'up'
                    elif 'no-pass' in interface['oper-status']:
                        oper_status = 'down'
                    elif 'lower-layer-down' in interface['oper-status']:
                        oper_status = 'down'
                    try:
                        ipv4_address = interface['ipv4']
                        ipv4_subnet_mask = IPAddress(
                            interface['ipv4-subnet-mask']
                        ).netmask_bits()
                    except KeyError:
                        ipv4_address = 'N/A'
                        ipv4_subnet_mask = 'N/A'
                    interfaces_obj = DeviceInterfaces(
                        device_id=host,
                        name=interface['name'],
                        description=interface['description'],
                        interface_type=interface_type,
                        ipv4_address=ipv4_address,
                        ipv4_subnet_mask=ipv4_subnet_mask,
                        admin_status=admin_status,
                        oper_status=oper_status,
                        speed=speed,
                        duplex=duplex,
                        mtu=interface['mtu'],
                        phys_address=interface['phys-address']
                    )
                    interfaces_obj.save()
                    poller_progress.append(
                        f'[+] DB entry {interfaces_obj.id} created for: ' +
                        interface['name']
                    )
            return {'status': 'success'}
    except Exception as error:
        return {'status': 'error', 'details': str(error)}


def device_initiate_poller():
    poller_result = {}
    if Device.objects.all():
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
                    http_client.headers = {'Accept': 'application/yang-data+json'}
                    http_client.verify = False
                    poller_progress.append(
                        f'[+] Performing device poll of: {host.hostname}'
                    )
                    device_info = rest_device_info(host, http_client)
                    interface_info = rest_interface_info(host, http_client)
                    if device_info['status'] and interface_info['status'] == 'success':
                        poller_result['status'] = 'success'
                        poller_progress.append(
                            f'>>> Polling of {host.hostname} completed successfully <<<'
                        )
                    else:
                        poller_result['status'] = 'failure'
            except Exception as error:
                return {'status': 'error', 'details': str(error)}
        poller_result.update(
            {
                'details': poller_progress,
                'message': 'Polling task completed successfully'
            }
        )
        return poller_result
    else:
        return {'status': 'failed', 'details': 'No devices in the database'}
