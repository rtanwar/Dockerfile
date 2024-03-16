import pika
import os
import sys
import time
import random
import sqlite3


rabbit_host = os.environ.get('rabbitmq_host', 'localhost')
rabbit_port = os.environ.get('rabbitmq_port', '5672')
rabbit_queue_name = os.environ.get('rabbitmq_queue', 'queue')
rabbit_pass = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')
rabbit_user = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
credentials = pika.PlainCredentials(rabbit_user,rabbit_pass)
#connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host,rabbit_port,"/",credentials))
#channel = connection.channel()

database_path = "/db/example.db"


def callback(ch, method, properties, body):
    print(f" [x] Received {body}")


def create_connection(database):
    """Create a database connection to the SQLite database specified by the database file."""
    db_connection = None
    try:
        db_connection = sqlite3.connect(database)
        print("Connection to SQLite database successful")
        return db_connection
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


db_connection = create_connection(database_path)
table_name = "example_table"

def read_row_by_id(db_connection, table_name, row_id):
    """Read a specific row from a table by ID."""
    try:
        cursor = db_connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
        row = cursor.fetchone()
        if row:
            print(f"Data for row with ID {row_id} in table '{table_name}':")
            return(row)
        else:
            print(f"No data found for row with ID {row_id} in table '{table_name}'")
            return None
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

def update_row_by_id(connection, table_name, row_id, new_data):
    """Update a specific row in a table by ID."""
    try:
        cursor = connection.cursor()
        update_query = f"""
        UPDATE {table_name}
        SET sum = ?            
        WHERE id = ?
        """
        cursor.execute(update_query, (*new_data, row_id))
        connection.commit()
        print(f"Row with ID {row_id} updated successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host,rabbit_port,"/",credentials))
    channel = connection.channel()

    channel.queue_declare(queue=rabbit_queue_name,durable=True)

    def callback(ch, method, properties, body):
        #print(f" [x] Received {body}")
        row_id_to_read = body.decode()
        print(f" [x] Received {row_id_to_read}")
        time_taken=random.randint(1, 3)
        time.sleep(time_taken)
        values = read_row_by_id(db_connection, table_name, row_id_to_read)
        sum = values[0]+values[1]
        update_row_by_id(db_connection,table_name,row_id_to_read,(sum,))
        print(f" [x] Done in {time_taken} Second(s).")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=rabbit_queue_name, on_message_callback=callback, auto_ack=False)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)



