##First Paragraph
%flink.ssql(type=update)

CREATE TABLE transactions_v3 (
  id STRING,
  user_id STRING,
  amount DOUBLE,
  event_time STRING,
  region STRING
)
WITH (
  'connector' = 'kinesis',
  'stream' = 'tx-stream',
  'aws.region' = 'us-east-1',
  'format' = 'json',
  'scan.stream.initpos' = 'LATEST'
);


##Second Paragraph
%flink.ssql(type=update)

CREATE TABLE fraud_output_s3 (
  id STRING,
  user_id STRING,
  amount DOUBLE,
  event_time STRING,
  region STRING
)
PARTITIONED BY (region)
WITH (
  'connector' = 'filesystem',
  'path' = 's3://fraud-output-buckett/fraud/',
  'format' = 'json'
);



##Third Parapgraph
%flink.ssql(type=update)

INSERT INTO suspicious_tx
SELECT *
FROM transactions
WHERE amount > 10000;

##Fourth Paragraph
%flink.ssql(type=update)

CREATE TABLE clean_tx (
  id STRING,
  user_id STRING,
  amount DOUBLE,
  timestamp STRING,
  region STRING
)
WITH (
  'connector' = 'filesystem',
  'path' = 's3://fraud-output-bucket/cleaned/',
  'format' = 'parquet'
);

##Five Parapgraph

%flink.ssql(type=update)

INSERT INTO clean_tx
SELECT *
FROM transactions
WHERE amount <= 10000;
