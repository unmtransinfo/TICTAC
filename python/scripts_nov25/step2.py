from pyspark.sql import SparkSession, functions as F

# Initialize Spark session with adjusted configurations
spark = SparkSession.builder \
    .appName("AggregationPipeline") \
    .config("spark.executor.memory", "12g") \
    .config("spark.driver.memory", "12g") \
    .config("spark.executor.cores", "4") \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

# Step 1: Load the input dataset from step1_output.parquet
print("Loading step1_output.parquet...")
df = spark.read.parquet("step1_output.parquet")

# Step 2: Round `semantic_score` and `frequency_score` to 4 decimal places
df = df.withColumn("semantic_score", F.round(F.col("semantic_score"), 4)) \
       .withColumn("frequency_score", F.round(F.col("frequency_score"), 4))

# Step 3: Perform aggregations to calculate `nDrug`, `nDiseases`, and retain `nStud` and `nct_ids`
df_aggregated = df.groupBy("disease_term", "doid", "gene_symbol", "uniprot", "doid_uniprot") \
    .agg(
        F.countDistinct("drug_name").alias("nDrug"),                        # Unique drug count per disease-gene pair
        F.countDistinct("doid").alias("nDiseases"),                         # Unique disease count per disease-gene pair
        F.first("nStud", ignorenulls=True).alias("nStud"),                  # Retain nStud from step1
        F.first("nct_ids", ignorenulls=True).alias("nct_ids"),              # Retain nct_ids from step1
        F.first("semantic_score", ignorenulls=True).alias("semantic_score"), # First non-null semantic score
        F.first("frequency_score", ignorenulls=True).alias("frequency_score") # First non-null frequency score
    )

# Step 4: Save the aggregated dataset to step2_output.parquet
output_path = "step2_output.parquet"
df_aggregated.write.mode("overwrite").parquet(output_path)
print(f"Aggregated dataset saved to '{output_path}'")

# Stop Spark session
spark.stop()
