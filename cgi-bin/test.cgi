#!/bin/bash

# web interface to run polling scripts for testing

eval $QUERY_STRING


echo 'Content-type: text/html'
echo ''
echo '<html>'
echo '<body bgcolor="white">'
echo '<center>'
echo '<hr width="100%">'
echo '</center>'
echo '<pre>'
var1=$(/var/www/cgi-bin/pollftp.py $site)
echo $var1
echo '<br>'
echo '<br>'
var2=$(/var/www/cgi-bin/pollxml.py $site)
echo $var2
echo '<h1>Test Completed!</h1>'
echo '<br>'
echo '<br>'
echo '<a href="/index.html">Return to Homepage</a>'
echo '</pre>'
echo '<center>'
echo '<hr width="100%">'
echo '</center>'
echo '</body>'
echo '</html>'
