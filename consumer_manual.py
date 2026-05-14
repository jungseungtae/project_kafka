import json
from confluent_kafka import Consumer, KafkaError

consumer = Consumer({
    'bootstrap.servers':  'localhost:9092',
    'group.id':           'pji-manual-group',
    'auto.offset.reset':  'earliest',
    'enable.auto.commit': False          # ← 자동 commit 끄기
})

consumer.subscribe(['pji-orders'])
print('Manual Commit Consumer 시작...\n')

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

        # --- 실제 처리 로직 (DB 저장 등) ---
        print(f'[처리중] P{msg.partition()}|O{msg.offset()} | {order["store_name"]} | {order["amount"]:,}원')

        # 처리 완료 후 수동 commit
        consumer.commit(asynchronous=False)
        print(f'[COMMIT] P{msg.partition()}|O{msg.offset()} 완료\n')

except KeyboardInterrupt:
    print('\n종료')
finally:
    consumer.close()