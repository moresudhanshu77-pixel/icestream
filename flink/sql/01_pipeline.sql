SET 'execution.checkpointing.interval' = '10s';

CREATE CATALOG ice WITH (
  'type' = 'iceberg',
  'catalog-impl' = 'org.apache.iceberg.rest.RESTCatalog',
  'uri' = 'http://iceberg-rest:8181',
  'warehouse' = 's3://warehouse/',
  'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
  's3.endpoint' = 'http://localstack:4566',
  's3.path-style-access' = 'true',
  'client.region' = 'us-east-1'
);

CREATE DATABASE IF NOT EXISTS ice.lake;

CREATE TABLE IF NOT EXISTS ice.lake.checkout_events (
  event_id STRING,
  order_id BIGINT,
  user_id BIGINT,
  event_ts TIMESTAMP(3),
  currency STRING,
  subtotal DOUBLE,
  tax_amount DOUBLE,
  total DOUBLE,
  country STRING,
  payment_method STRING
) WITH ('format-version' = '2');

CREATE TEMPORARY TABLE kafka_checkout (
  event_id STRING,
  order_id BIGINT,
  user_id BIGINT,
  event_ts TIMESTAMP(3),
  currency STRING,
  subtotal DOUBLE,
  tax_amount DOUBLE,
  total DOUBLE,
  country STRING,
  payment_method STRING
) WITH (
  'connector' = 'kafka',
  'topic' = 'checkout.events',
  'properties.bootstrap.servers' = 'kafka:9092',
  'properties.group.id' = 'icestream-flink',
  'scan.startup.mode' = 'latest-offset',
  'format' = 'json',
  'json.timestamp-format.standard' = 'ISO-8601',
  'json.ignore-parse-errors' = 'true'
);

INSERT INTO ice.lake.checkout_events SELECT * FROM kafka_checkout;