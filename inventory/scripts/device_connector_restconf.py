import requests
import urllib3
from ..models import Device


urllib3.disable_warnings()


def device_get_details_via_rest(device_id):
    host = Device.objects.get(pk=device_id)
    yang_models = [
        # 'Cisco-IOS-XE-native:native',
        # 'Cisco-IOS-XE-platform-software-oper:cisco-platform-software',
        # 'Cisco-IOS-XE-device-hardware-oper:device-hardware-data',
        'Cisco-IOS-XE-interfaces-oper:interfaces'
    ]
    try:
        headers = {'Accept': 'application/yang-data+json'}
        data = requests.get(
            f'https://{host.mgmt_ip}/restconf/data/{yang_models[0]}',
            headers=headers,
            auth=('svc_netadmin', 'Plum789!'),
            verify=False,
            timeout=3
        )
        if data.status_code == requests.codes.ok:
            return data.json()['Cisco-IOS-XE-interfaces-oper:interfaces']
    except Exception as error:
        return str(error)
