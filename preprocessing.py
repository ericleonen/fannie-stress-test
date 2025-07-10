from pyspark.sql import SparkSession, DataFrame
import pandas as pd
from pyspark.sql.functions import col, pandas_udf, lit, when, col, coalesce, round
from pyspark.sql.types import IntegerType, DoubleType, FloatType
import sys
import os

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = SparkSession.builder.getOrCreate()

COL_TO_INDEX = {
    "orig_interest_rate": 7,
    "orig_upb": 9,
    "orig_loan_term": 12,
    "orig_date": 13,
    "amortization_type": 34,
    "interest_only": 36,
    "zero_balance_code": 43,
    "zero_balance_date": 44,
    "upb_at_removal": 45,
    "foreclosure_costs": 53,
    "preservation_and_repair_costs": 54,
    "asset_recovery_costs": 55,
    "misc_holding_costs": 56,
    "holding_taxes_costs": 57,
    "net_sales_proceeds": 58,
    "credit_enhancement_proceeds": 59,
    "repurchase_make_whole_proceeds": 60,
    "other_foreclosure_proceeds": 61
}
col_names = COL_TO_INDEX.keys()
col_indexes = COL_TO_INDEX.values()

def preprocess_csv(file: str) -> DataFrame:
    # STEP ONE: Load file with selected columns and column names
    df = spark.read.csv(
        file,
        header=False,
        inferSchema=True,
        sep="|"
    ).select(
        [f"_c{i}" for i in col_indexes]
    ).toDF(*col_names)

    # STEP TWO: Filter loans that are FRMs, not interest-only, and have a zero-balance code and
    #           cast UPB to integers
    df = df.filter(
        (col("amortization_type") == "FRM") &
        (col("interest_only") == "N") &
        (col("zero_balance_code").isNotNull())
    ).drop(
        "amortization_type", "interest_only"
    ).withColumn("orig_upb", col("orig_upb").cast(IntegerType()))

    # STEP THREE: Compute cumulative interest paid
    def get_months(date: int) -> int:
        date_str = str(date).zfill(6)
        month = int(date_str[:2])
        year = int(date_str[2:])

        return month + 12*year

    @pandas_udf(DoubleType())
    def compute_cum_interest(
        principal: pd.Series,
        interest_rate: pd.Series,
        loan_term: pd.Series,
        orig_date: pd.Series,
        zero_balance_date: pd.Series
    ) -> pd.Series:
        results = []
        for P, r, n, start, end in zip(principal, interest_rate, loan_term, orig_date, zero_balance_date):
            m = get_months(end) - get_months(start)
            i = r / 12 / 100

            M = P * (i * (1 + i)**n) / ((1 + i)**n - 1)
            balance = P
            cum_interest = 0.0

            for _ in range(m):
                curr_interest = balance * i
                curr_principal = M - curr_interest
                balance -= curr_principal
                cum_interest += curr_interest
            results.append(cum_interest)

        return pd.Series(results)

    df = df.withColumn(
        "cum_interest",
        compute_cum_interest(
            df["orig_upb"],
            df["orig_interest_rate"],
            df["orig_loan_term"],
            df["orig_date"],
            df["zero_balance_date"]
        )
    ).drop("orig_interest_rate", "orig_loan_term", "orig_date", "zero_balance_date")

    # STEP FOUR: Compute LGDs for defaulted loans
    defaulted_costs_cols = [col for col in df.columns if col.endswith("_costs")]
    defaulted_proceeds_cols = [col for col in df.columns if col.endswith("_proceeds")]
    defaulted_codes = [2, 3, 9, 15, 16]
    defaulted = df["zero_balance_code"].isin(*defaulted_codes)

    defaulted_costs = None
    for c in defaulted_costs_cols:
        cost = when(defaulted, coalesce(col(c), lit(0)))
        
        if defaulted_costs is None:
            defaulted_costs = cost
        else:
            defaulted_costs += cost

    defaulted_proceeds = None
    for c in defaulted_proceeds_cols:
        proceed = when(defaulted, coalesce(col(c), lit(0)))
        
        if defaulted_proceeds is None:
            defaulted_proceeds = proceed
        else:
            defaulted_proceeds += proceed

    df = df.withColumn(
        "lgd",
        when(
            defaulted,
            (col("upb_at_removal") + defaulted_costs - defaulted_proceeds) / col("upb_at_removal")
        ).otherwise(lit(None)).alias("lgd")
    ).withColumn(
        "defaulted", 
        defaulted
    ).drop("zero_balance_code", *defaulted_costs_cols, *defaulted_proceeds_cols)

    # STEP FIVE: Compute net
    df = df.withColumn(
        "net",
        when(
            col("defaulted"), 
            col("cum_interest") - col("upb_at_removal") * col("lgd")
        ).otherwise(col("cum_interest")).alias("net")
    ).drop(
        "upb_at_removal", "cum_interest", "lgd"
    ).withColumn("net", round(col("net"), 2).cast(FloatType()))

    return df

years = [year for year in range(2020, 2024 + 1)]
quarters = [quarter for quarter in range(1, 4 + 1)]

for year in years:
    print(f"Preprocessing year={year}")
    year_df = None

    for quarter in quarters:
        print(f" - Preprocessing quarter={quarter}")
        quarter_df = preprocess_csv(f"data/{year}Q{quarter}.csv")
        year_df = quarter_df if year_df is None else year_df.union(quarter_df)

    print(f"Creating data/{year}.csv")
    year_df_pd = year_df.toPandas()
    year_df_pd.to_csv(f"data/{year}.csv", index=False)