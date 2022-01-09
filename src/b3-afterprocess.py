import IPy

in_file = 'data/b2-output'

for line in open(in_file):
    print(IPy.IPint(int(line[:-1], 16), ipversion=6))
