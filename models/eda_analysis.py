import pandas as pd

# load dataset from sheet "E Comm"
df = pd.read_excel(
    "data/raw/E Commerce Dataset.xlsx",
    sheet_name="E Comm"
)

print("Dataset shape:", df.shape)

print("\nColumns:")
print(df.columns)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nTarget distribution:")
print(df["Churn"].value_counts())