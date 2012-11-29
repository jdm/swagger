import sys
import sqlite3
from git import *
from collections import defaultdict

try:
    f = open('last_commit', 'rb')
    last_commit = f.read()
    f.close()
except:
    last_commit = None

repo = Repo(sys.argv[1])
assert repo.bare == False

commit_info = defaultdict(lambda: {'name': '', 'commits': 0, 'first_commit': sys.maxint, 'last_commit': 0})

for commit in repo.iter_commits('master'):
    if last_commit and commit.hexsha in last_commit:
        break
    author = commit.author
    commits = commit_info[author.email]['commits']
    commit_info[author.email]['commits'] += 1
    if not commits:
        commit_info[author.email]['name'] = author.name
    if commit.committed_date > commit_info[author.email]['last_commit']:
        commit_info[author.email]['last_commit'] = commit.committed_date
    if commit.committed_date < commit_info[author.email]['first_commit']:
        commit_info[author.email]['first_commit'] = commit.committed_date

conn = sqlite3.connect('committers.db')
c = conn.cursor()

if not last_commit:
    c.execute('''DROP TABLE IF EXISTS committers''')
    c.execute('''CREATE TABLE committers
                 (name text, email text, commits integer, first_commit datetime, last_commit datetime)''')

    records = []
    for email in commit_info:
        info = commit_info[email]
        records.append((info['name'], email, info['commits'], info['first_commit'], info['last_commit']))

    c.executemany('INSERT INTO committers VALUES (?, ?, ?, ?, ?)', records)

else:
    for email in commit_info:
        c.execute('SELECT commits FROM committers WHERE email=?', (email,))
        res = c.fetchone()
        if res:
            c.execute('UPDATE committers SET commits=?, last_commit=? WHERE email=?',
                      (int(res[0]) + commit_info[email]['commits'], commit_info[email]['last_commit'], email))
        else:
            c.execute('INSERT INTO committers VALUES (?, ?, ?, ?, ?)',
                      (commit_info[email]['name'], email, commit_info[email]['commits'],
                       commit_info[email]['first_commit'], commit_info[email]['last_commit']))
            print email

conn.commit()
conn.close()

f = open('last_commit', 'wb')
f.write(repo.commit('master').hexsha)
f.close()
