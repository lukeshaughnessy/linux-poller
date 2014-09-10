#!/usr/bin/python
# -*- coding: utf-8 -*-

#generate webpage showing site config params

import cgi
import cgitb
import psycopg2
import sys
import os

cgitb.enable()

print "Content-type: text/html\n\n"

form=cgi.FieldStorage()
if "query" not in form:
    print "<h1>The text input box was empty.</h1>"
else:
    text=form["query"].value
    VAR_QUERY=cgi.escape(text)
print '''
<!DOCTYPE html>
<html>
<head>
<title>Results</title>
</head>
<body>
<h2>Results</h2>
'''

con = psycopg2.connect(database='pollconfdb', user='vmuser')

cur = con.cursor()
cur.execute('SELECT obs_xml FROM xmldata WHERE site_name= %s ORDER BY write_time DESC LIMIT 1' , (VAR_QUERY,))
cur.fetchone()
print '<table>'

for row in cur:
    print '<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(col) for col in row]))

print '</table>'
print ('</html>')
cur.close()
con.close()   
print '<br><br>'
print '<a href="/index.html">Return to Homepage</a>'

