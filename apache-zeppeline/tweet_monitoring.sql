--Cell 1

%flink.ssql

CREATE TABLE tweets (
  id STRING,
  username STRING,
  tweet STRING,
  created_at STRING
) WITH (
  'connector' = 'kinesis',
  'stream' = 'tweet-stream',
  'aws.region' = 'us-east-1',
  'format' = 'json',
  'scan.stream.initpos' = 'LATEST'
);


--Cell 2

%flink.ssql

SELECT
  username,
  COUNT(*) AS tweet_count,
  TUMBLE_START(PROCTIME(), INTERVAL '30' SECOND) AS window_start
FROM tweets
GROUP BY
  username,
  TUMBLE(PROCTIME(), INTERVAL '30' SECOND);
