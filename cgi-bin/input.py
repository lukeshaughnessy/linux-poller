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

    pollList = ( (SITE_NAME, IP_ADDRESS, COMMUNITY_NAME, SNMP_PORT, POLL_FREQ, FTP_FREQ, FTP_USER, FTP_PASS, IMG_DIR, POLLING_ENABLE, FTP_ENABLE, OBS_SCALAR), )
    
    return pollList

    

def inputDb(pollList):
    '''Attach to DB and input data'''
    
    s = pollList[0]
    siteName = s[0]
    
    con = None

    try:

        con = psycopg2.connect(database='pollconfdb', user='vmuser')

        cur = con.cursor()
       
        #check for existing site information and delete if present
        cur.execute ('DELETE FROM pollers WHERE site_name = %s', (siteName,))  
    
        query = "INSERT INTO pollers (site_name, ip_address, community_name, snmp_port, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.executemany(query, pollList)

        con.commit()
  
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

    
    finally:
    
       if con:
           con.close()



def schedule(pollList):
    '''Write Crontab entries'''

    #add crontab entry and overwrite if existing (https://pypi.python.org/pypi/python-crontab/1.7.2)
    
    #match_* lines check for non-numeric chars to test for crontab or increment input from user-
    # ie "*" is non-numeric and would mean a crontab style entry

    l = pollList[0]
    SITE_NAME = l[0]
    POLL_FREQ = l[4]
    FTP_FREQ = l[5]
    POLLING_ENABLE = l[9]
    FTP_ENABLE = l[10]
    

    match_xml = re.search("\D", POLL_FREQ)
    match_ftp = re.search("\D", FTP_FREQ)


    pollcmd = 'cd /tmp; /tmp/pollxml.py ' + SITE_NAME + ' >> /var/log/vmuser/xml_poll.log' + ' #XML Poll'
    ftpcmd = 'cd /tmp; /tmp/pollftp.py ' + SITE_NAME + ' >> /var/log/vmuser/jpg_poll.log' + ' #FTP poll'

    tab = CronTab()
    tab.remove_all(SITE_NAME)


    if POLLING_ENABLE == 'on':
        job_xml = tab.new(pollcmd)

        if match_xml is None:
            job_xml.minute.every(POLL_FREQ)
        else:
            job_xml.setall(POLL_FREQ)
    else:
        job_xml = tab.new(pollcmd)
        job_xml.enable(False)


    if FTP_ENABLE == 'on':
        job_ftp = tab.new(ftpcmd)

        if match_ftp is None:
            job_ftp.minute.every(FTP_FREQ)
        else:
            job_ftp.setall(FTP_FREQ)
    else:
        job_ftp = tab.new(ftpcmd)
        job_ftp.enable(False)

    tab.write()

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
    <tr><th>SiteName</th><th>SiteIP</th><th>CommunityName</th><th>SnmpPort</th><th>PollFrequency</th><th>FTPFrequency</th><th>FTPUser</th><th>FTPPassword</th><th>ImageDir</th><th>FTPEnable</th><th>PollingEnable</th><th>Parameters</th></tr>'''

    con = psycopg2.connect(database='pollconfdb', user='vmuser')

    cur = con.cursor()
    cur.execute('SELECT site_name, ip_address, community_name, snmp_port, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar FROM pollers WHERE site_name = %s' , (SITE_NAME,))

    for (site_name, ip_address, community_name, snmp_port, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar) in cur:
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
        print '<td>', obs_scalar, '</td></tr>'
        print ('</table>')

def main():
    pollList = formData()
    inputDb(pollList)
    schedule(pollList)
    showResult(pollList)
    printout()


main()
 
