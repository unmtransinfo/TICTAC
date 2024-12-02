from pyspark.sql import SparkSession, functions as F
import math

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Calculate_nStudyNewness_for_FullDataset") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .getOrCreate()

# Load dataset
print("Loading step3_output.parquet...")
dataset_df = spark.read.parquet("step3_output.parquet")

# Load reference dataset with study years
print("Loading aact_study_refs_trans_corrected.parquet...")
aact_refs_df = spark.read.parquet("aact_study_refs_trans_corrected.parquet")

# Step 1: Explode nct_ids in the dataset to get individual NCT IDs for each disease-gene target
dataset_df_exploded = dataset_df.select(
    "doid_uniprot", "nct_ids", F.explode("nct_ids").alias("nct_id")
)

# Step 2: Join with the reference dataset to get the year of each study
joined_df = dataset_df_exploded.join(
    aact_refs_df.select("nct_id", "year"),
    on="nct_id",
    how="left"
)

# Step 3: Calculate the age of each study (2024 is considered the present year, and studies from 2024 have age 1)
joined_df = joined_df.withColumn("study_age", F.when(F.col("year").isNotNull(), 
                                                     F.when(F.col("year") == 2024, 1)
                                                     .otherwise(2024 - F.col("year")))
                                   .otherwise(None))

# Step 4: Define the exponential decay function for study age
def calculate_weighted_age(age):
    if age is None:
        return 0.0  # return 0 weight if age is None
    if age <= 10:
        half_life = 5  # primary half-life of 5 years
    else:
        half_life = 10  # slower decay beyond 10 years
    return float(math.pow(2, -age / half_life))

# Register the function as a UDF
weighted_age_udf = F.udf(calculate_weighted_age, "double")

# Step 5: Apply the exponential decay function to compute weighted age for each study
joined_df = joined_df.withColumn("weighted_age", weighted_age_udf("study_age"))

# Step 6: Calculate nStudyNewness by summing up the weighted ages for each doid_uniprot group and rounding to 2 decimal places
nStudyNewness_df = joined_df.groupBy("doid_uniprot") \
    .agg(F.round(F.sum("weighted_age"), 2).alias("nStudyNewness"))

# Step 7: Join nStudyNewness back to the original dataset DataFrame
result_df = dataset_df.join(nStudyNewness_df, on="doid_uniprot", how="left")

# Step 8: Save the enriched dataset to step4_output.parquet
output_path = "step4_output.parquet"
result_df.write.mode("overwrite").parquet(output_path)
print(f"Output with nStudyNewness saved to '{output_path}'")

# Stop Spark session
spark.stop()
