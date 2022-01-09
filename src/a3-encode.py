in_file0 = 'data/a0-output'
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

for line in open(in_file0):
    flag = False
    codes = []
    for segment in segments:
        val = int(line[segment['start']:segment['stop']], 16)
        if val in segment['values']:
            codes.append(str(segment['values'][val]))
        else:
            for r in segment['ranges']:
                if r[0] <= val <= r[1]:
                    codes.append(str(r[2]))
                    break
            else:
                flag = True
                break
    if flag:
        continue
    print('.'.join(codes))
