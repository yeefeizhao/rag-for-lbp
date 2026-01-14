import pandas as pd
import pingouin as pg

# Load CSV files from two evaluators
df1 = pd.read_csv('EVAL James Hill PEM Evaluation - education_materials_test.csv')
df2 = pd.read_csv('EVAL Dave Thompson PEM Evaluation - education_materials_test.csv')

# Add evaluator identifiers
df1['evaluator'] = 'evaluator_1'
df2['evaluator'] = 'evaluator_2'

# Combine the two dataframes
combined_df = pd.concat([df1, df2])

# Calculate ICC for each metric: Redundancy, Accuracy, and Completeness
metrics = ['Redundancy', 'Accuracy', 'Completeness']
icc_results = {}

for metric in metrics:
    # Compute ICC
    icc = pg.intraclass_corr(data=combined_df, targets='Model', raters='evaluator', ratings=metric)
    icc_results[metric] = icc

# Print ICC results for each metric
for metric, result in icc_results.items():
    print(f"Intraclass Correlation Coefficient for {metric}:\n", result)
