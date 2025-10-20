from pyspark.sql import SparkSession
from pyspark.sql import functions as F



def init_spark():

	"""

	Initialize spark instance -> here you don't need any credentials for wx.data 2.1.0, the configuration is setup for the cluster / unless you want to connect external sources

	"""

	builder = (SparkSession.builder
             .appName("spark-processing")
			 .enableHiveSupport()
             )           
    # spark = SparkSession.builder \
	# 	.appName("spark-processing") \
	# 	.enableHiveSupport() \
	builder = (builder
               .config("spark.extraListeners", "") )
	spark = builder.getOrCreate()

	return spark

spark = init_spark()

# env variables to read from job submission
hive_bucket = spark.conf.get("spark.myenv.hive_bucket")
iceberg_catalog = spark.conf.get("spark.myenv.iceberg_catalog")
hive_catalog = spark.conf.get("spark.myenv.hive_catalog")

schema_data_hive = spark.conf.get("spark.myenv.schema_data_hive")
schema_data_iceberg = spark.conf.get("spark.myenv.schema_data_iceberg")
schema_netezza_offload = spark.conf.get("spark.myenv.schema_netezza_offload")

#------------------------------------Configuration---------------------------------------------------------
# Make sure that the configuration of spark in cluster is the same as in watsonx.data UI (spark)

# print("Spark configuration", spark.sparkContext.getConf().getAll())


#---------------------------------------Check------------------------------------------------------
# ## Check catalogs and schemas
# > not advised: in case you changed names of catalogs and schemas from the default in .env_lab2, update all sql queries accordingly

print("Available catalogs", spark.sql("SHOW CATALOGS").show())

print("Schemas from iceberg data", spark.sql(f"""
show schemas from {iceberg_catalog}
""").show())

print("Schemas from hive catalog", spark.sql(f"""
show schemas from {hive_catalog}
""").show())

print("Tables from netezza offload", spark.sql(f"""
show tables from {iceberg_catalog}.{schema_netezza_offload}
""").show())

print(f"Tables from {schema_data_hive} schema", spark.sql(f"""
show tables from {hive_catalog}.{schema_data_hive}
""").show())

df = spark.sql(f"SELECT count(*) FROM {iceberg_catalog}.{schema_netezza_offload}.dim_exchange")
print("Number of rows in exchange table", df.show())



#------------------Create 2024 holding table based on the tables offloaded from Netezza--------------


##---------------------------------------Load data-----------------------------------------------------
# Load Netezza offloaded tables using spark sql
# We refer to a table via `catalog_name.schema_name.table_name`
# Load tables
fact_df = spark.sql(f"SELECT * FROM {iceberg_catalog}.{schema_netezza_offload}.fact_transactions")
stock_df =  spark.sql(f"SELECT * FROM {iceberg_catalog}.{schema_netezza_offload}.dim_stock")
exchange_df = spark.sql(f"SELECT * FROM {iceberg_catalog}.{schema_netezza_offload}.dim_exchange")
date_df = spark.sql(f"SELECT * FROM {iceberg_catalog}.{schema_netezza_offload}.dim_date")



##---------------------------------------Select and aggregate data------------------------------------------------------
# Stock symbols to filter
stock_symbols = ['BAC', 'IBM', 'AMZN', 'HD']


# Select only year 2024 and only required stock symbols, create joined table
# Filter date to 2024 and join with fact
filtered_fact = fact_df.join(date_df, fact_df["date_id"] == date_df["date_id"]) \
    .filter((date_df["year"] == 2024))


# Join with stock and exchange
joined_df = filtered_fact \
    .join(stock_df, "stock_id", "left") \
    .join(exchange_df, "exchange_id", "left") \
    .filter(stock_df["stock_symbol"].isin(stock_symbols))


# Aggregated table for `account_id`, `stock_symbol` and `exchange_country` with all data from offloaded Netezza tables needed to calculate `holdings_2024`


# Group and aggregate
nz_agg_2024_stocks = joined_df.groupBy(
    "account_id", "stock_symbol", "country"
).agg(
    F.sum("quantity").alias("total_quantity"),
    F.sum("total_value").alias("total_value")
).withColumnRenamed("country", "exchange_country")



# Show the result
print("NZ Tables Aggregations",nz_agg_2024_stocks.show())

##---------------------------------------Tax liability------------------------------------------------------
# > table containing tax percentage for specific countries -> needed to calculate tax liability column
tax_liability = spark.read.format("json").load(f"s3a://{hive_bucket}/input_data_hive/tax_liability_ht/tax_liability.json")
tax_liability = tax_liability.withColumnRenamed("country", "exchange_country")
tax_liability.show()


##---------------------------------------Final holdings_2024------------------------------------------------------

# Join with stock and exchange
holdings_2024 = nz_agg_2024_stocks \
    .join(tax_liability, "exchange_country", "left") \
    .withColumn("tax_liability", F.round(F.col("total_value") * F.col("tax_percentage") / 100, 2)) \
    .select(
        F.col("account_id"),
        F.col("stock_symbol").alias("asset_ticker"),
        F.col("total_quantity").alias("holding_amt_2024"),
        F.col("tax_liability").alias("tax_liability_2024")

    )
print("Holdings for 2024", holdings_2024.show())

#---------------------------------------Total holdings table up to 2024------------------------------------------------------
# Join holdings table for up to 2023 and new holdings table for 2024


holdings_2023 = spark.sql(f"SELECT account_id, asset_ticker, holding_amt as holding_amt_2023, tax_liability as tax_liability_2023 FROM {hive_catalog}.{schema_data_hive}.holdings_up_2023_ht")
holdings_2023.show()


holdings_total = holdings_2023 \
    .join(holdings_2024, ["account_id", "asset_ticker"], "left") \
    .fillna(0) \
    .withColumn("holding_amt", F.col("holding_amt_2023") + F.col("holding_amt_2024")) \
    .withColumn("tax_liability", F.col("tax_liability_2023") + F.col("tax_liability_2024")) \
    .withColumn("holding_id", F.sha2(F.concat_ws("_", F.col("account_id"), F.col("asset_ticker")), 256)) \
    .select(
        F.col("holding_id"),
        F.col("account_id"),
        F.col("asset_ticker"),
        F.col("holding_amt"),
        F.col("tax_liability")
    )


print("Total holdings table", holdings_total.show())

#---------------------------------------Save table to iceberg catalog------------------------------------------------------
# Writing holdings_total table to `{iceberg_catalog}.{schema_data_iceberg}.holdings_table` so that it can be later used by an agent

holdings_total.writeTo(f"{iceberg_catalog}.{schema_data_iceberg}.holdings_table") \
    .using('iceberg') \
    .createOrReplace()

spark.stop()