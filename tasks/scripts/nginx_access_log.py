import requests
from ipaddress import ip_address
# Models
from net_autom8.models import ExternalVisitorsInfo


progress = []


def get_nginx_access_hits():
    ip_addr_list = []
    with open('/var/log/nginx/access.log', 'r') as logfile:
        lines = logfile.readlines()
        for line in lines:
            ip_addr = line.split()[0]
            timestamp = line.split()[3].strip('[]').replace('/', '-')
            if ip_address(ip_addr).is_global:
                ip_addr_list.append(ip_addr)
    unique_ip_list = set(list(ip_addr_list))
    for ip in unique_ip_list:
        check_if_ip_in_db = ExternalVisitorsInfo.objects.filter(ip_address=ip)
        if not check_if_ip_in_db:
            progress.append(
                f'[+] Performing check of {ip} against AbuseDB'
            )
            get_geo_info = requests.get(
                f'https://ipqualityscore.com/api/json/ip/IshTioALRMSVm5lXLXrDiwMVWlLkueNB/{ip}'
            )
            if get_geo_info.status_code == 200:
                ip_data = get_geo_info.json()
                external_user_info = ExternalVisitorsInfo(
                    ip_address=ip,
                    hostname=ip_data['host'],
                    provider=ip_data['ISP'],
                    bgp_asn=ip_data['ASN'],
                    city=ip_data['city'],
                    country_code=ip_data['country_code'],
                    recent_abuse=ip_data['recent_abuse'],
                    fraud_score=ip_data['fraud_score']
                )
                print(f'[+] Writing new {ip} to ExternalVisitorsInfoDB')
                external_user_info.save()
            else:
                progress.append(
                    f'[+] Received: HTTP/{get_geo_info.status_code} most likely due to limit being reached'
                )
                return {'status': 'failure', 'details': progress, 'message': 'API Limit was reached'}
        else:
            progress.append(
                f'[+] Following: {ip} is already in ExternalVisitorsInfoDB'
            )
    return {'status': 'success', 'details': progress, 'message': 'Log parsing completed successfully'}