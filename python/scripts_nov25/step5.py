from pyspark.sql import SparkSession, functions as F

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Calculate_nPublicationWeighted_for_FullDataset") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .getOrCreate()

# Step 1: Load the dataset and reference data
print("Loading step4_output.parquet...")
dataset_df = spark.read.parquet("step4_output.parquet")

print("Loading aact_study_refs_trans_corrected.parquet...")
aact_refs_df = spark.read.parquet("aact_study_refs_trans_corrected.parquet")

# Step 2: Explode the nct_ids column
dataset_df_exploded = dataset_df.select(
    "doid_uniprot", F.explode("nct_ids").alias("nct_id")
)

# Step 3: Join with the reference data to bring in reference_type
joined_df = dataset_df_exploded.join(
    aact_refs_df.select("nct_id", "reference_type"),
    on="nct_id",
    how="left"
)

# Step 4: Define the weight mapping for reference types
# Weight mapping:
# 0.0 -> Result publications (weight = 1.0)
# 1.0 -> Background publications (weight = 0.5)
# 2.0 -> Derived publications (weight = 0.25)
weight_mapping = {
    0.0: 1.0,
    1.0: 0.5,
    2.0: 0.25
}
weight_expr = F.create_map([F.lit(x) for item in weight_mapping.items() for x in item])

# Step 5: Add a weighted column based on reference_type
weighted_df = joined_df.withColumn("weighted_type", weight_expr[F.col("reference_type")])

# Step 6: Calculate nPublicationWeighted by summing weighted values per doid_uniprot
nPublicationWeighted_df = weighted_df.groupBy("doid_uniprot") \
    .agg(F.sum("weighted_type").alias("nPublicationWeighted"))

# Step 7: Join the nPublicationWeighted result back to the original dataset
result_df = dataset_df.join(nPublicationWeighted_df, on="doid_uniprot", how="left")

# Step 8: Save the result to step5_output.parquet
output_path = "step5_output.parquet"
result_df.write.mode("overwrite").parquet(output_path)
print(f"Output with nPublicationWeighted saved to '{output_path}'")

# Stop Spark session
spark.stop()
