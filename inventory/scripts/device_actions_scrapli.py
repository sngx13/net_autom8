from scrapli import Scrapli
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
            if 'ARPA' in interface['encapsulation'] or '802.1Q' in interface['encapsulation']:
                interface_type = 'ethernet'
                speed = interface['speed']
                duplex = interface['duplex'].replace('Duplex', '')
            elif interface['encapsulation'] != 'ARPA':
                interface_type = interface['encapsulation'].lower()
                speed = 'N/A'
                duplex = 'N/A'
            if interface['link_status'] == 'administratively down':
                oper_status = 'down'
                admin_status = 'down'
            if interface['link_status'] and interface['protocol_status'] == 'up':
                oper_status = 'up'
                admin_status = 'up'
            elif interface['link_status'] and interface['protocol_status'] == 'down':
                oper_status = 'down'
                admin_status = 'up'
            interfaces_obj = DeviceInterfaces(
                device_id=host,
                name=interface['interface'],
                description=interface['description'],
                interface_type=interface_type,
                ipv4_address=interface['ip_address'],
                ipv4_subnet_mask=subnet_mask,
                admin_status=admin_status,
                oper_status=oper_status,
                speed=speed,
                duplex=duplex,
                mtu=interface['mtu'],
                phys_address=interface['bia'],
                in_crc_errors=interface['crc']
            )
            interfaces_obj.save()
    except Exception as error:
        return {'status': 'error', 'message': str(error)}
