import math
from collections import defaultdict

in_file = 'data/a0-output'

DB = {}
N = 0

for pos in range(32):
    DB[pos] = defaultdict(int)

for line in open(in_file):
    if len(line) != 33:
        continue
    s = line[:-1]
    for pos in range(32):
        DB[pos][s[pos]] += 1
    N += 1

print(f'# N\t{N}')

METRICS = {}

print('## \tPOS\tENT')

for pos in range(32):
    d = DB[pos]
    ENT = 0
    for pattern in d.keys():
        p = d[pattern] / N
        ENT -= p * math.log(p, 2)
    ENT /= 4
    METRICS[pos] = ENT
    print(f'# ent\t{pos}\t{ENT}')

cs = 0
lt = -1
le = -1
ents = []

print('## \tTYPE\tSTART\tSTOP\tAVGENT')

for pos in range(32):
    ENT = METRICS[pos]
    if pos < 8:
        ents.append(ENT)
        continue

    t = 6
    if ENT < 0.025:
        t = 1
    elif ENT < 0.1:
        t = 2
    elif ENT < 0.3:
        t = 3
    elif ENT < 0.5:
        t = 4
    elif ENT < 0.9:
        t = 5

    d = False
    if pos == 8:
        d = True
    elif pos == 16:
        d = True
    elif lt > 0 and t != lt and abs(ENT - le) > 0.05:
        d = True

    if d and len(ents) > 0:
        print(f'# segment\tt{lt}\t{cs}\t{pos}\t{sum(ents)/len(ents)}')
        cs = pos
        ents = []

    ents.append(ENT)
    lt = t
    le = ENT

print(f'# segment\tt{lt}\t{cs}\t{32}\t{sum(ents)/len(ents)}')
