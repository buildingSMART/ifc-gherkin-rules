import itertools
import json
import operator
from .main import run

def wrap(n):
    def inner(it):
        while it:
            lens = list(map(len, it))
            csum = [sum(lens[:i+1]) for i in range(len(lens))]
            amnt = sum(a+b<n for a, b in zip(csum, itertools.count()))
            yield " ".join(it[0:amnt])
            it = it[amnt:]
    return inner

if __name__ == "__main__":
    import sys
    results = sorted(run(*(v for v in sys.argv[1:] if not v.startswith("--"))))
    if "--json" in sys.argv:
        json.dump(results, sys.stdout)
    for k, rs in itertools.groupby(results, operator.itemgetter(0)):
        rs = list(rs)
        print("Feature:", k)
        print("    URL:", rs[0][1])
        print()
        for k, rs in itertools.groupby(rs, operator.itemgetter(2)):
            print("   Step:", k)
            print()

            for r in rs:
                print("       *", r[3])
                for ln in wrap(80)(r[4].split(' ')):
                    print("        ", ln)
                print()
