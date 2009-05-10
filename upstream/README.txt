The SRD, version 3.5, as a sqlite database.  Originally from here:
http://files.antlinux.com/docs/DnD/

Use:

zcat {tables,srd}*.sql.gz | sqlite3 -init - srd35.db
