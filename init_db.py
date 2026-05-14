import mysql.connector

conn = mysql.connector.connect(
    host='localhost', port=3306,
    user='root', password='kafka1234',
    database='pji_kafka'
)
cursor = conn.cursor()

# 원본 주문 테이블 (UPSERT 대상)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id   INT          PRIMARY KEY,
        store_name VARCHAR(50)  NOT NULL,
        menu       VARCHAR(50)  NOT NULL,
        amount     INT          NOT NULL,
        created_at DATETIME     NOT NULL
    )
""")

# 매장별 실시간 집계 테이블
cursor.execute("""
    CREATE TABLE IF NOT EXISTS store_sales_realtime (
        store_name  VARCHAR(50)  PRIMARY KEY,
        total_sales BIGINT       NOT NULL DEFAULT 0,
        order_count INT          NOT NULL DEFAULT 0,
        updated_at  DATETIME     NOT NULL
    )
""")

conn.commit()
cursor.close()
conn.close()
print('테이블 생성 완료')