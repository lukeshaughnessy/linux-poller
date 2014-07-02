#!/usr/bin/python
#Connect to DB and get config settings
import psycopg2



def dbgetconfigs(siteArg):
	con = None
	try:

	    con = psycopg2.connect(database='pollconfdb', user='vmuser')
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
        return configs

