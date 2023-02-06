# FRC ETL

Tools for importing the data from the old frontrowcrew.com database to the new one.

## Execute Full ETL

> **NOTE:** Running the full ETL will also reset the database completely.
1. Export MySQL database to SQLite using [mysql2sqlite](https://github.com/dumblob/mysql2sqlite).
2. Put the file onto the same file system as the PostgreSQL database.
3. Run the management command `./manage.py etl_frc <PATH>` where PATH is the absolute path to the SQLite database file on that same file system.


## Cleaning Export

The complete export of the old MySQL database has a lot of extra tables in it that are unecessary for ETL and/or contain sensitive data like hashed passwords. Before committing or sharing a database file, process it with `sql_steps/00_clean_sqlite_db.sql` to remove those tables.
