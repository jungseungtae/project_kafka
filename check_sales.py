import mysql.connector

conn = mysql.connector.connect(
    host='localhost', port=3306,
    user='root', password='kafka1234',
    database='pji_kafka'
)
cursor = conn.cursor()

print('=== 매장별 실시간 매출 집계 ===\n')
cursor.execute("""
    SELECT store_name, order_count,
           FORMAT(total_sales, 0) AS total_sales,
           updated_at
    FROM store_sales_realtime
    ORDER BY total_sales DESC
""")

for row in cursor.fetchall():
    print(f'{row[0]:10s} | {row[1]:3d}건 | {row[2]:>12s}원 | {row[3]}')

cursor.close()
conn.close()