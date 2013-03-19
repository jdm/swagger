import sys
import sqlite3
import mysql.connector
from git import *
from datetime import datetime, date
from collections import defaultdict

update_commits = True
args = sys.argv[1:]
if args[0] == '--no-commits':
    update_commits = False
    args.pop()

email = args.pop()

records = []

types = ['bugzilla general', 'mozilla-central commit', 'mozilla-central push',
         'bugzilla triage', 'bugzilla qa', 'bugzilla crashstats']

print 'Digging through Bugzilla data...'

cnx = mysql.connector.connect(user='jdm', password='',
                              host='127.0.0.1',
                              database='bmo')
cursor = cnx.cursor()

bmo_activity = defaultdict(lambda: defaultdict(int))

query = "SELECT userid, realname FROM profiles WHERE login_name LIKE %s"
cursor.execute(query, (email,))
(user, name) = cursor.fetchone()

def getSingleColumnResult(table, resultcolumn, comparecolumn, param, cursor):
    query = "SELECT " + resultcolumn + " FROM " + table + " WHERE " + comparecolumn + " LIKE %s"
    cursor.execute(query, (param,))
    return cursor.fetchone()[0]

def getFieldId(name, cursor):
    return getSingleColumnResult('fielddefs', 'id', 'name', name, cursor)

cc_field = getFieldId("cc", cursor)
crash_field = getFieldId("cf_crash_signature", cursor)
component_field = getFieldId("component", cursor)
product_field = getFieldId("product", cursor)
status_field = getFieldId("bug_status", cursor)

def getProductId(name, cursor):
    return getSingleColumnResult('products', 'id', 'name', name, cursor)
def getComponentId(name, product, cursor):
    query = "SELECT id FROM components WHERE name LIKE %s AND product_id = %s"
    cursor.execute(query, (name, product))
    return cursor.fetchone()[0]
#def getStatusId(name, cursor):
#    return getSingleColumnResult('bug_status', 'id', 'value', name, cursor)

#ff_product = getProductId('Firefox', cursor)
#untriaged_component = getComponentId('Untriaged', ff_product, cursor)

#verified_status = getStatusId('VERIFIED', cursor)

# Find all field changes that aren't CC-related
query = "SELECT bug_when, fieldid, removed, added, comment_id FROM bugs_activity WHERE who=%s AND attach_id IS NULL AND fieldid != %s"
cursor.execute(query, (user, cc_field))
for (bug_when, fieldid, removed, added, comment_id) in cursor:
    if fieldid == crash_field:
        act_type = "bugzilla crashstats"
    elif fieldid == component_field and removed == "Untriaged":
        act_type = "bugzilla triage"
    elif fieldid == status_field and added == "VERIFIED":
        act_type = "bugzilla qa"
    else:
        act_type = "bugzilla general"        

    bmo_activity[str(bug_when.year) + "-" + str(bug_when.month)][act_type] += 1;

    # When an action is taken along with the comment, we want to avoid counting that
    # as twice as much activity, so we cause the comment not to be counted.
    if comment_id != "NULL":
        bmo_activity[str(bug_when.year) + "-" + str(bug_when.month)]["bugzilla general"] -= 1;

# Find all comments
query = "SELECT bug_when FROM longdescs WHERE who=%s"
cursor.execute(query, (user,))
for (bug_when,) in cursor:
    bmo_activity[str(bug_when.year) + "-" + str(bug_when.month)]["bugzilla general"] += 1;

cnx.close()

if update_commits:
    print 'Digging through mozilla-central data...'

    repo = Repo(args.pop())
    assert repo.bare == False

    for commit in repo.iter_commits('master'):
        if commit.author.email != email:
            continue
        dateval = datetime.fromtimestamp(commit.committed_date)
        bmo_activity[str(dateval.year) + "-" + str(dateval.month)]["mozilla-central commit"] += 1

print 'Postprocessing the data...'

for yearmonth in bmo_activity:
    values = map(lambda x: int(x), yearmonth.split('-'))
    dateval = date(values[0], values[1], 28)
    for activity_type in bmo_activity[yearmonth]:
        records += [(types.index(activity_type),
                     dateval.isoformat(),
                     bmo_activity[yearmonth][activity_type])]

print 'Populating timeline database...'

conn = sqlite3.connect('timeline.db')
c = conn.cursor()

query = "CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY, name VARCHAR(50) NOT NULL, email VARCHAR(50) UNIQUE NOT NULL)";
c.execute(query);

query = "CREATE TABLE IF NOT EXISTS activity(aid INTEGER PRIMARY KEY, uid INTEGER, type INTEGER, happened TEXT NOT NULL, amount INTEGER)"
c.execute(query)

query = "SELECT uid FROM users WHERE email LIKE ?"
c.execute(query, (email,))
try:
    uid = int(c.fetchone()[0])
except:
    query = "INSERT INTO users(uid, email, name) VALUES(NULL, ?, ?)"
    c.execute(query, (email, name))
    uid = c.lastrowid

if update_commits:
    query = 'DELETE FROM activity WHERE uid=?'
else:
    query = 'DELETE FROM activity WHERE uid=? AND type != ?'
c.execute(query, (uid, types.index('mozilla-central commit')))

query = 'INSERT INTO activity(aid, uid, type, happened, amount) VALUES (NULL, ?, ?, ?, ?)'
c.executemany(query, map(lambda x: (uid, x[0], x[1], x[2]), records))

conn.commit()
conn.close()

print 'Done'
