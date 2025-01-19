import pika
import json
from db import conn

RABBITMQ_USER='user'
RABBITMQ_PASSWORD='password'
RABBITMQ_HOST='172.16.22.5'
RABBITMQ_PORT='5672'
RABBITMQ_TIMEOUT = 1800
RABBITMQ_HEARTBEAT = 1800

# .............Connection.............
credentials = pika.PlainCredentials(
            RABBITMQ_USER,
            RABBITMQ_PASSWORD
            )

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    credentials= credentials,
    heartbeat=RABBITMQ_HEARTBEAT,
    blocked_connection_timeout=RABBITMQ_TIMEOUT
))
channel = connection.channel()

queue_1 = channel.queue_declare('downlaod_audio')
queue_2 = channel.queue_declare('process_transcript')
queue_3 = channel.queue_declare('analysis')

queue_1_name = queue_1.method.queue
queue_2_name = queue_2.method.queue
queue_3_name = queue_3.method.queue

channel.queue_bind(
    exchange='audio',
    queue=queue_1_name,
    routing_key='audio'
)

channel.queue_bind(
    exchange='asr',
    queue=queue_2_name,
    routing_key='asr'
)

channel.queue_bind(
    exchange='analysis',
    queue=queue_3_name,
    routing_key='analysis'
)

import time
def callback_1(ch, method, properties, body):
    payload = json.loads(body)
    print(f"Before processing call_back_1 : {list(conn.find({'id':payload['id']}))[0]}")
    print(' [x] notifying audio_url : {}'.format(payload))
    time.sleep(5)
    payload['status'] = "audio downloaded sucessfully"
    payload['stage'] = 1
    del payload['_id']
    conn.update_one({'id': payload['id']},{"$set": payload})
    print(' [x] Done')

    ch.basic_ack(delivery_tag = method.delivery_tag)

def callback_2(ch, method, properties, body):    
    payload = json.loads(body)
    print(f"Before processing callback_2 : {list(conn.find({'id':payload['id']}))}")
    
    print(' [x] notifying {}'.format(payload['user_email']))
    time.sleep(10)
    payload['transcript'] = "transcipt of given audio...."
    del payload['_id']
    conn.update_one({"id": payload['id']},{"$set": payload})
    print(' [x] Done')

    ch.basic_ack(delivery_tag = method.delivery_tag)

# def callback_3(ch, method, properties, body):
#     payload = json.loads(body)
#     print(' [x] notifying {}'.format(payload['user_email']))
#     print(' [x] Done')

#     ch.basic_ack(delivery_tag = method.delivery_tag)    

channel.basic_consume(on_message_callback=callback_1, queue=queue_1_name)
channel.basic_consume(on_message_callback=callback_2, queue=queue_2_name)
# channel.basic_consume(on_message_callback=callback_3, queue=queue_3_name)


print(' [*] Wating for notiy message.')

channel.start_consuming()