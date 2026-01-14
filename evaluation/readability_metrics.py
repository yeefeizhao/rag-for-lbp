import csv
from collections import defaultdict

def permute_grade(score):
    # FRE read_grade level
    grade = '4th Grade or Below'
    if round(score, 0) >= 90:
        grade = '5th Grade'
    elif round(score, 0) >= 80:
        grade = '6th Grade'
    elif round(score, 0) >= 70:
        grade = '7th Grade'
    elif round(score, 0) >= 60:
        grade = '9th Grade'
    elif round(score, 0) >= 50:
        grade = '11th Grade'
    elif round(score, 0) >= 30:
        grade = 'College Level'
    else:
        grade = 'College Graduate'
    return grade

sums = defaultdict(lambda: {'FK_Readability': 0.0, 'FK_Grade': 0.0, 'FK_CalcGrade': 0.0, 'Num_Words': 0.0, 'Num_Syllables': 0.0, 'Num_Sentences': 0.0, 'count': 0})

with open('readability_output.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for row in reader:
        model = row['Model']
        sums[model]['FK_Readability'] += float(row['FK_Readability'])
        sums[model]['FK_CalcGrade'] += float(row['FK_CalcGrade'])
        sums[model]['Num_Words'] += float(row['Num_Words'])
        sums[model]['Num_Syllables'] += float(row['Num_Syllables'])
        sums[model]['Num_Sentences'] += float(row['Num_Sentences'])
        sums[model]['count'] += 1

averages = []
for model, values in sums.items():
    avg_fk_readability = values['FK_Readability'] / values['count']
    avg_fk_grade = permute_grade(avg_fk_readability)
    avg_fk_calcgrade = values['FK_CalcGrade'] / values['count']
    avg_num_words = values['Num_Words'] / values['count']
    avg_num_syllables = values['Num_Syllables'] / values['count']
    avg_num_sentences = values['Num_Sentences'] / values['count']
    
    averages.append({
        'Model': model,
        'Avg_FK_Readability': avg_fk_readability,
        'Avg_FK_Grade': avg_fk_grade,
        'Avg_FK_CalcGrade': avg_fk_calcgrade,
        'Avg_Num_Words': avg_num_words,
        'Avg_Num_Syllables': avg_num_syllables,
        'Avg_Num_Sentences': avg_num_sentences
    })

with open('model_fk_averages.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Model', 'Avg_FK_Readability', 'Avg_FK_Grade', 'Avg_FK_CalcGrade', 'Avg_Num_Words', 'Avg_Num_Syllables', 'Avg_Num_Sentences']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for avg in averages:
        writer.writerow(avg)

print("Average Flesch-Kincaid scores calculated and written to 'model_fk_averages.csv'.")
