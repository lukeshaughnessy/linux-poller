#!/usr/bin/python
import psycopg2
from crontab import CronTab
import re
import sys
import os
import subprocess
import platform
from ConfigParser import SafeConfigParser


parser = SafeConfigParser() #read in from conf file
parser.read('conf.ini')
db = parser.get('config', 'db')
dbUser = parser.get('config', 'dbUser')
dbHost = parser.get('config', 'dbHost')

hostName = platform.node()

#connect to database
def dbGetconfigs():
    try:
        con = psycopg2.connect(database= db, user= dbUser, host= dbHost)
        cur = con.cursor()
        cur.execute("""SELECT * from pollers""")
        configs = cur.fetchall()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)


    finally:

        if con:
            con.close()

    return configs


#get info from db
def writeCron(configs):

    subprocess.call(["crontab", "-r"])

    for row in configs:
        SITE_NAME = row[1]
        POLL_FREQ = row[5]
        FTP_FREQ  = row[6]
        POLLING_ENABLE = row[10]
        FTP_ENABLE = row[11] 
        POLLING_NODE = row[13]

        hostName = platform.node()

        if POLLING_NODE == hostName:      

            match_xml = re.search("\D", POLL_FREQ)
            match_ftp = re.search("\D", FTP_FREQ)

            pollcmd = 'cd /home/vmuser; /home/vmuser/pollxml.py ' + SITE_NAME + ' >> /var/log/vmuser/xml_poll.log' + ' #XML Poll'
            ftpcmd = 'cd /home/vmuser; /home/vmuser/pollftp.py ' + SITE_NAME + ' >> /var/log/vmuser/jpg_poll.log' + ' #FTP poll'

            tab = CronTab()

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


def main():
    configs = dbGetconfigs()
    writeCron(configs)


main()

print 'Update completed for ' + hostName
