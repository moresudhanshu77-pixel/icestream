# IceStream: Real-Time Lakehouse Observability

A self-healing data pipeline that monitors e-commerce checkout telemetry in real time.

## Problem
Batch ETL jobs delay bad-data detection by hours. Null values or schema drift often go
unnoticed until a dashboard breaks. IceStream catches data quality issues in the stream,
quarantines bad data automatically, and requires zero human intervention.

## Architecture
Kafka -> Flink -> Apache Iceberg (on MinIO/S3), with a Python rules engine
and a React Flow lineage dashboard.