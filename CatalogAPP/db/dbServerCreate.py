import os

DATABASE = SqliteDatabase(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'Items.db'
    ),
    threadlocals=True
)
