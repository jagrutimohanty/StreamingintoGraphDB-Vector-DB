# StreamingintoGraphDB-Vector-DB
Working on project using streaming application using kafka neo4j python sdk chroma db to create datapipelines

# Excel → Kafka → Neo4j Data Pipeline

A production-style data ingestion pipeline that reads records from Excel, publishes them to Kafka, and writes them into Neo4j as a graph using Python.

This project demonstrates:
- Decoupled ingestion using Kafka
- Schema validation with Pydantic
- Batched, idempotent writes to Neo4j
- Local development using Docker Compose

---

## Use Case

- Ingest structured business data from Excel
- Stream records through Kafka for durability and scalability
- Persist data into Neo4j as nodes and relationships
- Enable reprocessing, replay, and future real-time extensions

---

## Architecture Overview

Excel File --> Python Producer --> Kafka Topic --> Python Consumer --> Neo4j Graph Database

- **Producer** converts Excel rows into JSON messages
- **Kafka** acts as a buffer and replayable log
- **Consumer** batches messages and performs graph upserts
- **Neo4j** stores entities and relationships



## Sample Data (Excel)

The Excel file must contain the following columns:

| Column Name   | Description |
|--------------|------------|
| person_id    | Unique ID for person |
| person_name  | Person name |
| company_id   | Unique ID for company |
| company_name | Company name |
| role         | Role at company |
| event_time   | ISO timestamp |

A sample file with 10 records is provided in `data/input.xlsx`.

---

## Quick Start

### 1 Start Kafka and Neo4j

```bash
docker compose up -d

Neo4j UI: http://localhost:7474

Apply Neo4j Constraints

### 2 Run in Neo4j Browser:

CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT company_id IF NOT EXISTS
FOR (c:Company) REQUIRE c.id IS UNIQUE;


### 3 Create Python Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

### 4 Configure Environment Variables
cp .env.example .env

### 5 Run Consumer (Kafka → Neo4j)
python -m src.consumer.kafka_to_neo4j


### 6 Run Producer (Excel → Kafka)
python -m src.producer.excel_to_kafka

### 7 Verify in Neo4j

MATCH (p:Person)-[w:WORKS_AT]->(c:Company)
RETURN p, w, c;
