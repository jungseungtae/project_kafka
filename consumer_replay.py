import json
from confluent_kafka import Consumer, TopicPartition

consumer = Consumer({
    'bootstrap.servers':  'localhost:9092',
    'group.id':           'pji-replay-group',
    'auto.offset.reset':  'earliest',
    'enable.auto.commit': False
})

TOPIC = 'pji-orders'

# Partition 0번을 Offset 0부터 재처리
replay_partitions = [
    TopicPartition(TOPIC, partition=0, offset=0),
    TopicPartition(TOPIC, partition=1, offset=0),
    TopicPartition(TOPIC, partition=2, offset=0),
]

consumer.assign(replay_partitions)   # subscribe 대신 assign 사용
print('재처리 시작 (Offset 0부터)\n')

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue
        if msg.error():
            continue

        order = json.loads(msg.value().decode('utf-8'))
        print(f'[재처리] P{msg.partition()}|O{msg.offset()} | {order["store_name"]} | {order["menu"]} | {order["amount"]:,}원')

except KeyboardInterrupt:
    print('\n재처리 종료')
finally:
    consumer.close()