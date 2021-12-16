import configparser
import os
import re
import requests
import urllib3
from http import HTTPStatus
from netaddr import IPNetwork
from requests import codes


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
# Regex parser for interfaces
if_parser = re.compile('([a-zA-Z]+)([0-9]+)')


def edit_interface(host, interface):
    net_mask = str(
        IPNetwork(
            f'{interface.ipv4_address}/{interface.ipv4_subnet_mask}'
        ).netmask
    )
    interface_type = str(if_parser.findall(interface.name)[0][0])
    interface_number = int(if_parser.findall(interface.name)[0][1])
    cfg = {
        f'Cisco-IOS-XE-native:{interface_type}': {
            'name': interface_number,
            'description': interface.description,
            'ip': {
                'address': {
                    'primary': {
                        'address': interface.ipv4_address,
                        'mask': net_mask
                    }
                }
            }
        }
    }
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
            data = http_client.patch(
                f'https://{host.mgmt_ip}/restconf/data/native/interface/{interface_type}={interface_number}',
                auth=(username, password),
                verify=False,
                json=cfg
            )
            if data.status_code == codes.ok:
                print(data)
                cfg_save = http_client.post(
                    f'https://{host.mgmt_ip}/restconf/operations/cisco-ia:save-config/',
                    auth=(username, password),
                    verify=False,
                )
                print(cfg_save)
            else:
                http_status_description = str(
                    HTTPStatus(data.status_code)).split('.')[1]
                print(
                    f'Received HTTP:{data.status_code} - {http_status_description}'
                )
    except Exception as error:
        return {'status': 'error', 'details': str(error)}
