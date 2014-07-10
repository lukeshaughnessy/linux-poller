#!/usr/bin/python
# -*- coding: utf-8 -*-


from crontab import CronTab
import cgi
import cgitb
import psycopg2
import sys
import os
import subprocess
import re
import paramiko
from ConfigParser import SafeConfigParser

parser = SafeConfigParser() #from conf file
parser.read('conf.ini')
dbUser = parser.get('config', 'dbUser')
db = parser.get('config', 'db')
hostlist = parser.get('config', 'hosts')
hosts = hostlist.split(',')


def formData():
    '''Get user input from webpage.'''
    cgitb.enable()

    print "Content-type: text/html\n\n"

    form=cgi.FieldStorage()

    if "site_name" not in form:
        print "<h1>The text input box was empty.</h1>"
    else:
        SITE_NAME = form.getvalue('site_name')
        SITE_NAME = SITE_NAME.strip()

    if "ip_address" not in form:
        print "<h1>The text input box was empty.</h1>"
    else:
        IP_ADDRESS= form.getvalue('ip_address')
        IP_ADDRESS = IP_ADDRESS.strip()

    if "community_name" not in form:
        print "<h1>The text input box was empty.</h1>"
    else:
        COMMUNITY_NAME = form.getvalue('community_name')
        COMMUNITY_NAME = COMMUNITY_NAME.strip()

    if "snmp_port" not in form:
        print "<h1>The text input box was empty.</h1>"
    else:
        SNMP_PORT = form.getvalue('snmp_port')
        SNMP_PORT = SNMP_PORT.strip()


    if "poll_freq" not in form:
        print "<h1>The text input box was empty.</h1>"
    else:
        POLL_FREQ = form.getvalue('poll_freq')
        POLL_FREQ = POLL_FREQ.strip()

    FTP_FREQ = form.getvalue('ftp_freq')
    FTP_FREQ = FTP_FREQ.strip()

    FTP_USER = form.getvalue('ftp_user')

    FTP_PASS = form.getvalue('ftp_pass')

    IMG_DIR = form.getvalue('img_dir')

    POLLING_ENABLE = form.getvalue('poll_enable')

    FTP_ENABLE = form.getvalue('ftp_enable')

    OBS_SCALAR = form.getlist('obs')

    POLLING_NODE = form.getvalue('polling_node')
    POLLING_NODE = POLLING_NODE.strip()

    pollList = ( (SITE_NAME, IP_ADDRESS, COMMUNITY_NAME, SNMP_PORT, POLL_FREQ, FTP_FREQ, FTP_USER, FTP_PASS, IMG_DIR, POLLING_ENABLE, FTP_ENABLE, OBS_SCALAR, POLLING_NODE), )
    
    return pollList

    

def inputDb(pollList):
    '''Attach to DB and input data'''
    
    s = pollList[0]
    siteName = s[0]
    
    con = None

    try:

        con = psycopg2.connect(database= db, user= dbUser)

        cur = con.cursor()
       
        #check for existing site information and delete if present
        cur.execute ('DELETE FROM pollers WHERE site_name = %s', (siteName,))  
    
        query = "INSERT INTO pollers (site_name, ip_address, community_name, snmp_port, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar, polling_node) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.executemany(query, pollList)

        con.commit()
  
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

    
    finally:
    
       if con:
           con.close()


def setCrons():
    ssh = paramiko.SSHClient()
    for i in hosts:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(i, username='vmuser', password='password')
        stdin, stdout, stderr = ssh.exec_command('/home/vmuser/setcrons.py')

    #print stdout.readlines()
    #print stderr.readlines()
        ssh.close()



def printout():
    print "<h2>Site Info Has Been Submitted!</h2>"
    print '<br>'
    print '<br>'
    print '<a href="/index.html">Return to Homepage</a>'

def showResult(pollList):

    l = pollList[0]
    SITE_NAME = l[0]


    print '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>Results</title>
    </head>
    <body>
    <h2>Results</h2>
    <table border=1>
    <tr><th>SiteName</th><th>SiteIP</th><th>CommunityName</th><th>SnmpPort</th><th>PollFrequency</th><th>FTPFrequency</th><th>FTPUser</th><th>FTPPassword</th><th>ImageDir</th><th>FTPEnable</th><th>PollingEnable</th><th>Parameters</th><th>PollingNode</th></tr>'''

    con = psycopg2.connect(database= db, user= dbUser)

    cur = con.cursor()
    cur.execute('SELECT site_name, ip_address, community_name, snmp_port, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar, polling_node FROM pollers WHERE site_name = %s' , (SITE_NAME,))

    for (site_name, ip_address, community_name, snmp_port, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar, polling_node) in cur:
        print '<tr><td>', site_name, '</td>'
        print '<td>', ip_address, '</td>'
        print '<td>', community_name, '</td>'
        print '<td>', snmp_port, '</td>'
        print '<td>', poll_freq, '</td>'
        print '<td>', ftp_freq, '</td>'
        print '<td>', ftp_user, '</td>'
        print '<td>', ftp_pass, '</td>'
        print '<td>', img_dir, '</td>'
        print '<td>', ftp_enable, '</td>'
        print '<td>', polling_enable, '</td>'
        print '<td>', obs_scalar, '</td>'
        print '<td>', polling_node, '</td></tr>'
        print ('</table>')

def main():
    pollList = formData()
    inputDb(pollList)
    setCrons()
    showResult(pollList)
    printout()


main()
 
