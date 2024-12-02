import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract

def filter_and_save_data(doid_uniprot_value, input_file, output_file):
    # Initialize Spark session with configurations for large data
    spark = SparkSession.builder \
        .appName("ProvenanceFilter") \
        .config("spark.executor.memory", "16g") \
        .config("spark.driver.memory", "16g") \
        .getOrCreate()

    # Load the Parquet file
    print(f"Loading the dataset from {input_file}...")
    df = spark.read.parquet(input_file)
    print(f"Total rows in dataset: {df.count()}")

    # Ensure the filter value matches the expected format
    if not doid_uniprot_value.startswith("DOID:"):
        doid_uniprot_value = f"DOID:{doid_uniprot_value}"

    # Extract the DOID prefix for filtering
    df = df.withColumn("DOID_prefix", regexp_extract(df.doid_uniprot, r"^DOID:\d+", 0))

    # Check for partial matches
    partial_matches = df.filter(df.doid_uniprot.contains(doid_uniprot_value.split(":")[1]))
    print(f"Rows with partial matches for '{doid_uniprot_value.split(':')[1]}': {partial_matches.count()}")
    partial_matches.select("doid_uniprot").distinct().show(100, truncate=False)

    # Filter the DataFrame based on the given `doid_uniprot` value
    print(f"Filtering for doid_uniprot: {doid_uniprot_value}...")
    filtered_df = df.filter(df.DOID_prefix == doid_uniprot_value)

    matching_rows = filtered_df.count()
    print(f"Rows matching the filter: {matching_rows}")

    if matching_rows == 0:
        print("Warning: No rows match the filter. Exiting.")
        spark.stop()
        sys.exit(0)

    # Ensure a safe file name
    safe_output_file = output_file.replace(":", "_")

    # Save the filtered DataFrame to a Parquet file
    print(f"Saving the filtered data to {safe_output_file}...")
    filtered_df.write.parquet(safe_output_file, mode="overwrite")
    print(f"Filtering completed. File saved as {safe_output_file}.")

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python provenance_filter.py <doid_uniprot_value>")
        sys.exit(1)

    doid_uniprot_value = sys.argv[1]
    input_file = "study_refs.parquet"
    output_file = f"{doid_uniprot_value}_provenance.parquet"

    filter_and_save_data(doid_uniprot_value, input_file, output_file)

