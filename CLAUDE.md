# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Apache Kafka 실습 프로젝트. 피자 주문 도메인을 모델로 사용하며 Producer→Kafka→Consumer→MySQL 파이프라인을 구현한다.

## 실행 명령어

```bash
# 인프라 기동 (Kafka, MySQL, Kafka-UI, Kafka-Connect)
docker-compose up -d

# DB 테이블 초기화 (최초 1회)
python init_db.py

# 메시지 전송 (10건, 0.5초 간격)
python producer.py

# 컨슈머 실행 (각각 별도 터미널)
python consumer.py A              # Auto-commit, 인스턴스 A
python consumer.py B              # Auto-commit, 인스턴스 B (파티션 분배 확인)
python consumer_manual.py         # Manual-commit 패턴
python consumer_pipeline.py       # MySQL UPSERT 파이프라인
python consumer_replay.py         # 오프셋 0 재처리

# 집계 결과 조회
python check_sales.py
```

## 아키텍처

### 데이터 흐름

`producer.py`가 `pji-orders` 토픽에 JSON 메시지를 전송하면, 4개의 컨슈머가 각기 다른 패턴으로 소비한다. `consumer_pipeline.py`만 MySQL에 데이터를 저장하며, 나머지는 출력 또는 재처리 목적이다.

### Consumer Group 설계

각 컨슈머 파일은 의도적으로 서로 다른 `group.id`를 사용한다. 같은 그룹 ID를 공유하면 파티션이 분배되어 메시지가 나뉘고, 다른 그룹 ID면 같은 메시지를 독립적으로 소비한다. `consumer.py A`와 `consumer.py B`는 같은 `pji-analytics-group`을 공유하므로 파티션 리밸런싱이 발생한다.

### Manual Commit 패턴 (consumer_manual.py, consumer_pipeline.py)

`enable.auto.commit: False`로 설정하고 처리 완료 후 `consumer.commit()`을 명시적으로 호출한다. `consumer_pipeline.py`는 MySQL `commit()` 이후에 Kafka `commit()`을 호출해 DB 저장과 오프셋 진행의 순서를 보장한다.

### MySQL UPSERT 패턴

`consumer_pipeline.py`는 두 단계로 처리한다:
1. `upsert_order()` — `orders` 테이블에 원본 저장 (`INSERT ... ON DUPLICATE KEY UPDATE`)
2. `upsert_sales_summary()` — `store_sales_realtime` 테이블에 매장별 집계 갱신

### Replay 패턴 (consumer_replay.py)

`subscribe()` 대신 `assign(TopicPartition(topic, partition, offset=0))`을 사용해 특정 오프셋부터 재처리한다. 파티션 0·1·2를 수동 할당한다.

## 인프라 구성

- **Kafka Broker**: `localhost:9092` (내부 리스너: `29092`)
- **Kafka UI**: `http://localhost:8080`
- **MySQL**: `localhost:3306`, DB=`pji_kafka`, user=`root`, password=`kafka1234`
- **Kafka Connect**: `localhost:8083` (JDBC 커넥터 포함)

Zookeeper 모드로 운영 (KRaft 미사용). `KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"` 설정으로 토픽 자동 생성.

## 의존성

```
confluent-kafka >= 2.14.0
mysql-connector-python >= 9.7.0
```
