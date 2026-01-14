import pandas as pd

df1 = pd.read_csv('james_hill_evaluation.csv')
df2 = pd.read_csv('dave_thompson_evaluation.csv')

std_evaluator1 = df1[['Redundancy', 'Accuracy', 'Completeness']].std()
std_evaluator1.name = 'Evaluator 1'

std_evaluator2 = df2[['Redundancy', 'Accuracy', 'Completeness']].std()
std_evaluator2.name = 'Evaluator 2'

std_df = pd.concat([std_evaluator1, std_evaluator2], axis=1)

std_df.to_csv('evaluator_std.csv')

print("Standard deviations for each evaluator have been calculated and saved to 'evaluators_std.csv'.")
