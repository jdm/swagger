#!/usr/bin/env python

# enable debugging
import cgitb
import cgi
import sys
import time
import sqlite3
cgitb.enable()

print "Content-Type: text/html;charset=utf-8"
print

form = cgi.FieldStorage()
start = int(form.getfirst('start', 0))
end = int(form.getfirst('end', 0))

print '''<!DOCTYPE html>
<html>
<head>
</head>
<body>
  <center>
    <h1>New Contributor Awareness-Raiser</h1>
    <h5><a href="http://github.com/jdm/swagger/">(source)</a></h5>
  </center>
  Date range in which to search (<a href="http://www.onlineconversion.com/unix_time.htm">unix timestamps</a>):
  <form action="index.cgi" method="post">
    <input type="number" name="start" value="%s">
    until
    <input type="number" name="end" value="%s"> (defaults to now) <br><br>
    <input type="submit" value="Show results">
  </form> <br>''' % (str(start) if start else '', str(end) if end else '')

if start:
    if not end:
        end = time.time()
    conn = sqlite3.connect('committers.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM committers WHERE first_commit >= ? AND first_commit <= ?',
                         (start, end)):
        print '''<a href="https://bugzilla.mozilla.org/page.cgi?id=user_activity.html&action=run&who=%s"><img src="bugzilla.gif"></a>
                 <a href="mailto:%s">%s</a> (%s)<br>''' % (row[1], row[1], row[0], row[2])

print '''</body>
</html>'''
