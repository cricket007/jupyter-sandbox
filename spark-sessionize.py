'''
Resources
SQL Cumulative Sum: http://stackoverflow.com/questions/2120544/how-to-get-cumulative-sum

'''

import sys
from pyspark import SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.window import Window
import pyspark.sql.functions as func

f_in = "data/sample_input.txt"
if len(sys.argv) < 2:
    print("Usage: ", sys.argv[0], "input.txt")
    sys.exit(1)

if __name__ == "__main__":
    sc = SparkContext()
    sqlContext = SQLContext(sc)

    f_in = sys.argv[1]
    lines = sc.textFile(f_in)
    # lines = sc.textFile(sys.argv[1]).cache()
    pairs = lines.map(lambda line: line.split(','))

    sqlSchema = pairs.map(lambda pair: Row(id=pair[1], time=int(pair[0])))
    df = sqlContext.createDataFrame(sqlSchema)

    # window_id = Window.partitionBy(df['id']).orderBy(df['time'])
    # window_time = Window.partitionBy(df['time'])
    # time_lag = func.lag(df['time'],default=-1).over(window_id)
    # id_lag = func.lag(df['id']).over(window_id)

    # labeled = df.select(df['id'], df['time'], func.when(df['time']-time_lag > 1, 1).otherwise(0).alias('boundary'))

    # df.registerTempTable("data")
    df.cacheTable("data")

    query = sqlContext.sql(
        r"SELECT SUM(CASE WHEN dup_count + LAG(dup_count, 1, -1) OVER (PARTITION BY id) = 0 THEN 1 ELSE 0 END) OVER (ORDER BY time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), time FROM (SELECT id, time, COUNT(time) OVER (PARTITION BY time) AS dup_count FROM data) tmp")
    groupings = query.rdd

    groupings.groupByKey().map(lambda tup: sorted(set(tup[1]))).collect()
