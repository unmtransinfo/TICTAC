from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Step 1: Initialize Spark Session
spark = SparkSession.builder \
    .appName("Transform AACT Study Refs") \
    .config("spark.executor.memory", "16g") \
    .config("spark.driver.memory", "16g") \
    .config("spark.executor.memoryOverhead", "2g") \
    .config("spark.sql.parquet.columnarReaderBatchSize", "1024") \
    .config("spark.sql.shuffle.partitions", "500") \
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35") \
    .getOrCreate()

# Step 2: Load `aact_study_refs.tsv` into a DataFrame
print("Loading aact_study_refs.tsv...")
aact_study_refs = spark.read.csv(
    "aact_study_refs.tsv",
    sep="\t",
    header=True,
    inferSchema=True
).select("nct_id", "reference_type", "pmid", "citation")

# Step 3: Load `merged_disease_drug_association.parquet`
print("Loading merged_disease_drug_association.parquet...")
disease_drug_assoc = spark.read.parquet("merged_disease_drug_association.parquet") \
    .select("doid_uniprot", "nct_ids")

# Step 4: Explode `nct_ids` into multiple rows
print("Exploding `nct_ids` into individual rows...")
disease_drug_assoc_exploded = disease_drug_assoc.withColumn("nct_id", explode(col("nct_ids")))

# Step 5: Perform an inner join on `nct_id`
print("Joining exploded dataset with study references...")
joined_df = disease_drug_assoc_exploded.join(
    aact_study_refs,
    on="nct_id",
    how="inner"
)

# Step 6: Select required columns
print("Selecting required columns...")
final_df = joined_df.select("doid_uniprot", "nct_id", "reference_type", "pmid", "citation")

# Step 7: Save the resulting DataFrame as Parquet
output_path = "study_ref_redundant.parquet"
print(f"Saving transformed data to {output_path}...")
final_df.write.mode("overwrite").parquet(output_path)

print("Transformation complete. Output saved successfully.")

# Stop Spark Session
spark.stop()
