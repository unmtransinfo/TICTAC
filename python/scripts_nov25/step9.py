from pyspark.sql import SparkSession

# Initialize Spark Session with optimized configurations
spark = SparkSession.builder \
    .appName("Optimized Deduplication with Local Spill") \
    .config("spark.executor.memory", "16g") \
    .config("spark.driver.memory", "16g") \
    .config("spark.executor.memoryOverhead", "4g") \
    .config("spark.sql.parquet.columnarReaderBatchSize", "512") \
    .config("spark.sql.shuffle.partitions", "1000") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.files.maxPartitionBytes", "128m") \
    .config("spark.memory.storageFraction", "0.5") \
    .config("spark.local.dir", "./spark_local_dir") \
    .getOrCreate()

# Reduce logging verbosity
spark.sparkContext.setLogLevel("ERROR")

# Step 1: Load the Parquet File
print("Loading transformed study references dataset...")
df = spark.read.parquet("study_ref_redundant.parquet")

# Step 2: Deduplicate data by specified columns
print("Deduplicating the dataset...")
df_deduplicated = df.dropDuplicates(subset=["doid_uniprot", "nct_id", "reference_type", "pmid"]).persist()

# Step 3: Set Local Checkpoint Directory
checkpoint_dir = "./spark_checkpoint_dir"  # Local directory for checkpointing
print(f"Setting checkpoint directory to '{checkpoint_dir}'...")
spark.sparkContext.setCheckpointDir(checkpoint_dir)

print("Checkpointing intermediate results...")
df_deduplicated = df_deduplicated.checkpoint()

# Step 4: Save the deduplicated dataset in smaller partitions
output_path = "study_refs.parquet"
print(f"Saving deduplicated dataset to '{output_path}'...")
df_deduplicated.repartition(100).write.partitionBy("doid_uniprot").parquet(output_path, mode="overwrite")

print("Deduplication completed and results saved successfully.")

# Stop the Spark session
spark.stop()
