import json
import time
from typing import Any, Dict, List

from confluent_kafka import Consumer, KafkaException
from neo4j import GraphDatabase

from src.common.config import (
    KAFKA_BOOTSTRAP, KAFKA_TOPIC, KAFKA_GROUP_ID,
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,
    BATCH_SIZE, BATCH_MAX_WAIT_SEC
)
from src.common.schema import WorkRecord

UPSERT_CYPHER = """
UNWIND $rows AS r

MERGE (p:Person {id: r.person_id})
SET p.name = coalesce(r.person_name, p.name)

MERGE (c:Company {id: r.company_id})
SET c.name = coalesce(r.company_name, c.name)

MERGE (p)-[w:WORKS_AT]->(c)
SET w.role = coalesce(r.role, w.role),
    w.event_time = coalesce(r.event_time, w.event_time)
"""

def build_consumer() -> Consumer:
    return Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": KAFKA_GROUP_ID,
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest",
        "max.poll.interval.ms": 300000,
    })

def write_batch(driver, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    with driver.session() as session:
        session.execute_write(lambda tx: tx.run(UPSERT_CYPHER, rows=rows).consume())

def run() -> None:
    consumer = build_consumer()
    consumer.subscribe([KAFKA_TOPIC])

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    batch: List[Dict[str, Any]] = []
    last_flush = time.time()

    print(f"Consuming topic={KAFKA_TOPIC} group={KAFKA_GROUP_ID} ...")

    try:
        while True:
            msg = consumer.poll(1.0)
            now = time.time()

            if msg is None:
                if batch and (now - last_flush) >= BATCH_MAX_WAIT_SEC:
                    write_batch(driver, batch)
                    consumer.commit(asynchronous=False)
                    print(f"Flushed {len(batch)} records (time-based)")
                    batch.clear()
                    last_flush = now
                continue

            if msg.error():
                raise KafkaException(msg.error())

            payload = json.loads(msg.value().decode("utf-8"))
            record = WorkRecord(**payload)  # validate

            batch.append(record.model_dump())

            if len(batch) >= BATCH_SIZE:
                write_batch(driver, batch)
                consumer.commit(asynchronous=False)
                print(f"Flushed {len(batch)} records (size-based)")
                batch.clear()
                last_flush = now

    finally:
        try:
            if batch:
                write_batch(driver, batch)
                consumer.commit(asynchronous=False)
        except Exception:
            pass
        consumer.close()
        driver.close()

if __name__ == "__main__":
    run()