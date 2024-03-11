import pandas as pd

input_csv_path = "datasets/train (2).csv"
output_jsonl_path = "datasets/train.jsonl"

df = pd.read_csv(input_csv_path)
df.to_json(output_jsonl_path, orient="records", lines=True)
