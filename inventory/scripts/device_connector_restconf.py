import requests
import urllib3

urllib3.disable_warnings()

base_url = 'restconf/data'
yang_models = [
    'Cisco-IOS-XE-native:native',
    'Cisco-IOS-XE-platform-software-oper:cisco-platform-software',
    'Cisco-IOS-XE-device-hardware-oper:device-hardware-data',
    'Cisco-IOS-XE-interfaces-oper:interfaces'
]


def get_device_details(mgmt_ip, yang_model):
    try:
        headers = {'Accept': 'application/yang-data+json'}
        data = requests.get(
            f'https://{mgmt_ip}/{base_url}/{yang_model}',
            headers=headers,
            auth=('svc_netadmin', 'Plum789!'),
            verify=False,
            timeout=3
        )
        if data.status_code == requests.codes.ok:
            return data.json()
    except Exception as error:
        return str(error)


for yang_model in yang_models:
    print(get_device_details('153.92.46.1', yang_model))
