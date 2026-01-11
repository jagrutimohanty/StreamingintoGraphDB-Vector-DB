import json
import pandas as pd
from confluent_kafka import Producer

from src.common.config import KAFKA_BOOTSTRAP, KAFKA_TOPIC
from src.common.schema import WorkRecord

def build_producer() -> Producer:
    return Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "enable.idempotence": True,
        "linger.ms": 50,
        "batch.num.messages": 10000,
    })

def row_to_dict(row) -> dict:
    d = row.to_dict()
    # convert pandas NaN -> None
    for k, v in list(d.items()):
        if pd.isna(v):
            d[k] = None
        # convert datetime to isoformat
        if hasattr(d[k], "isoformat"):
            d[k] = d[k].isoformat()
    return d

def excel_to_kafka(excel_path: str, sheet_name: str | int = 0) -> None:
    df = pd.read_excel(excel_path, sheet_name=sheet_name, engine="openpyxl")

    producer = build_producer()

    produced = 0
    for _, row in df.iterrows():
        payload = row_to_dict(row)

        # validate / enforce schema (raises if required fields missing)
        record = WorkRecord(**payload)

        key = record.person_id
        producer.produce(
            topic=KAFKA_TOPIC,
            key=key.encode("utf-8"),
            value=json.dumps(record.model_dump()).encode("utf-8"),
        )
        produced += 1

    producer.flush()
    print(f"Produced {produced} messages to topic={KAFKA_TOPIC}")

if __name__ == "__main__":
    excel_to_kafka("data/input.xlsx", sheet_name=0)
