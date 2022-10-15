import pyarrow.parquet as pq

df = pq.read_pandas('BTC-USDT.parquet').to_pandas()
