import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

BOOTSTRAP_SERVERS = 'localhost:9092'
TOPIC = 'pji-orders'

def delivery_callback(err, msg):
    if err:
        print(f'[ERROR] 전송 실패: {err}')
    else:
        print(f'[OK] Partition={msg.partition()} | Offset={msg.offset()}')

producer = Producer({'bootstrap.servers': BOOTSTRAP_SERVERS})

STORES = ['강남점', '송파점', '마포점', '판교점']
MENUS  = ['페퍼로니', '슈퍼파파스', '가든파티', '불고기']

def generate_order():
    return {
        'order_id':   random.randint(100000, 999999),
        'store_name': random.choice(STORES),
        'menu':       random.choice(MENUS),
        'amount':     random.randint(15000, 45000),
        'timestamp':  datetime.now().isoformat()
    }

for i in range(10):
    order = generate_order()
    print(f'[발행] {order["store_name"]} | {order["menu"]} | {order["amount"]:,}원')
    producer.produce(
        topic    = TOPIC,
        key      = order['store_name'],
        value    = json.dumps(order, ensure_ascii=False),
        callback = delivery_callback
    )
    producer.poll(0)
    time.sleep(0.5)

producer.flush()
print('전송 완료')