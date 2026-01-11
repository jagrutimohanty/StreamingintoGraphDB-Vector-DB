import os
from dotenv import load_dotenv

load_dotenv()

def env(key: str, default: str | None = None) -> str:
    val = os.getenv(key, default)
    if val is None:
        raise ValueError(f"Missing required env var: {key}")
    return val

KAFKA_BOOTSTRAP = env("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = env("KAFKA_TOPIC", "excel.records")
KAFKA_GROUP_ID = env("KAFKA_GROUP_ID", "neo4j-writer")

NEO4J_URI = env("NEO4J_URI", "neo4j://localhost:7687")
NEO4J_USER = env("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = env("NEO4J_PASSWORD", "password")

BATCH_SIZE = int(env("BATCH_SIZE", "500"))
BATCH_MAX_WAIT_SEC = float(env("BATCH_MAX_WAIT_SEC", "2"))
