import json
from confluent_kafka import Consumer, KafkaError

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id':          'pji-analytics-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['pji-orders'])
print('메시지 대기 중... (Ctrl+C로 종료)\n')

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f'ERROR: {msg.error()}')
            continue

        order = json.loads(msg.value().decode('utf-8'))
        print(f'[수신] {order["store_name"]} | {order["menu"]} | {order["amount"]:,}원 | {order["timestamp"]}')

except KeyboardInterrupt:
    print('\n종료')
finally:
    consumer.close()