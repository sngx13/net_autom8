# net_autom8 - Network Automation & Inventory Portal

### Powered By:
 - Nginx
 - Gunicorn
 - Django
 - Crispy Forms
 - Bootstrap5
 - Datatables
 - Google Charts
 - Scrapli

### Job Scheduling:
Celery & Redis

### Hosted on Raspberry PI
> https://netautom8.servehttp.com/

### How it works
* Inventory
    - Device List
        > Shows a list of devices that have been added to inventory, regadless whether those have been discovered or not.
        > Allows for device re-discovery.
        >> Could be used when device was changed, hostname / IP stayed the same.
    - Add device
        > Adds single device to inventory, initiates SSH connections to obtain basic information (uptime, serial, model)
        > Checks whether RESTCONF is enabled.
    - Import devides
        > Relies of structured CSV file for import.
        > Loops over devices and performs same checks as above (signle device discovery)
