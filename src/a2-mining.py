import math
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict

in_file0 = 'data/a0-output'
in_file1 = 'data/a1-output'

SL = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

segments = []

for line in open(in_file1):
    if not line.startswith('# segment\t'):
        continue
    d = line[:-1].split('\t')
    segments.append({'start': int(d[2]), 'stop': int(d[3]), 'vals': []})

for line in open(in_file0):
    if len(line) != 33:
        continue
    s = line[:-1]
    for segment in segments:
        segment['vals'].append(int(s[segment['start']:segment['stop']], 16))


def pp(vals, counts, N, L):
    if len(counts) == 0:
        return False
    rv = False
    indexer = counts.argsort()[::-1]
    for u, c in zip(vals[indexer], counts[indexer]):
        pcnt = 100 * c / N
        if pcnt < 0.005:
            continue
        print((f'  %0{L}x') % (u) + ' ' * (33 - L) + f'{pcnt}%')
        rv = True
    return rv


def rpp(vals, counts, N, L):
    if len(counts) == 0:
        return False
    rv = False

    if len(counts > 4):
        q1, q3 = np.percentile(counts, [25, 75])
        T = min(0.1 * N, max(q3 + 1.5 * (q3 - q1), 0.02 * N))
        hhs = counts > T
        rv = pp(vals[hhs], counts[hhs], N, L)
        vals = vals[~hhs]
        counts = counts[~hhs]

    pcnt = 100 * sum(counts) / N
    if pcnt < 0.05:
        return rv
    if len(vals) < 5:
        rv |= pp(vals, counts, N, L)
    else:
        print((f'* %0{L}x-%0{L}x') % (vals.min(), vals.max()) + ' ' *
              (32 - 2 * L) + f'{pcnt}%')
        rv = True

    return rv


def metric(p1, p2):
    bdiff = math.fabs(p2[0] - p1[0])
    pdiff = math.fabs(math.log(p2[2], 13) - math.log(p1[2], 13))
    return 0.25 * bdiff + 50 * pdiff


for n, segment in enumerate(segments):
    print(f'{SL[n]}: {segment["start"]} - {segment["stop"]}')
    L = segment['stop'] - segment['start']
    P = 1 / (2**(4 * L))
    if len(segment['vals']) > 50000:
        vals = np.random.choice(segment['vals'], size=50000)
    else:
        vals = np.asarray(segment['vals'])
    N = len(vals)
    unique, counts = np.unique(vals, return_counts=True)

    if len(counts) > 10:
        q1, q3 = np.percentile(counts, [25, 75])
        T = min(0.1 * N, max(q3 + 1.5 * (q3 - q1), P * N))
        hhs = counts > T
        nhhs = ~hhs

        if sum(hhs) > 10:
            indexer = counts.argsort()[::-1]
            t10 = max(2, counts[indexer[9]])
            hhs = counts >= t10
            nhhs = ~hhs

            if sum(hhs) > 10:
                hhs = indexer[:10]
                nhhs = indexer[10:]
    else:
        hhs = counts > max(2, 0.001 * N)
        nhhs = ~hhs

    hhunique = unique[hhs]
    hhcounts = counts[hhs]
    unique2 = unique[nhhs]
    counts2 = counts[nhhs]

    pp(hhunique, hhcounts, N, L)

    if sum(counts2) < 0.001 * N:
        continue
    elif len(counts2) < 5:
        pp(unique2, counts2, N, L)
        continue

    if L >= 2:
        dbscan = DBSCAN(eps=L**3, min_samples=5)
        regions = dbscan.fit_predict(unique2.reshape(-1, 1))
        labels = set(regions)
        left = sum(counts2)

        for label in labels:
            rvals = unique2[regions == label]
            rcounts = counts2[regions == label]

            if label == -1:
                continue
            elif sum(rcounts) < 0.001 * N:
                regions[regions == label] = -1
                continue

            observedc = sum(rcounts)
            expectedc = (rvals.max() - rvals.min()) / (2**(4 * L) - 1) * left
            density = observedc / expectedc
            if density < 100:
                regions[regions == label] = -1
                continue
            rpp(rvals, rcounts, N, L)

        unique3 = unique2[regions == -1]
        counts3 = counts2[regions == -1]
    else:
        unique3 = unique2
        counts3 = counts2

    if L >= 2 and len(counts3) > 1:
        bincount = min(256, 2**(4 * L))
        hist, bins = np.histogram(unique3, weights=counts3, bins=bincount)
        step = bins[1] - bins[0]

        data = np.asarray((range(len(hist)), bins[:-1], hist / N)).T
        data = data[data[:, 2] > 0]

        dbscan = DBSCAN(eps=5, min_samples=5, metric=metric)
        regions = dbscan.fit_predict(data)
        labels = set(regions)

        cregions = []
        for label in labels:
            rbins = data[regions == label, 1]
            rfreqs = data[regions == label, 2]

            if label == -1:
                continue

            if len(rbins) < 5 or sum(rfreqs) < 0.1:
                regions[regions == label] = -1
                continue

            start = rbins.min()
            stop = rbins.max() + step
            avg = rfreqs.mean()
            cregions.append((start, stop, avg))

        if len(cregions) > 0:
            cregions = np.array(cregions)
            cregions = list(cregions[np.argsort(cregions[:, 0])])

            i = 0
            while i + 1 < len(cregions):
                cur = cregions[i]
                nxt = cregions[i + 1]

                if nxt[0] < cur[1]:
                    if nxt[2] > cur[2]:
                        if cur[1] > nxt[1]:
                            cregions.insert(i + 2,
                                            np.array([nxt[1], cur[1], cur[2]]))
                        cur[1] = nxt[0]
                    else:
                        nxt[0] = cur[1]
                i += 1

            for cregion in cregions:
                indexer = (unique3 >= cregion[0]) & (unique3 <= cregion[1])
                rvals = unique3[indexer]
                rcounts = counts3[indexer]
                if rpp(rvals, rcounts, N, L):
                    unique3 = unique3[~indexer]
                    counts3 = counts3[~indexer]

    rpp(unique3, counts3, N, L)
