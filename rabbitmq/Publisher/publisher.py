import pika
import os
import sys
import sqlite3
import random

rabbit_host = os.environ.get('rabbitmq_host', 'localhost')
rabbit_port = os.environ.get('rabbitmq_port', '5672')
rabbit_queue_name = os.environ.get('rabbitmq_queue', 'queue')
rabbit_pass = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
rabbit_user = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
credentials = pika.PlainCredentials(rabbit_user,rabbit_pass)
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host,rabbit_port,"/",credentials))
channel = connection.channel()
    # Create a connection to the database


def create_connection(database):
    """Create a database connection to the SQLite database specified by the database file."""
    db_connection = None
    try:
        db_connection = sqlite3.connect(database)
        print("Connection to SQLite database successful")
        return db_connection
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

def create_table(db_connection, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        cursor = db_connection.cursor()
        cursor.execute(create_table_sql)
        print("Table created successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

def insert_data(db_connection, insert_data_sql, data):
    """Insert data into the table."""
    try:
        cursor = db_connection.cursor()
        cursor.execute(insert_data_sql, data)
        db_connection.commit()        
        print("Data inserted successfully")
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

database_path = "/db/example.db"

    # SQL statements
create_table_sql = """
    CREATE TABLE IF NOT EXISTS example_table (
        id INTEGER PRIMARY KEY,
        value1 INTEGER,
        value2 INTEGER,
        sum INTEGER
    );
    """

insert_data_sql = """
    INSERT INTO example_table (value1, value2) VALUES (?, ?)
    """

def send_message(channel,rabbit_queue_name,message):
    
    channel.queue_declare(queue=rabbit_queue_name,durable=True)
    properties=pika.BasicProperties(
                     delivery_mode=2#pika.DeliveryMode.Persistent
                        )
    
    if db_connection is not None:
    # Create table
        create_table(db_connection, create_table_sql)
    # Insert data
        value1=random.randint(1, 999)
        value2=random.randint(1, 999)

        message=insert_data(db_connection, insert_data_sql, (value1,value2))
        channel.basic_publish(exchange='', routing_key=rabbit_queue_name,properties=properties,body=str(message))
    # Close connection
        db_connection.close()
    else:
        print("Unable to establish connection to the database")
    
    print(f" [x] Sent {message}")

message = 'Hello World!'
if len(sys.argv) > 1:
    message = sys.argv[1]

db_connection = create_connection(database_path)
send_message(channel,rabbit_queue_name,message)
connection.close()



