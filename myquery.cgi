#!/usr/bin/env python

# enable debugging
import cgitb
import cgi
import sys
import time
import sqlite3
from datetime import datetime, timedelta, date, timedelta, time
cgitb.enable()

form = cgi.FieldStorage()
user = form.getfirst('user', '')

conn = sqlite3.connect('timeline.db')
c = conn.cursor()

query = "SELECT uid FROM users WHERE email LIKE ?"
c.execute(query, (user,))
uid = int(c.fetchone()[0])

events = []
types = ['Bugzilla activity', 'mozilla-central commits', 'mozilla-central pushes',
         'Bugzilla triage', 'Bugzilla QA', 'Bugzilla crashstats']

query = 'SELECT type, happened, amount FROM activity WHERE uid=?'
c.execute(query, (uid,))
for (act_type, when, amount) in c.fetchall():
    events += [{'title': types[act_type], 'desc': amount, 'when': when}]

c.close()

print "Content-Type: application/json;charset=utf-8"
print
print '{'
print '"dateTimeFormat": "iso8601",'
print '"events": [',
for i in xrange(0, len(events)):
    print '{"start": "%s", "durationEvent": false, "description": "%s", "title": "%s"}' % (events[i]['when'], events[i]['desc'], events[i]['title'])
    if i < len(events) - 1:
        print ',',
print ']}'

