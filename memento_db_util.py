#!/bin/env python
# -*- coding: utf-8 -*-

# Utility for tweaking the database used by the Android app Memento Database.
# E. Woudenberg, Melbourne, Autumn 2013

# Notes: I can recommend sqlitebrowser for perusing the memento.db
# file: http://sourceforge.net/projects/sqlitebrowser/

import sqlite3 as lite
import sys
import uuid
import os
import time

def usage():
    print '''usage: mementoutil.py [-d <memento_sqlite.db>] command [args]
Options:
    -d <sqlite file>      ; default 'memento.db'
Commands:
    libs                  ; list libraries in memento db.
    fields <lib>          ; list fields in given lib.
    emptytrash <lib>      ; delete 'removed' items.
    content <lib> <field> ; list all content entries for a field.
    preload <lib> <field> <file> ; add contents of file to field, one entry per line.
                          ; (use - for stdin)
'''
    sys.exit(1)

def main():
    args = sys.argv
    database = 'memento.db'
    if len(args) > 3 and args[1] == '-d':
        database = args[2]
        del args[1:3]
    if len(args) < 2:
        usage()
    opendb(database)
    cmd = args[1]
    if cmd == 'libs': listlibs()
    elif cmd == 'fields': listfields(args[2])
    elif cmd == 'emptytrash': emptytrash(args[2])
    elif cmd == 'showtrash': showtrash(args[2])
    elif cmd == 'content': listcontent(args[2], args[3])
    elif cmd == 'preload': preload(args[2], args[3], args[4])
    else:
        usage()

def preload(lib, field, filename):
    lines = (sys.stdin if filename == '-' else open(filename, 'rb')).readlines()
    libuid = getlib(lib)
    fielduid = getfield(lib, field)
    itemuid = '%s' % uuid.uuid4()
    timestamp = int(time.time())
    Cur.execute('''Insert into tbl_library_item (uuid, lib_uuid, removed, creation_date, removed_time, view_time, favorite, edit_time)
        values (?,?,?,?,?,?,?,?)''',
                (itemuid, libuid, 1, timestamp, timestamp, timestamp, 0, 0))
    for i in lines:
        i = i.strip()
        uid = '%s' % uuid.uuid4()
        Cur.execute('''Insert into tbl_flex_content (uuid, stringcontent, owneruuid, templateuuid)
        values (?, ?, ?, ?)''', (uid, i, itemuid, fielduid))
    Con.commit()

    
def listcontent(lib, field):
    fielduid = getfield(lib, field)
    Cur.execute('''SELECT stringcontent,realcontent,intcontent from tbl_flex_content
        where templateuuid = ?''', (fielduid,))
    for i in Cur.fetchall():
        for j,t in zip(i, ['s','r','i']):
            if j: print t, j,
        print
    

def showtrash(lib):
    libuid = getlib(lib)
    Cur.execute('Select uuid from tbl_library_item where lib_uuid = ? and removed = 1', (libuid,))
    for i in Cur.fetchall():
        print '\n--------------Owner', i[0]
        owner = i[0]
        Cur.execute('Select uuid, stringcontent from tbl_flex_content where owneruuid = ?', (owner,))
        for j in Cur.fetchall():
            print j[0], j[1]

def emptytrash(lib):
    libuid = getlib(lib)
    Cur.execute('Select uuid from tbl_library_item where lib_uuid = ? and removed = 1', (libuid,))
    for i in Cur.fetchall():
        owner = i[0]
        Cur.execute('delete from tbl_flex_content where owneruuid = ?', (owner,))
    Cur.execute('delete from tbl_library_item where lib_uuid = ? and removed = 1', (libuid,))
    Con.commit()
    
def listfields(lib):
    libuid = getlib(lib)
    Cur.execute('SELECT title, type_code, uuid from tbl_flex_template where lib_uuid = ?', (libuid,))
    for i in Cur.fetchall():
        print '%s %16s %s' % (i[2], i[1], i[0])
    
def listlibs():
    Cur.execute('SELECT uuid, title from tbl_library')
    for i in Cur.fetchall():
        print i[0], i[1]
    

def getfield(lib, field):
    libuid = getlib(lib)
    Cur.execute('''SELECT uuid from tbl_flex_template where
        lib_uuid = ? and lower(title) = lower(?)''', (libuid, field))
    results = Cur.fetchone()
    if not results:
        print 'Unknown field of library %s:' % lib, field
        sys.exit(1)
    return results[0]
    
def getlib(lib):
    Cur.execute('SELECT uuid from tbl_library where lower(title) = lower(?)', (lib,))
    results = Cur.fetchone()
    if not results:
        print 'Unknown library:', lib
        sys.exit(1)
    return results[0]
    
def opendb(dbfile):
    global Con, Cur
    try:
        Con = lite.connect(dbfile)
        Cur = Con.cursor()    
    except lite.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

main()
