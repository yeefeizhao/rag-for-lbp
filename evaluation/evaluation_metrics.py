import pandas as pd

# Read the CSV files into DataFrames
df1 = pd.read_csv('EVAL James Hill PEM Evaluation - education_materials_test.csv')
df2 = pd.read_csv('EVAL Dave Thompson PEM Evaluation - education_materials_test.csv')

# Concatenate the two DataFrames
combined_df = pd.concat([df1, df2])

# Calculate mean and standard deviation for redundancy, accuracy, and completeness for each model
grouped = combined_df.groupby('Model').agg(
    redundancy_mean=('Redundancy', 'mean'),
    redundancy_sd=('Redundancy', 'std'),
    accuracy_mean=('Accuracy', 'mean'),
    accuracy_sd=('Accuracy', 'std'),
    completeness_mean=('Completeness', 'mean'),
    completeness_sd=('Completeness', 'std')
).reset_index()

# Save the results to a new CSV file
grouped.to_csv('combined_model_statistics.csv', index=False)

print("Mean and standard deviation have been calculated from both files and saved to 'combined_model_statistics.csv'.")
