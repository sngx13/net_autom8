import requests
from netaddr import IPAddress
from scrapli import Scrapli
from datetime import datetime
# Models
from ..models import DeviceInterfaces


def scrapli_get_hw_information(host, device):
    system_data = {}
    try:
        with Scrapli(**device) as conn:
            device_data = conn.send_command('show version')
            for hw in device_data.textfsm_parse_output():
                system_data['hardware_model'] = hw['hardware'][0]
                system_data['software_version'] = hw['version']
                system_data['serial'] = hw['serial'][0]
                system_data['uptime'] = hw['uptime']
                system_data['reload_reason'] = hw['reload_reason']
            return system_data
    except Exception as error:
        return {'status': 'error', 'message': str(error)}


def scrapli_get_interfaces(host, device):
    try:
        DeviceInterfaces.objects.filter(device_id=host.id).delete()
        with Scrapli(**device) as conn:
            interface_data = conn.send_command('show interfaces')
        for interface in interface_data.textfsm_parse_output():
            if interface['ip_address']:
                subnet_mask = interface['ip_address'].split('/')[1]
            if not interface['ip_address']:
                subnet_mask = 'N/A'
            interfaces_obj = DeviceInterfaces(
                device_id=host,
                name=interface['interface'],
                description=interface['description'],
                interface_type=interface['encapsulation'],
                ipv4_address=interface['ip_address'],
                ipv4_subnet_mask=subnet_mask,
                admin_status='N/A',
                oper_status=interface['protocol_status'],
                speed=interface['speed'],
                duplex=interface['duplex'].replace('Duplex', ''),
                mtu=interface['mtu'],
                phys_address=interface['bia'],
                in_crc_errors=interface['crc']
            )
            interfaces_obj.save()
    except Exception as error:
        return {'status': 'error', 'message': str(error)}


def restconf_get_hw_information(host, http_client):
    system_data = {}
    try:
        yang_model = 'Cisco-IOS-XE-device-hardware-oper:device-hardware-data'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        if data.status_code == requests.codes.ok:
            device_data = data.json()['Cisco-IOS-XE-device-hardware-oper:device-hardware-data']
            for hw in device_data['device-hardware']['device-inventory']:
                if hw['hw-type'] == 'hw-type-chassis':
                    system_data['hardware_model'] = hw['part-number']
                    system_data['serial'] = hw['serial-number']
            sw_data = device_data['device-hardware']['device-system-data']
            device_current_time = datetime.strptime(
                sw_data['current-time'],
                '%Y-%m-%dT%H:%M:%S.%f+00:00'
            ).replace(microsecond=0)
            device_boot_time = datetime.strptime(
                sw_data['boot-time'],
                '%Y-%m-%dT%H:%M:%S+00:00'
            ).replace(microsecond=0)
            device_uptime = device_current_time - device_boot_time
            ios_type = sw_data['rommon-version'].replace('ROMMON', '')
            release_version = sw_data['software-version'].split()[9]
            system_data['software_version'] = ios_type + ' ' + release_version
            system_data['uptime'] = str(device_uptime)
            system_data['reload_reason'] = sw_data['last-reboot-reason']
        return system_data
    except Exception as error:
        return {'status': 'error', 'message': str(error)}


def restconf_get_interfaces(host, http_client):
    try:
        DeviceInterfaces.objects.filter(device_id=host.id).delete()
        yang_model = 'Cisco-IOS-XE-interfaces-oper:interfaces/interface'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_model}'
        )
        if data.status_code == requests.codes.ok:
            interface_data = data.json()['Cisco-IOS-XE-interfaces-oper:interface']
            for interface in interface_data:
                if 'csmacd' in interface['interface-type']:
                    speed = interface['ether-state']['negotiated-port-speed'].replace('speed-', '')
                    duplex = interface['ether-state']['negotiated-duplex-mode'].replace('-duplex', '')
                elif 'loopback' in interface['interface-type']:
                    speed = 'N/A'
                    duplex = 'N/A'
                interfaces_obj = DeviceInterfaces(
                    device_id=host,
                    name=interface['name'],
                    description=interface['description'],
                    interface_type=interface['interface-type'],
                    ipv4_address=interface['ipv4'],
                    ipv4_subnet_mask=IPAddress(
                        interface['ipv4-subnet-mask']
                    ).netmask_bits(),
                    admin_status=interface['admin-status'],
                    oper_status=interface['oper-status'],
                    speed=speed,
                    duplex=duplex,
                    mtu=interface['mtu'],
                    phys_address=interface['phys-address'],
                    in_crc_errors=interface['statistics']['in-crc-errors']
                )
                interfaces_obj.save()
    except Exception as error:
        return {'status': 'error', 'message': str(error)}
