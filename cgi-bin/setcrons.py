#!/usr/bin/python
import cgi
import cgitb
import paramiko
from ConfigParser import SafeConfigParser

cgitb.enable()

print "Content-type: text/html\n\n"

parser = SafeConfigParser() #from conf file
parser.read('conf.ini')
hostlist = parser.get('config', 'hosts')
hosts = hostlist.split(',')
user = parser.get('config', 'user')
password = parser.get('config', 'password')
command_path = parser.get('config', 'command_path')


ssh = paramiko.SSHClient()
for i in hosts:
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(i, username= user, password= password)
    stdin, stdout, stderr = ssh.exec_command(command_path)

    print  str(stdout.readlines())[2:][1:-4] 
    print  str(stderr.readlines())[2:][1:-4] 
    print '<br>'

ssh.close()
print "<h1>Schedule Updated!</h1>"
print '<br>'
print '<br>'
print '<a href="/index.html">Return to Homepage</a>'
