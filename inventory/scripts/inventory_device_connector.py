import configparser
import os
from ..models import Device
from scrapli import Scrapli


project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(f'{project_dir}/inventory/authentication/device_credentials.ini')
cli_username = auth_config['cli_logins']['username']
cli_password = auth_config['cli_logins']['password']


def device_get_details(mgmt_ip, vendor):
    if 'Cisco' in vendor:
        platform = 'cisco_iosxe'
    device = {
        'host': mgmt_ip,
        'auth_username': cli_username,
        'auth_password': cli_password,
        'auth_strict_key': False,
        'platform': platform
    }
    try:
        with Scrapli(**device) as conn:
            interfaces = conn.send_command('show interfaces')
            version = conn.send_command('show version')
            routing = conn.send_command('show ip route')
            bgp_table = conn.send_command('show ip bgp')
        return {
            'interfaces': interfaces.textfsm_parse_output(),
            'version': version.textfsm_parse_output(),
            'routing': routing.textfsm_parse_output(),
            'bgp_table': bgp_table.textfsm_parse_output()
        }
    except Exception as error:
        return {'status': 'error', 'error_msg': str(error)}


def device_run_discovery():
    devices = Device.objects.all()
    for host in devices:
        if not host.serial_number:
            device = {
                'host': host.mgmt_ip,
                'auth_username': cli_username,
                'auth_password': cli_password,
                'auth_strict_key': False,
                'platform': 'cisco_iosxe'
            }
            try:
                with Scrapli(**device) as conn:
                    version = conn.send_command('show version')
                    output = version.textfsm_parse_output()
                    for i in output:
                        host.software_version = i['rommon'] + '' + i['version']
                        host.serial_number = i['serial'][0]
                        host.hardware_model = i['hardware'][0]
                        host.save()
            except Exception as error:
                print({'status': 'error', 'error_msg': str(error)})
                return {'status': 'error', 'error_msg': str(error)}
