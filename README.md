# Kafka 실습 프로젝트 — 피자 주문 스트리밍 시스템

Apache Kafka의 핵심 패턴을 피자 주문 도메인으로 실습하는 프로젝트입니다.

## 학습 목표

- Kafka Producer / Consumer 기본 패턴
- Consumer Group을 이용한 파티션 분배
- Auto Commit vs Manual Commit 차이
- Kafka → MySQL 실시간 파이프라인 구축
- 메시지 Replay (오프셋 재지정)

---

## 아키텍처

```
producer.py
    │  (pji-orders 토픽)
    ▼
Kafka Broker (localhost:9092)
    │
    ├─▶ consumer.py            — 메시지 출력 (pji-analytics-group)
    ├─▶ consumer_manual.py     — 수동 오프셋 커밋 (pji-manual-group)
    ├─▶ consumer_pipeline.py   — MySQL 저장 (pji-pipeline-group)
    └─▶ consumer_replay.py     — 오프셋 0부터 재처리 (pji-replay-group)

MySQL (localhost:3306 / pji_kafka)
    ├─ orders                  — 주문 원본
    └─ store_sales_realtime    — 매장별 실시간 집계
         │
         └─▶ check_sales.py   — 집계 조회 유틸리티
```

---

## 사전 요구사항

- Python 3.10+
- Docker & Docker Compose

---

## 빠른 시작

### 1. 인프라 실행

```bash
docker-compose up -d
```

| 서비스 | 주소 | 용도 |
|---|---|---|
| Kafka Broker | localhost:9092 | 메시지 브로커 |
| Kafka UI | http://localhost:8080 | 토픽/메시지 모니터링 |
| MySQL | localhost:3306 | 데이터 저장 |
| Kafka Connect | localhost:8083 | JDBC 커넥터 |

### 2. 파이썬 패키지 설치

```bash
pip install confluent-kafka mysql-connector-python
```

### 3. MySQL 테이블 초기화

```bash
python init_db.py
```

### 4. Producer 실행

```bash
python producer.py
```

4개 매장(강남점·송파점·마포점·판교점), 4개 메뉴(페퍼로니·슈퍼파파스·가든파티·불고기)로 주문 10건을 0.5초 간격으로 전송합니다.

### 5. Consumer 실행 (별도 터미널)

```bash
# 기본 컨슈머 (인스턴스 A)
python consumer.py A

# 기본 컨슈머 (인스턴스 B) — 파티션 분배 확인
python consumer.py B

# 수동 커밋 컨슈머
python consumer_manual.py

# DB 파이프라인 컨슈머
python consumer_pipeline.py
```

### 6. 실시간 집계 조회

```bash
python check_sales.py
```

---

## 파일 구조

```
project_kafka/
├── docker-compose.yml        # Kafka, MySQL, Kafka-UI, Kafka Connect
├── producer.py               # 주문 메시지 생성·전송
├── consumer.py               # 기본 컨슈머 (Auto Commit)
├── consumer_manual.py        # 수동 오프셋 커밋 패턴
├── consumer_pipeline.py      # MySQL UPSERT 파이프라인
├── consumer_replay.py        # 오프셋 0 재처리
├── init_db.py                # DB 테이블 초기화
└── check_sales.py            # 매장별 집계 조회
```

---

## 주요 Kafka 개념별 코드

| 개념 | 파일 | 핵심 설정 |
|---|---|---|
| Delivery Callback | `producer.py` | `producer.produce(..., callback=delivery_report)` |
| Consumer Group | `consumer.py` | `group.id: pji-analytics-group` |
| Auto Commit | `consumer.py` | `enable.auto.commit: True` (기본값) |
| Manual Commit | `consumer_manual.py` | `enable.auto.commit: False` + `consumer.commit()` |
| DB 파이프라인 | `consumer_pipeline.py` | Kafka 커밋과 MySQL 커밋 순서 보장 |
| Offset Replay | `consumer_replay.py` | `assign(TopicPartition(..., offset=0))` |

---

## DB 스키마

```sql
-- 주문 원본
orders (
    order_id        VARCHAR(50) PRIMARY KEY,
    store_name      VARCHAR(50),
    menu            VARCHAR(50),
    amount          INT,
    order_timestamp DATETIME
)

-- 매장별 실시간 집계
store_sales_realtime (
    store_name   VARCHAR(50) PRIMARY KEY,
    order_count  INT,
    total_sales  BIGINT,
    last_updated DATETIME
)
```

---

## 접속 정보

| 항목 | 값 |
|---|---|
| Kafka | localhost:9092 |
| MySQL Host | localhost:3306 |
| MySQL DB | pji_kafka |
| MySQL User | root / kafka1234 |
| Kafka UI | http://localhost:8080 |
