import requests
from scrapli import Scrapli
from ..models import DeviceInterfaces


def restconf_get_hw_information(host, http_client):
    try:
        yang_model = 'Cisco-IOS-XE-device-hardware-oper:device-hardware-data'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/' + yang_model
        )
        if data.status_code == requests.codes.ok:
            hw_info = data.json()['Cisco-IOS-XE-device-hardware-oper:device-hardware-data']
            return hw_info['device-hardware']['device-inventory']
    except Exception as error:
        return {'status': 'error', 'message': str(error)}


def restconf_get_interfaces(host, http_client):
    try:
        DeviceInterfaces.objects.filter(device_id=host.id).delete()
        yang_model = 'Cisco-IOS-XE-interfaces-oper:interfaces/interface'
        data = http_client.get(
            f'https://{host.mgmt_ip}/restconf/data/' + yang_model
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
                    ipv4_subnet_mask=interface['ipv4-subnet-mask'],
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
