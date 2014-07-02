#!/usr/bin/python
# -*- coding: utf-8 -*-
import psycopg2
import datetime
import subprocess
from ConfigParser import SafeConfigParser
from lxml import etree
import argparse



def gettime():
    '''get the time and format it'''
    utc_datetime = datetime.datetime.utcnow()
    timeStamp = utc_datetime.strftime("%Y%m%dT%H%M%S")
    return timeStamp


def pollname():
    '''Get command argument (name of site) and check for corrent usage'''
    argp = argparse.ArgumentParser()
    argp.add_argument("site", help="Runs an XML poll using the sitename as an argument")
    args = argp.parse_args()
    siteArg = args.site
    return siteArg

def dbgetconfigs(siteArg):
    '''Get configuration settings from the db'''
    parser = SafeConfigParser() #read in from conf file
    parser.read('conf.ini')
    db = parser.get('config', 'db')
    dbUser = parser.get('config', 'dbUser')

    con = None
    try:

        con = psycopg2.connect(database = db, user = dbUser)
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
    return configs   #configs is now a tuple (immutable list if you must know) with all the configuation params




def snmpget(configs):
    '''run snmpget shell command to get site obs data'''
    parser = SafeConfigParser() #again getting from conf file
    parser.read('conf.ini')
    tryTimes = parser.get('config', 'tryTimes')
    tryTimes = int(tryTimes)

    communName = configs[3] #these are coming from the configs tuple created earlier
    ipAddr = configs[2]
    snmpPort = configs[4]
    hostPort = ipAddr+':'+snmpPort 
    obsList = configs[12]

    #call shell command and get exit status; if 0 (success), break. If not 0, try x times as set by tryTimes. 
    for i in range(tryTimes):
        p = subprocess.Popen(["/usr/bin/snmpget", "-Oqse", "-v2c",  "-m", "all", "-c", communName, hostPort] + obsList, stdout=subprocess.PIPE)
        output, err = p.communicate()
        rc = p.returncode
        if rc == 0:
            break

    array = output.splitlines() # gets the list of readings and puts them into an array
    return array



def xmlwrite(configs, array, timeStamp): # using 'lxml' python lib for this, see http://lxml.de/tutorial.html
    '''format XML and write to file'''
    parser = SafeConfigParser() #from conf file
    parser.read('conf.ini')
    xmlPath = parser.get('config', 'xmlPath')
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

    parser = SafeConfigParser() #from conf file
    parser.read('conf.ini')
    db = parser.get('config', 'db')
    dbUser = parser.get('config', 'dbUser')
    
    inputList = (
        (siteName, obsData),
    )

    con = None

    try:

        con = psycopg2.connect(database = db, user = dbUser)

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
    siteArg = pollname()
    timeStamp = gettime()
    configs = dbgetconfigs(siteArg)
    array = snmpget(configs)
    obsData = xmlwrite(configs, array, timeStamp)
    xmlstore(configs, obsData, timeStamp)

main()


