import configparser
import os
import requests
import urllib3
from http import HTTPStatus
from netaddr import IPNetwork


# Disable invalid cert warning
urllib3.disable_warnings()
# Auth
project_dir = os.getcwd()
auth_config = configparser.ConfigParser()
auth_config.read(
    f'{project_dir}/tasks/authentication/device_credentials.ini'
)
# Headers
headers = {
    'Accept': 'application/yang-data+json',
    'Content-Type': 'application/yang-data+json'
}
# Response codes
http_respose_codes = [200, 201, 204]


def edit_interface(host, interface):
    net_mask = str(
        IPNetwork(
            f'{interface.ipv4_address}/{interface.ipv4_subnet_mask}'
        ).netmask
    )
    if interface.admin_status == 'up':
        admin_status = True
    elif interface.admin_status == 'down':
        admin_status = False
    cfg = {
        'ietf-interfaces:interface': {
            'name': interface.name,
            'description': interface.description,
            'enabled': admin_status,
            'ietf-ip:ipv4': {
                'address': [
                    {
                        'ip': interface.ipv4_address,
                        'netmask': net_mask
                    }
                ]
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
                f'https://{host.mgmt_ip}/restconf/data/ietf-interfaces:interfaces/interface={interface.name}',
                auth=(username, password),
                verify=False,
                json=cfg
            )
            if data.status_code in http_respose_codes:
                cfg_save = http_client.post(
                    f'https://{host.mgmt_ip}/restconf/operations/cisco-ia:save-config/',
                    auth=(username, password),
                    verify=False,
                )
                if cfg_save.status_code in http_respose_codes:
                    return {'status': 'success', 'details': 'Config was saved'}
            else:
                http_status_verbal = str(
                    HTTPStatus(data.status_code)).split('.')[1]
                return {
                    'status': 'failure',
                    'details': f'Could not edit {interface.name}, received HTTP:{data.status_code}/{http_status_verbal}'
                }
    except Exception as error:
        return {'status': 'error', 'details': str(error)}


def delete_interface(host, interface):
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
            data = http_client.delete(
                f'https://{host.mgmt_ip}/restconf/data/ietf-interfaces:interfaces/interface={interface.name}',
                auth=(username, password),
                verify=False
            )
            if data.status_code in http_respose_codes:
                cfg_save = http_client.post(
                    f'https://{host.mgmt_ip}/restconf/operations/cisco-ia:save-config/',
                    auth=(username, password),
                    verify=False,
                )
                if cfg_save.status_code in http_respose_codes:
                    return {'status': 'success', 'details': 'Config was saved'}
            else:
                http_status_verbal = str(
                    HTTPStatus(data.status_code)).split('.')[1]
                return {
                    'status': 'failure',
                    'details': f'Could not delete {interface.name}, received HTTP:{data.status_code}/{http_status_verbal}'
                }
    except Exception as error:
        return {'status': 'error', 'details': str(error)}
