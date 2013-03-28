memento-util
============

Utilities for tweaking/adjusting/maintaining the Memento Database Sqlite file (memento.db)

Help sheet:

usage: mementoutil.py [-d <memento_sqlite.db>] command [args]
Options:
    -d <sqlite file>      ; default 'memento.db'
Commands:
    libs                  ; list libraries in memento db.
    fields <lib>          ; list fields in given lib.
    emptytrash <lib>      ; delete 'removed' items.
    content <lib> <field> ; list all content entries for a field.
    preload <lib> <field> <file> ; add contents of file to field, one entry per line.
                          ; (use - for stdin)
						  
This program is used chiefly for pre-loading Memento's autocomplete text fields so that by just typing a few characters a list of all matching entries is presented.

It does this by adding "deleted" entries to the library. Note that if the library is cleared (more->settings->clearing the library) these preloads will disappear.

Techincal Details:

This is running under Python 2.7. It uses sqlite3, which has been part of Python since version 2.5

 