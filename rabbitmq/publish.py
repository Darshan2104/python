import pika
import json
import uuid
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


channel.exchange_declare(
    exchange='audio',
    exchange_type = pika.exchange_type.ExchangeType.direct #'direct'
)

channel.exchange_declare(
    exchange='asr',
    exchange_type = pika.exchange_type.ExchangeType.direct #'direct'
)

channel.exchange_declare(
    exchange='analysis',
    exchange_type = pika.exchange_type.ExchangeType.direct #'direct'
)

#  ----------------------------- Pushlishing data -----------------------------
order = {
    "id":str(uuid.uuid4()),
    "user_email":"abc@gmail.com",
    "product":"t shirt",
    "stage":0,
    "audio_url":"url",
    "status":""
}

conn.insert_one(order)

channel.basic_publish(
    exchange='audio',
    routing_key='audio',
    body=json.dumps(order,default=str)
)
print('sent audio to process')


payload = list(conn.find({"id":order['id']}))[0]
print("before send sent : ",payload)

channel.basic_publish(
    exchange='asr',
    routing_key='asr',
    body=json.dumps(payload,default=str)
)
print(' [x] sent report message')


# channel.basic_publish(
#     exchange='analysis',
#     routing_key='analysis',
#     body=json.dumps(order)
# )
# print(' [x] sent report message')


connection.close()