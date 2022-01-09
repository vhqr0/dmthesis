import IPy

in_file = 'data/dataset.txt'

for line in open(in_file):
    if line == '\n' or line[0] == '#':
        continue
    print(hex(IPy.IP(line[:-1]).int())[2:])
