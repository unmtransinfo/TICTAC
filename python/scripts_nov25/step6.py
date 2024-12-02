from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import FloatType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Reintroduce_Columns_and_Split_Data") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .getOrCreate()

# Step 1: Load the input dataset
print("Loading step5_output.parquet...")
df = spark.read.parquet("step5_output.parquet")

# List of numerical variables for ranking
variables = [
    "nDiseases", "nDrug", "nStud", "nPub", "nStudyNewness", "nPublicationWeighted"
]

# Step 2: Rank each variable across all associations
for var in variables:
    rank_col = f"{var}_rank"
    window = Window.orderBy(F.desc(var))  # Ranking in descending order
    df = df.withColumn(rank_col, F.rank().over(window))

# Step 3: Calculate meanRank as the average rank of the variables
rank_cols = [F.col(f"{var}_rank") for var in variables]
df = df.withColumn("meanRank", sum(rank_cols) / len(rank_cols))

# Step 4: Calculate percentile rank and meanRankScore
percentile_window = Window.orderBy("meanRank")
df = df.withColumn("percentile_meanRank", F.percent_rank().over(percentile_window))
df = df.withColumn("meanRankScore", (100 - (F.col("percentile_meanRank") * 100)).cast(FloatType()))

# Step 5: Create `disease_target_association` dataset
disease_target_association = df.select(
    "doid_uniprot", "gene_symbol", "nDiseases", "nDrug", "nStud",
    "nPub", "nStudyNewness", "nPublicationWeighted", "meanRankScore", "nct_ids", "pmids"
)

# Step 6: Create `ranking_info` dataset
ranking_info = df.select(
    "doid_uniprot", "meanRank", "percentile_meanRank", "meanRankScore",
    *[f"{var}_rank" for var in variables]
)

# Step 7: Save the results to output Parquet files
disease_target_association.write.mode("overwrite").parquet("disease_target_association.parquet")
ranking_info.write.mode("overwrite").parquet("ranking_info.parquet")
print("Data split into disease_target_association and ranking_info tables.")

# Stop the Spark session
spark.stop()
