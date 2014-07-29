#!/usr/bin/python
# -*- coding: utf-8 -*-

#web interface to submit query to DB

import cgi
import cgitb
import psycopg2
import sys
import os


cgitb.enable()

print "Content-type: text/html\n\n"

form=cgi.FieldStorage()


if "update" not in form:
    print "<h1>The text input box was empty.</h1>"
else:
    text=form["update"].value
    UPDATE=cgi.escape(text)
	
	
con = None

try:

    con = psycopg2.connect(database='pollconfdb', user='vmuser')

    cur = con.cursor()
    cur.execute(UPDATE)
    con.commit()


except psycopg2.DatabaseError, e:

    if con:
        con.rollback()

    print 'Error %s' % e
    sys.exit(1)


finally:

    if con:
        con.close()
print "<h1>Database Updated!</h1>"
print '<br>'
print '<br>'
print '<a href="/index.html">Return to Homepage</a>'
