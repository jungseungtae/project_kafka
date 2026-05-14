import json
from datetime import datetime
from confluent_kafka import Consumer, KafkaError
import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host='localhost', port=3306,
    user='root', password='kafka1234',
    database='pji_kafka'
)
cursor = conn.cursor()

consumer = Consumer({
    'bootstrap.servers':  'localhost:9092',
    'group.id':           'pji-pipeline-group',
    'auto.offset.reset':  'earliest',
    'enable.auto.commit': False          # Manual Commit
})

consumer.subscribe(['pji-orders'])
print('파이프라인 시작...\n')

def upsert_order(order):
    """주문 원본 저장 (중복 시 UPDATE)"""
    cursor.execute("""
        INSERT INTO orders (order_id, store_name, menu, amount, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            amount     = VALUES(amount),
            created_at = VALUES(created_at)
    """, (
        order['order_id'],
        order['store_name'],
        order['menu'],
        order['amount'],
        order['timestamp'][:19]          # ISO → MySQL datetime
    ))

def upsert_sales_summary(order):
    """매장별 집계 UPSERT"""
    cursor.execute("""
        INSERT INTO store_sales_realtime (store_name, total_sales, order_count, updated_at)
        VALUES (%s, %s, 1, %s)
        ON DUPLICATE KEY UPDATE
            total_sales = total_sales + VALUES(total_sales),
            order_count = order_count + 1,
            updated_at  = VALUES(updated_at)
    """, (
        order['store_name'],
        order['amount'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

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

        # 1. 주문 원본 저장
        upsert_order(order)

        # 2. 집계 업데이트
        upsert_sales_summary(order)

        conn.commit()

        # 3. Kafka Offset commit
        consumer.commit(asynchronous=False)

        print(
            f'[저장완료] P{msg.partition()}|O{msg.offset()} | '
            f'{order["store_name"]} | {order["menu"]} | {order["amount"]:,}원'
        )

except KeyboardInterrupt:
    print('\n종료')
finally:
    cursor.close()
    conn.close()
    consumer.close()