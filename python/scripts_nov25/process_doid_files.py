from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split

def process_file(doid_number):
    # Initialize SparkSession with memory optimizations
    spark = SparkSession.builder \
        .appName("Process DOID Files with Join") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "16g") \
        .config("spark.memory.offHeap.enabled", "true") \
        .config("spark.memory.offHeap.size", "8g") \
        .config("spark.sql.shuffle.partitions", "200") \
        .getOrCreate()

    # File paths (updated to use the correct file name)
    idg_file_path = "idg_disease_drug_target.parquet"
    disease_file_path = "disease_target_association.parquet"  # Updated file name

    # Load the datasets
    print("Loading datasets...")
    idg_df = spark.read.parquet(idg_file_path).select(
        "doid_uniprot", "disease_term", "drug_name", "gene_symbol", "idgTDL"
    )
    disease_df = spark.read.parquet(disease_file_path).select(
        "doid_uniprot", "nDiseases", "nDrug", "nStud", "nPub", "nStudyNewness",
        "nPublicationWeighted", "meanRankScore", "nct_ids", "pmids", "gene_symbol"
    )

    # Extract DOID prefix for filtering
    idg_df = idg_df.withColumn("DOID_prefix", split(col("doid_uniprot"), "_").getItem(0))
    disease_df = disease_df.withColumn("DOID_prefix", split(col("doid_uniprot"), "_").getItem(0))

    # Filter both datasets by DOID prefix
    doid_prefix = f"DOID:{doid_number}"
    print(f"Filtering for DOID prefix: {doid_prefix}...")
    idg_filtered_df = idg_df.filter(col("DOID_prefix") == doid_prefix).drop("DOID_prefix")
    disease_filtered_df = disease_df.filter(col("DOID_prefix") == doid_prefix)

    # Join the filtered datasets on `doid_uniprot` and `gene_symbol`
    print("Joining the datasets...")
    joined_df = disease_filtered_df.join(
        idg_filtered_df, on=["doid_uniprot", "gene_symbol"], how="inner"
    ).select(
        "doid_uniprot", "nDiseases", "nDrug", "nStud", "nPub", "nStudyNewness",
        "nPublicationWeighted", "meanRankScore", "disease_term", "drug_name", 
        "idgTDL", "gene_symbol", "DOID_prefix"
    )

    # Repartition for better memory management
    joined_df = joined_df.repartition(100)

    # Save the joined data
    filtered_output_path = f"filtered_DOID_{doid_number}.parquet"
    print(f"Saving filtered data to {filtered_output_path}...")
    joined_df.write.mode("overwrite").parquet(filtered_output_path)

    print(f"Filtered data saved to {filtered_output_path}.")

    # Stop SparkSession
    spark.stop()

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python process_doid_files.py <DOID_number>")
        sys.exit(1)

    # Get the DOID number from command line arguments
    doid_number = sys.argv[1]
    process_file(doid_number)

