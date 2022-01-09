import toposort
import random

N = 256

in_file = 'data/a5-output'

CPD = eval(open(in_file).read())

order = toposort.toposort_flatten({k: set(v['pars']) for k, v in CPD.items()})

print('# ' + '.'.join(sorted(order)))

for _ in range(N):
    chosen = {}
    vals = {}

    for V in order:
        vertex = CPD[V]

        query = tuple(chosen[P] for P in vertex['pars'])
        if query in vertex['cpds']:
            pd = vertex['cpds'][query]
        else:
            pd = {None: vertex['cpds'][None]}

        cprob = random.random()
        ks = set(range(len(vertex['vals'])))
        for k, prob in pd.items():
            if k == None:
                continue
            cprob -= prob
            if cprob <= 0:
                break
            else:
                ks.remove(k)
        else:
            if len(ks) > 0:
                k = random.choice(list(ks))
            else:
                k = random.choice(range(vertex['vals']))

        vals[V] = vertex['vals'][k]
        chosen[V] = k

    print('.'.join(vals[k] for k in sorted(vals.keys())))
