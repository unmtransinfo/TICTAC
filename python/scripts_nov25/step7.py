from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

# Initialize Spark session with optimized memory and shuffle configurations
spark = SparkSession.builder \
    .appName("Merge_Disease_and_Drug_Associations") \
    .config("spark.executor.memory", "16g") \
    .config("spark.driver.memory", "16g") \
    .config("spark.sql.shuffle.partitions", "400") \
    .getOrCreate()

# Step 1: Load the first dataset (disease-gene associations)
print("Loading disease_gene_association.parquet...")
disease_gene_association = spark.read.parquet("disease_gene_association.parquet").persist()

# Step 2: Load the second dataset (drug-target interaction data)
print("Loading sddt_links2.parquet...")
sddt_links2 = spark.read.parquet("sddt_links2.parquet").persist()

# Step 3: Merge the datasets on the `doid_uniprot` column
# Use a broadcast join to optimize the merge if `sddt_links2` is significantly smaller
print("Merging datasets on `doid_uniprot` column...")
merged_df = disease_gene_association.join(
    broadcast(sddt_links2),  # Broadcasting `sddt_links2` for optimization
    on="doid_uniprot",
    how="inner"
)

# Step 4: Save the merged dataset
output_path = "merged_disease_drug_association.parquet"
print(f"Saving merged dataset to {output_path}...")
merged_df.write.mode("overwrite").partitionBy("gene_symbol").parquet(output_path)

# Step 5: Stop the Spark session
spark.stop()
print("Merge complete. Spark session stopped.")
