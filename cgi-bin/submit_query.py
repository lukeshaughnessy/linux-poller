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
<table border=1>
<tr><th>SiteName</th><th>SiteIP</th><th>CommunityName</th><th>PollFrequency</th><th>FTPFrequency</th><th>FTPUser</th><th>FTPPassword</th><th>ImageDir</th><th>FTPEnable</th><th>PollingEnable</th><th>Parameters</th><th>PollingNode</th></tr>'''

con = psycopg2.connect(database='pollconfdb', user='vmuser')

cur = con.cursor()
cur.execute('SELECT site_name, ip_address, community_name, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar, polling_node FROM pollers WHERE site_name = %s' , (VAR_QUERY,))

for (site_name, ip_address, community_name, poll_freq, ftp_freq, ftp_user, ftp_pass, img_dir, polling_enable, ftp_enable, obs_scalar, polling_node) in cur:
    print '<tr><td>', site_name, '</td>'
    print '<td>', ip_address, '</td>'
    print '<td>', community_name, '</td>'
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
print ('</body>')
print ('</html>')
cur.close()
con.close()   
print '<br><br>'
print '<a href="/index.html">Return to Homepage</a>'

