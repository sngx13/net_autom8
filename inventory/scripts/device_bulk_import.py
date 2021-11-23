import pandas as pd
from django.utils import timezone
from random import randint
from inventory.models import Device


def inventory_importer(file):
    try:
        data = []
        add_random_number = randint(100, 1000)
        uploaded_file = f'uploaded_files/imported_file_{add_random_number}.csv'
        with open(uploaded_file, 'wb+') as csv_file:
            for chunk in file.chunks():
                csv_file.write(chunk)
        df = pd.read_csv(uploaded_file, sep=',')
        for i in range(len(df)):
            data.append(
                Device(
                    hostname=df.iloc[i][0],
                    mgmt_ip=df.iloc[i][1],
                    vendor=df.iloc[i][2],
                    date_added=timezone.now()
                )
            )
        Device.objects.bulk_create(data)
        return {
            'status': 'success',
            'message': 'CSV file imported successfully!'
        }
    except Exception as error:
        return {
            'status': 'fail',
            'message': str(error)
        }
