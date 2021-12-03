import re
import requests
from netaddr import IPAddress
from datetime import datetime
# Models
from ..models import DeviceInterfaces


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
# Task progress
progress = []


def clear_task_progress():
    progress.clear()


def restconf_get_hw_information(host, http_client):
    system_data = {}
    try:
        yang_model = 'Cisco-IOS-XE-device-hardware-oper:device-hardware-data'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        if data.status_code == requests.codes.ok:
            device_data = data.json()[yang_model]
            for hw in device_data['device-hardware']['device-inventory']:
                if hw['hw-type'] == 'hw-type-chassis':
                    system_data['hardware_model'] = hw['part-number']
                    system_data['serial'] = hw['serial-number']
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
            system_data['software_version'] = ios_type + ' ' + code_version
            system_data['uptime'] = str(device_uptime)
            system_data['reload_reason'] = sw_data['last-reboot-reason']
        return system_data
    except Exception as error:
        return {'status': 'error', 'details': str(error)}


def restconf_get_interfaces(host, http_client):
    try:
        DeviceInterfaces.objects.filter(device_id=host.id).delete()
        yang_model = 'Cisco-IOS-XE-interfaces-oper:interfaces'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        progress.append(
            f'[+] Connecting to {host.hostname}, using YANG: {yang_model}'
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
                    progress.append(
                        f'[+] DB entry {interfaces_obj.id} created for: ' +
                        interface['name']
                    )
            return {'status': 'success', 'details': progress}
    except Exception as error:
        return {'status': 'error', 'details': str(error)}
