#!/usr/bin/python
#FTP script to connect to sites and download image files
import sys
from ConfigParser import SafeConfigParser
import os
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
from sets import Set
from ftplib import FTP
import datetime
import argparse
import psycopg2


parser = SafeConfigParser()
parser.read('conf.ini')


def pollname():
    '''Get sitename as argument to command from CLI'''
    argp = argparse.ArgumentParser()
    argp.add_argument("site", help="runs a JPG poll using the sitename as an argument")
    args = argp.parse_args()
    siteArg = args.site
    return siteArg

def gettime():
    '''get the time and format it'''
    utc_datetime = datetime.datetime.utcnow()
    timeStamp = utc_datetime.strftime("%Y%m%dT%H%M%S")
    return timeStamp

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



def moveFTPFiles(siteArg,timeStamp,serverName,userName,passWord,remotePath,localPath,deleteRemoteFiles=False,onlyDiff=False):
    """Connect to an FTP server and bring down files to a local directory"""


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
    siteArg = pollname()
    timeStamp = gettime()
    configs = dbgetconfigs(siteArg)
    serverName = configs[2]
    userName = configs[7]
    passWord = configs[8]
    remotePath = configs[9]
    localPath = parser.get('config', 'localPath')
    moveFTPFiles(siteArg,timeStamp,serverName,userName,passWord,remotePath,localPath,deleteRemoteFiles=False,onlyDiff=False)

main()



