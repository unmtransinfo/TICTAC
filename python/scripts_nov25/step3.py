from pyspark.sql import SparkSession, functions as F

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Calculate_nPub_with_pmids_for_FullDataset") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .getOrCreate()

# Load input files
print("Loading step2_output.parquet...")
dataset_df = spark.read.parquet("step2_output.parquet")

print("Loading aact_study_refs_trans_corrected.parquet...")
aact_refs_df = spark.read.parquet("aact_study_refs_trans_corrected.parquet")

# Step 1: Explode the nct_ids column to create individual rows for each NCT ID
dataset_df_exploded = dataset_df.select(
    "doid_uniprot", F.explode("nct_ids").alias("nct_id")
)

# Step 2: Join with the publication references to associate NCT IDs with PMIDs
joined_df = dataset_df_exploded.join(
    aact_refs_df.select("nct_id", "pmid"),
    on="nct_id",
    how="left"
)

# Step 3: Aggregate by doid_uniprot to create a `pmids` column (unique list of PMIDs)
nPub_df = joined_df.groupBy("doid_uniprot") \
    .agg(
        F.countDistinct("pmid").alias("nPub"),  # Count distinct PMIDs for each doid_uniprot
        F.collect_set("pmid").alias("pmids")   # Collect unique PMIDs as a set for each doid_uniprot
    )

# Step 4: Join the aggregated results back with the original dataset
result_df = dataset_df.join(nPub_df, on="doid_uniprot", how="left")

# Step 5: Save the result to step3_output.parquet
output_path = "step3_output.parquet"
result_df.write.mode("overwrite").parquet(output_path)
print(f"Output with nPub and pmids saved to '{output_path}'")

# Stop Spark session
spark.stop()
