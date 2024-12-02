from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Initialize Spark session with optimized memory and configurations
spark = SparkSession.builder \
    .appName("DiseaseTargetAssociation") \
    .config("spark.executor.memory", "16g") \
    .config("spark.driver.memory", "16g") \
    .config("spark.executor.cores", "2") \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "100") \
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC -XX:InitiatingHeapOccupancyPercent=35") \
    .getOrCreate()

# Reduce logging verbosity for performance improvement
spark.sparkContext.setLogLevel("ERROR")

# Load Data with optimized repartitioning
print("Loading data...")
sddt_links_df = spark.read.parquet('sddt_links.parquet').repartition("doid")

# Filter out rows with missing values in critical columns
sddt_links_df = sddt_links_df.filter(
    (F.col("disease_term").isNotNull()) &
    (F.col("drug_name").isNotNull()) &
    (F.col("gene_symbol").isNotNull())
).persist()  # Persisting intermediate data to optimize memory usage

print("Data loaded and filtered successfully.\n")

# Step 1: Create `doid_uniprot` column for disease-target association
sddt_links_df = sddt_links_df.withColumn("doid_uniprot", F.concat(F.col("doid"), F.lit("_"), F.col("uniprot")))

# Step 2: Count unique `nct_id` values per `doid_uniprot` to get `nStud`
nct_id_count_df = sddt_links_df.groupBy("doid_uniprot") \
    .agg(F.countDistinct("nct_id").alias("nStud"),
         F.collect_set("nct_id").alias("nct_ids"))

# Join the `nStud` and `nct_ids` back to the main DataFrame
sddt_links_df = sddt_links_df.join(nct_id_count_df, on="doid_uniprot", how="left")

# Save output with the new columns `doid_uniprot`, `nStud`, and `nct_ids`
output_path = "step2.parquet/"
sddt_links_df.select("disease_term", "doid", "drug_name", "molecule_chembl_id", 
                     "gene_symbol", "uniprot", "doid_uniprot", "nStud", "nct_ids") \
    .write.partitionBy("doid").parquet(output_path, mode="overwrite")

print(f"Final results saved to '{output_path}'")
spark.stop()
