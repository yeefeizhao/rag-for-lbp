import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

df1 = pd.read_csv('EVAL James Hill PEM Evaluation - education_materials_test.csv')
df2 = pd.read_csv('EVAL Dave Thompson PEM Evaluation - education_materials_test.csv')

combined_df = pd.concat([df1, df2])

metrics = ['Redundancy', 'Accuracy', 'Completeness']

anova_results = {}

for metric in metrics: 
    model = ols(f'{metric} ~ C(Model)', data = combined_df).fit()

    anova_table = sm.stats.anova_lm(model, typ=2)

    anova_results[metric] = anova_table

for metric, result in anova_results.items():
    print(f'ANOVA result for {metric}:\n', result)
    print('\n')