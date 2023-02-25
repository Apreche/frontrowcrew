#!/usr/bin/env python
# Take the csv exports from the forums and make an SQLLite database from them

import csv
import sqlite3
from dateutil.parser import parse as dateparse

NEW_FORUM_CSV_NAME = "community.csv"
OLD_FORUM_CSV_NAME = "oldforum.csv"
MANUAL_LINK_CSV_NAME = "manual_forum_link.csv"
FORUM_DB_NAME = "forum.db"
OLD_FORUM_TABLE_NAME = "oldforum"
NEW_FORUM_TABLE_NAME = "newforum"


create_table_query = """
    CREATE TABLE {table_name} (
        id INTEGER PRIMARY KEY,
        created_at TEXT,
        title TEXT,
        creator_id INTEGER,
        creator_name TEXT,
        category_id INTEGER,
        category_name TEXT
    );
"""

create_manual_table_query = """
    CREATE TABLE manual_forum_links (
        content_id INTEGER PRIMARY KEY,
        show_title TEXT,
        content_title TEXT,
        date TEXT,
        forum TEXT,
        discussion_id INT
    );
"""


insert_query = """
    INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?)
"""

manual_insert_query = """
    INSERT INTO manual_forum_links VALUES (?, ?, ?, ?, ?, ?)
"""


def load_csv(csv_name: str):
    csv_data = []
    with open(csv_name) as csvfile:
        reader = csv.reader(
            csvfile,
            delimiter=',',
            quotechar='"',
            escapechar="\\"
        )
        for row in reader:
            id = int(row[0])
            date = dateparse(row[1])
            title = row[2]
            user_id = row[3]
            username = row[4]
            category_id = row[5]
            category_name = row[6]
            if not category_id.isnumeric():
                breakpoint()
                print(row)
            csv_data.append(
                (
                    id,
                    date,
                    title,
                    user_id,
                    username,
                    category_id,
                    category_name
                )
            )
    return csv_data


def load_manual_csv(csv_name: str):
    csv_data = []
    with open(csv_name) as csvfile:
        reader = csv.reader(
            csvfile,
            delimiter=',',
            quotechar='"',
            escapechar="\\"
        )
        for row in reader:
            raw_discussion_id = row[5]
            if raw_discussion_id.isnumeric():
                content_id = int(row[0])
                show_title = row[1]
                content_title = row[2]
                date = dateparse(row[3])
                forum = row[4]
                discussion_id = int(raw_discussion_id)
                csv_data.append(
                    (
                        content_id,
                        show_title,
                        content_title,
                        date,
                        forum,
                        discussion_id,
                    )
                )
    return csv_data


def main() -> int:
    # Create SQLite tables
    connection = sqlite3.connect(FORUM_DB_NAME)
    cursor = connection.cursor()
    cursor.execute(create_table_query.format(table_name=NEW_FORUM_TABLE_NAME))
    cursor.execute(create_table_query.format(table_name=OLD_FORUM_TABLE_NAME))
    cursor.execute(create_manual_table_query)

    # Get data from csvs
    old_forum_data = load_csv(OLD_FORUM_CSV_NAME)
    new_forum_data = load_csv(NEW_FORUM_CSV_NAME)
    manual_linkage_data = load_manual_csv(MANUAL_LINK_CSV_NAME)

    # insert data into SQLite
    cursor.executemany(
        insert_query.format(table_name=OLD_FORUM_TABLE_NAME),
        old_forum_data
    )
    cursor.executemany(
        insert_query.format(table_name=NEW_FORUM_TABLE_NAME),
        new_forum_data
    )
    cursor.executemany(
        manual_insert_query, manual_linkage_data
    )

    # Remove threads from forbidden categories
    cursor.execute("DELETE from newforum where category_id in (4,5);")
    cursor.execute("DELETE from oldforum where category_id = 18;")
    cursor.execute("DELETE from oldforum where creator_id='N';")

    connection.commit()
    connection.close()
    return 0


if __name__ == "__main__":
    main()
