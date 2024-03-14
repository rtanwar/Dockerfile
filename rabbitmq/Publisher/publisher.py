import pika
import os
import sys

rabbit_host = os.environ.get('rabbitmq_host', 'localhost')
rabbit_port = os.environ.get('rabbitmq_port', '5672')
rabbit_queue_name = os.environ.get('rabbitmq_queue', 'queue')
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host,rabbit_port))
channel = connection.channel()

def send_message(channel,rabbit_queue_name,message):
    
    channel.queue_declare(queue=rabbit_queue_name,durable=True)
    properties=pika.BasicProperties(
                     delivery_mode=2#pika.DeliveryMode.Persistent
                        )
    channel.basic_publish(exchange='',
                      routing_key=rabbit_queue_name,properties=properties,body=message)
    
    
    print(f" [x] Sent {message}")

message = 'Hello World!'
if len(sys.argv) > 1:
    message = sys.argv[1]
send_message(channel,rabbit_queue_name,message)

connection.close()