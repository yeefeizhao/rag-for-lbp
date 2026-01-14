import csv
from fkscore import fkscore

"""
Flesch Reading Ease:
In the Flesch reading-ease test, higher scores indicate material that is easier to read; lower numbers mark passages that are more difficult to read.
The formula for the Flesch reading-ease score (FRES) test is:
206.835 - (1.015 * (total words / total sentences)) - (84.6 * (total syllables / total words))
The score is a float number rounded to 3 decimal places.
Grade level can be permuted from the Flesch Reading Ease score:
100.00–90.00 - 5th grade - Very easy to read. Easily understood by an average 11-year-old student.
90.0–80.0 - 6th grade Easy to read - Conversational English for consumers.
80.0–70.0 - 7th grade - Fairly easy to read.
70.0–60.0 - 8th & 9th grade - Plain English. Easily understood by 13- to 15-year-old students.
60.0–50.0 - 10th to 12th grade - Fairly difficult to read.
50.0–30.0 - College - Difficult to read.
30.0–10.0 - College graduate - Very difficult to read. Best understood by university graduates.
10.0–0.0 - Professional - Extremely difficult to read. Best understood by subject-matter experts.


Flesch Kincaid Grade Level:
These readability tests are used extensively in the field of education. The "Flesch–Kincaid Grade Level Formula" presents a score as a U.S. grade level, making it easier to assess audience.
It can also mean the number of years of education generally required to understand this text, most relevant when the formula results in a number greater than 10.
The reason to use the calculated grade level versus the permuted table is when there is potential for text to be outside the minimum and maximum table lookup.
Note there is often a difference between the permuted grade level and the calculated grade level.
The grade level is calculated with the following formula:
(0.39 * (total words / total sentences)) + (11.8 * (total syllables / total words)) -15.59
The calculated grade is a float number rounded to 3 decimal places.


Text Statistics:
Number of words
Number of syllables
Number of sentences
"""

with open('final_education_materials.csv', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    results = []

    for row in reader:
        fk_score = fkscore(row['Answer'])

        results.append({
            'Model': row['Model'],
            'FK_Readability': fk_score.score['readability'],
            'FK_Grade': fk_score.score['read_grade'],
            'FK_CalcGrade': fk_score.score['calc_grade'],
            'Num_Words': fk_score.stats['num_words'],
            'Num_Syllables': fk_score.stats['num_syllables'],
            'Num_Sentences': fk_score.stats['num_sentences']
        })

with open('raw_data_readability_output.csv', 'w', newline='', encoding='utf-8') as file:
    headers = ['Model', 'FK_Readability', 'FK_Grade', 'FK_CalcGrade', 'Num_Words', 'Num_Syllables', 'Num_Sentences']
    writer = csv.DictWriter(file, fieldnames=headers)

    writer.writeheader()
    for result in results:
        writer.writerow(result)

print('Scores calculated and saved to raw_data_readability_output.csv')