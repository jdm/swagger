#!/usr/bin/env python

# enable debugging
import cgitb
import cgi
import sys
import time
import sqlite3
from datetime import datetime, timedelta, date, timedelta, time
cgitb.enable()

today = datetime.now()

form = cgi.FieldStorage()
start = form.getfirst('start', '2011-01')
end = form.getfirst('end', '%s-%s' % (str(today.year), str(today.month)))

conn = sqlite3.connect('committers.db')
c = conn.cursor()

def next_month(d):
    new = None
    try:
        new = d.replace(month=d.month + 1)
    except:
        if d.month == 12:
            new = d.replace(year=d.year + 1, month=1)
    return new

def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = datetime.combine(date=dt, time=time(0,0,0)) - epoch
    return delta.total_seconds()

start_date = date(int(start.split('-')[0]), int(start.split('-')[1]), 1)
end_date = next_month(date(int(end.split('-')[0]), int(end.split('-')[1]), 1))

conn = sqlite3.connect('committers.db')
c = conn.cursor()

data = []
d = start_date
while d < end_date:
    c.execute('SELECT COUNT(*) FROM committers WHERE first_commit >= ? AND first_commit <= ?',
              (unix_time(d), unix_time(next_month(d))))
    data.append(int(c.fetchone()[0]))
    d = next_month(d) 

c.close()

print "Content-Type: application/json;charset=utf-8"
print
print '[',
for i in xrange(0, len(data)):
    print data[i],
    if i < len(data) - 1:
        print ',',
print ']'

