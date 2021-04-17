from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.functions import udf
from pyspark.ml.linalg import SparseVector, Vectors, VectorUDT
from pyspark.sql.types import ArrayType, IntegerType

spark = SparkSession \
    .builder \
    .appName("Keyword clustering") \
    .getOrCreate()

sc = spark.sparkContext

df = spark.read.csv('./search_results.csv', header=True)

df = df.drop('Title', '_id')

keyword2url = df.groupBy('Keyword') \
  .agg(F.collect_list('url').alias('urlIndex'))

df3 = keyword2url.withColumn("k_id", F.monotonically_increasing_id())
df3.createOrReplaceTempView('df3')
df3 = spark.sql('select row_number() over (order by "k_id") as Keyword_id, * from df3').drop('k_id')


df4 = df3.withColumn("Url", F.explode(df3.urlIndex)) \
      .drop("urlIndex")

keyword_ids = df3.select('Keyword_id', 'Keyword')
keyword_ids.coalesce(1).write.csv('keywords.csv')

