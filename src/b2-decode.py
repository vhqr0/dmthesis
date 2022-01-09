import random

in_file1 = 'data/b1-output'
in_file2 = 'data/a2-output'

segments = []

sname = None
sstart = 0
sstop = 0
scode = 0
svalues = {}
sranges = []

for line in open(in_file2):
    d = line.split()
    if line[0].isalpha():
        if sname:
            segments.append({
                'name': sname,
                'start': sstart,
                'stop': sstop,
                'code': scode,
                'values': svalues,
                'ranges': sranges
            })
        sname = d[0][:-1]
        sstart = int(d[1])
        sstop = int(d[3])
        scode = 0
        svalues = {}
        sranges = []
    elif line[0] == ' ':
        svalues[int(d[0], 16)] = scode
        scode += 1
    elif line[0] == '*':
        r = [int(x, 16) for x in d[1].split('-')]
        sranges.append((r[0], r[1], scode))
        scode += 1
    else:
        raise Exception('parse error: ' + line)
segments.append({
    'name': sname,
    'start': sstart,
    'stop': sstop,
    'code': scode,
    'values': svalues,
    'ranges': sranges
})

for line in open(in_file1):
    if line[0] == '#':
        continue
    codes = []
    for val, segment in zip(line.split('.'), segments):
        code = int(val)
        for k, v in segment['values'].items():
            if code == v:
                code = k
                break
        else:
            for r in segment['ranges']:
                if code == r[2]:
                    code = random.randint(r[0], r[1])
                    break
            else:
                raise Exception('parse error: ' + line)
        codes.append((f'%0{segment["stop"] - segment["start"]}x') % code)
    print(''.join(codes))
