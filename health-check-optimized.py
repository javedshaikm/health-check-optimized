from __future__ import print_function
from netmiko import ConnectHandler
import pandas as pd
import smtplib
import sys
import time
import select
import paramiko
import re
from io import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


username = 'cisco'
password = 'cisco'

interfaces = {'10.0.10.100':['Ethernet0/0','Ethernet1/0'],
'10.0.10.101':['FastEthernet0/0','FastEthernet0/1']}
platform = 'cisco_ios'


def send_mail(status=''):
    fromaddr = "@gmail.com"
    toaddr = "@hotmail.com"
    msg = MIMEMultipart()
    msg['From'] = '@gmail.com'
    msg['To'] = '@hotmail.com'
    msg['Subject'] = "This is Health check"
    msg.attach(MIMEText(status, 'plain'))   
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print("Sending email:\n{status}".format(status=status))
    return

status_for_hosts = []

for key, value in interfaces.items():
    for items in value:
        status_list = []
        connect = ConnectHandler(device_type=platform, ip=key, username=username, password=password)
        output = connect.send_command('terminal length 0', expect_string=r'#')
        output = connect.send_command('enable',expect_string=r'#')
        host_name = connect.send_command('show run | in hostname',expect_string=r'#')                       
        interface_status = connect.send_command(f'show ip int brief',expect_string=r'#')
        old_stdout = sys.stdout
        interface_result = StringIO()
        sys.stdout = interface_result
        sys.stdout = old_stdout
        data = pd.read_fwf(StringIO(interface_status),  widths=[27, 16, 3, 7, 23, 8])
        for index, row in data.iterrows():
            if row[4] == 'administratively down' or row[4] == 'down':
                status_list.append(f"\nInterface {row[0]} is down in {host_name}\n")

        
# Use join() instead of string concatenation
full_status = ''.join(status_list)
status_for_hosts.append(full_status)

send_mail(status='\n'.join(status_for_hosts))
