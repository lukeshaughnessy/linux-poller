#!/usr/bin/python
# -*- coding: utf-8 -*-
#Polling script to connect to site, get obs data and set rpu time.

import psycopg2
import datetime
import time
import random
import subprocess
from ConfigParser import SafeConfigParser
from lxml import etree
import argparse

#read configs in from conf.ini file
parser = SafeConfigParser() #from conf file
parser.read('conf.ini')
db = parser.get('config', 'db')
dbUser = parser.get('config', 'dbUser')
dbHost = parser.get('config', 'dbHost')
tryTimes = int(parser.get('config', 'tryTimes'))
xmlPath = parser.get('config', 'xmlPath')



def gettime():
    '''get the time and format it'''
    utc_datetime = datetime.datetime.utcnow()
    timeStamp = utc_datetime.strftime("%Y%m%dT%H%M%S")
    return timeStamp


def pollname():
    '''Get command argument (name of site) and check for correct usage'''
    argp = argparse.ArgumentParser()
    argp.add_argument("site", help="Runs an XML poll using the sitename as an argument")
    argp.add_argument("-s", "--stagger", action="store_true", help="Introduces a randomized delay to poller script")
    args = argp.parse_args()
    
    #this is the sitename in the command, e.g. "pollftp.py hwy20" where "hwy20" is the sitename
    siteArg = args.site
    
    #check for -s or --stagger arg
    if args.stagger:
        staggerOn = 1
    else:
        staggerOn = 0
    return (siteArg, staggerOn)

def staggerpolls(staggerOn):
    '''Set optional random delay to execute script'''
    if staggerOn == 1:
        delayTime = random.randrange(0,30)
        time.sleep(delayTime)

def dbgetconfigs(siteArg):
    '''Get configuration settings from the db'''

    con = None
    try:

        con = psycopg2.connect(database= db, user= dbUser, host= dbHost)
        cur = con.cursor()
        cur.execute('SELECT * FROM pollers WHERE site_name= %s' , (siteArg,))

        while True:

            row = cur.fetchone()
            if row == None:
                break
            configs = row

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(1)


    finally:

        if con:
            con.close()
    return configs   #configs is now a tuple with all the configuration params




def snmpget(configs):
    '''run snmp shell commands to get site obs data and set the time'''

    communName = configs[3] #these are coming from the configs tuple created earlier
    ipAddr = configs[2]
    snmpPort = configs[4]
    hostPort = ipAddr+':'+snmpPort 
    obsList = configs[12]
    
    epochTime = str(int(time.time()))

    #call shell command and get exit status; if 0 (success), break. If not 0, try x times as set by tryTimes. 
    for i in range(tryTimes):
        p = subprocess.Popen(["/usr/bin/snmpget", "-Oqse", "-v2c",  "-m", "all", "-c", communName, hostPort] + obsList, stdout=subprocess.PIPE)
        output, err = p.communicate()
        rc = p.returncode
        if rc == 0:
            break

    #set time on RPU
    q = subprocess.Popen(["/usr/bin/snmpset", "-m", "GLOBAL", "-Oqse", "-v2c", "-c", communName, hostPort, "globalTime.0", "=", epochTime], stdout=subprocess.PIPE)
    output, err = q.communicate()

    # gets the list of readings and puts them into an array
    array = output.splitlines()
    return array

    

def xmlwrite(configs, array, timeStamp): # using 'lxml' python lib for this, see http://lxml.de/tutorial.html
    '''format XML and write to file'''
    siteName = configs[1]
    fileName = xmlPath + siteName + '-obs_' + timeStamp + '.xml'

    obs=etree.Element('observation', xmlns='http://www.vaisala.com/iceTrafficMsg')
    ins=etree.SubElement(obs, 'instance')
    tar=etree.SubElement(ins, 'target')
    na=etree.SubElement(tar, 'name')
    na.text = siteName
    res=etree.SubElement(ins, 'resultOf', timestamp=timeStamp, codeSpace='NTCIP')

    #loop through the array to put all the readings into "<value>" tags
    for i in array:
        string1 = i.split(' ')[0]
        string2 = i.split(' ')[1]
        val=etree.SubElement(ins, 'value', code=string1)
        val.text = string2

    with open(fileName,'w') as f:
        f.write( '<?xml version="1.0" encoding="utf-8" ?>\n' )
        f.write(etree.tostring(obs,pretty_print=True))

    heading = '<?xml version="1.0" encoding="utf-8" ?>\n'   
    obsData = (etree.tostring(obs,pretty_print=True))
    obsData = heading + obsData
    print 'XML file for site written: ' + siteName +' '+timeStamp 
    return obsData


def xmlstore(configs, obsData, timeStamp):
    '''stores xml obs files to db'''
    obsData = obsData
    siteName = configs[1]

    
    inputList = (
        (siteName, obsData),
    )

    con = None

    try:

        con = psycopg2.connect(database= db, user= dbUser, host= dbHost)
        cur = con.cursor()

        #cur.execute("INSERT INTO xmldata VALUES (%s)", (siteName))
        query = "INSERT INTO xmldata(site_name, obs_xml)VALUES(%s, %s)"
        cur.executemany(query, inputList)
        con.commit()
  
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

    
    finally:
    
        if con:
            con.close()
    print 'XML file stored to database: ' + siteName +' '+ timeStamp

def main():
    siteArg, staggerOn = pollname()
    timeStamp = gettime()
    staggerpolls(staggerOn)
    configs = dbgetconfigs(siteArg)
    array = snmpget(configs)
    obsData = xmlwrite(configs, array, timeStamp)
    xmlstore(configs, obsData, timeStamp)

main()


