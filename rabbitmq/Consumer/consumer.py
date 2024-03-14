import pika
import os
import sys
import time
import random

rabbit_host = os.environ.get('rabbitmq_host', 'localhost')
rabbit_port = os.environ.get('rabbitmq_port', '5672')
rabbit_queue_name = os.environ.get('rabbitmq_queue', 'queue')
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host,rabbit_port))
channel = connection.channel()

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host,rabbit_port))
    channel = connection.channel()

    channel.queue_declare(queue=rabbit_queue_name,durable=True)

    def callback(ch, method, properties, body):
        #print(f" [x] Received {body}")
        print(f" [x] Received {body.decode()}")
        time_taken=random.randint(1, 3)
        time.sleep(time_taken)

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



