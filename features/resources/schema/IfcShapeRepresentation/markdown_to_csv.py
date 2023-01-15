import pandas as pd

exclude = ['Type', 'Identifier']

with open('README.md') as f:
    rows = []
    for row in f.readlines():
        if not ('|') in row:
            continue

        if row[0] == '|':
            row = row[1:]

        clean_line = [col.strip() for col in row.split('|')]

        elem = clean_line[0]
        if elem in exclude or not any([i.isalpha() for i in elem]):
            continue
        rows.append(clean_line)
    rows = rows[:1] + rows[2:]


df = pd.DataFrame(rows)

df.to_csv('RepresentationIdentifier.csv', header=None, index=False)