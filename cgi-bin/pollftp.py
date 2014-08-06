#!/usr/bin/python
#FTP script to connect to sites and download image files
import sys
from ConfigParser import SafeConfigParser
import os
import random
import warnings
from sets import Set
from ftplib import FTP
import datetime
import time
import argparse
import psycopg2

#ignore warning for "set" module, it's not used by default anyway since onlyDiff is False (in moveFTPFiles function below)
warnings.simplefilter("ignore", DeprecationWarning)

#read configs in from conf.ini file
parser = SafeConfigParser()
parser.read('conf.ini')
db = parser.get('config', 'db')
dbUser = parser.get('config', 'dbUser')
localPath = parser.get('config', 'localPath')

def pollname():
    '''Get command argument (name of site) and check for correct usage'''
    argp = argparse.ArgumentParser()
    argp.add_argument("site", help="runs a JPG poll using the sitename as an argument")
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

def gettime():
    '''get the time and format it'''
    utc_datetime = datetime.datetime.utcnow()
    timeStamp = utc_datetime.strftime("%Y%m%dT%H%M%S")
    return timeStamp

def dbgetconfigs(siteArg):
    '''Get configuration settings from the db'''
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
    #"configs" is now a tuple with all the configuation params
    return configs   



def moveFTPFiles(configs,timeStamp,localPath,siteArg,deleteRemoteFiles=False,onlyDiff=False):
    """Connect to an FTP server and bring down files to a local directory"""
    
    serverName = configs[2]
    userName = configs[7]
    passWord = configs[8]
    remotePath = configs[9]
    
    try:
        ftp = FTP(serverName)
        ftp.set_pasv(False)
    except:
        print "Couldn't find server"
    ftp.login(userName,passWord)
    ftp.cwd(remotePath)
    
    try:
        print "Connecting..."
        if onlyDiff:
            lFileSet = Set(os.listdir(localPath))
            rFileSet = Set(ftp.nlst())
            transferList = list(rFileSet - lFileSet)
            print "Missing: " + str(len(transferList))
        else:
        
        #matches jpg files to be downloaded- there must be some better way of globbing in python... *.jpg would be nice 
            tList = ftp.nlst()
            transferList = []
            for i in tList:
                if i.endswith('.jpg'):
                    transferList.append(i)
    
        delMsg = "" 
        filesMoved = 0
        for fl in transferList:
            # create a full local filepath
            localFile = localPath + fl
            grabFile = True
            if grabFile:                
                #open a the local file
                fileObj = open(localFile, 'wb')
                # Download the file a chunk at a time using RETR
                ftp.retrbinary('RETR ' + fl, fileObj.write)
                # Close the file
                fileObj.close()
                filesMoved += 1
                 
            # Delete the remote file if requested
            if deleteRemoteFiles:
                ftp.delete(fl)
                delMsg = " and Deleted"
    
        print siteArg
        print "Files Moved" + delMsg + ": " + str(filesMoved) +  " on " + timeStamp
        print transferList 
        print "--------------------------"

    except:   
       print "Connection Error - " + timeStamp
    ftp.close() # Close FTP connection
    ftp = None
 
 


def main():
    '''Get various parameters from DB (user, password, etc) and run the FTP download'''
    siteArg, staggerOn = pollname()
    staggerpolls(staggerOn)
    timeStamp = gettime()
    configs = dbgetconfigs(siteArg)
    moveFTPFiles(configs,timeStamp,localPath,siteArg,deleteRemoteFiles=False,onlyDiff=False)

main()