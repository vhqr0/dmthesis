import numpy as np

in_file = 'data/a3-output'

a = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

db = {}

lines = []

for line in open(in_file):
    lines.append((int(x) for x in line.split('.')))

if len(lines) > 100000:
    lines = np.random.choice(lines, size=100000)

for line in lines:
    for k, v in enumerate(line):
        if k not in db:
            db[k] = []
        db[k].append(v)

for key in sorted(db.keys()):
    vals = set(db[key])
    print(f'#discrete {a[key]} {" ".join([str(x) for x in vals])}')
    print(f'#parents {a[key]} {" ".join([a[x] for x in range(key)])}')

print('exp ' + ' '.join('L' + str(x + 1) for x in range(len(db[0]))))

for key in sorted(db.keys()):
    print(f'{a[key]} {" ".join(str(x) for x in db[key])}')
