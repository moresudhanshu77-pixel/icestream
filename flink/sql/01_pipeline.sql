CREATE CATALOG ice WITH (
  'type' = 'iceberg',
  'catalog-impl' = 'org.apache.iceberg.rest.RESTCatalog',
  'uri' = 'http://iceberg-rest:8181',
  'warehouse' = '/warehouse',
  'io-impl' = 'org.apache.iceberg.hadoop.HadoopFileIO'
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