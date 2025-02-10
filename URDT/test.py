import pandas as pd

# Load the Excel file
xlsx_file = r"D:\DJANGO\URDT\input.xlsx"  # Replace with your file name
df = pd.read_excel(xlsx_file)

# Save as CSV
csv_file = r"D:\DJANGO\URDT\output.csv"  # Replace with your desired output file name
df.to_csv(csv_file, index=False)

print(f"Conversion complete: {csv_file}")
