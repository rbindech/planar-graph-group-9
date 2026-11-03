"""
Reliability tests for both planarity algorithms.

1) Known graphs: reads tests.txt, where each graph is preceded by a comment
   '# Graph k: <name> -> expected: PLANAR / NON-PLANAR'.
2) Random graphs (only if networkx is installed): networkx.check_planarity is
   used as a reference ("oracle") to compare our answers on many graphs.

Usage:  python test_planarity.py            (tests.txt + 2000 random graphs)
        python test_planarity.py my_file 500
"""

import sys
import random

from Left_Right import PlanarityChecker
from DMP import DMPPlanarityChecker

ALGOS = {
    "Left-Right": PlanarityChecker,
    "DMP": DMPPlanarityChecker,
}


def build(algo_class, n, edges):
    g = algo_class(n)
    for u, v in edges:
        g.add_edge(u, v)
    return g


def read_test_file(filename):
    """Returns a list of (name, expected, n, edges)."""
    with open(filename) as f:
        lines = [l.strip() for l in f if l.strip()]

    tests, name, expected, i = [], None, None, 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            if "expected:" in line:
                name = line.split(":", 1)[1].split("->")[0].strip()
                expected = "NON-PLANAR" not in line.split("expected:")[1]
            i += 1
            continue
        n, m = map(int, line.split())
        edges = [tuple(map(int, lines[i + 1 + k].split())) for k in range(m)]
        tests.append((name, expected, n, edges))
        i += 1 + m
    return tests


def test_known_graphs(filename):
    print(f"=== Known graphs ({filename}) ===")
    tests = read_test_file(filename)
    failures = {a: [] for a in ALGOS}

    header = f"{'#':>3}  {'Graph':<42} {'Expected':<11}" + "".join(f"{a:<12}" for a in ALGOS)
    print(header)
    print("-" * len(header))
    for k, (name, expected, n, edges) in enumerate(tests, start=1):
        row = f"{k:>3}  {name[:42]:<42} {'PLANAR' if expected else 'NON-PLANAR':<11}"
        for algo, cls in ALGOS.items():
            try:
                ok = build(cls, n, edges).is_planar() == expected
            except Exception as e:  # a crash counts as a failure
                ok = False
                name = f"{name} [crash: {type(e).__name__}]"
            row += f"{'ok' if ok else 'FAIL':<12}"
            if not ok:
                failures[algo].append(f"#{k} {name}")
        print(row)

    print()
    for algo in ALGOS:
        nb_ok = len(tests) - len(failures[algo])
        print(f"{algo}: {nb_ok}/{len(tests)} correct")
        for f in failures[algo]:
            print(f"   FAIL {f}")
    print()


def test_random_graphs(nb_graphs):
    try:
        import networkx as nx
    except ImportError:
        print("networkx not installed: random tests skipped (pip install networkx)")
        return

    print(f"=== {nb_graphs} random graphs, compared with networkx ===")
    random.seed(42)
    errors = {a: 0 for a in ALGOS}
    smallest = {a: None for a in ALGOS}

    for t in range(nb_graphs):
        n = random.randint(1, 15)
        G = nx.gnp_random_graph(n, random.random() * 0.6, seed=t)
        edges = list(G.edges())
        expected = nx.check_planarity(G)[0]
        for algo, cls in ALGOS.items():
            try:
                ok = build(cls, n, edges).is_planar() == expected
            except Exception:
                ok = False
            if not ok:
                errors[algo] += 1
                if smallest[algo] is None or len(edges) < len(smallest[algo][1]):
                    smallest[algo] = (n, edges, expected)

    for algo in ALGOS:
        print(f"{algo}: {nb_graphs - errors[algo]}/{nb_graphs} correct")
        if smallest[algo]:
            n, edges, expected = smallest[algo]
            print(f"   smallest wrong graph: n={n}, expected "
                  f"{'PLANAR' if expected else 'NON-PLANAR'}, edges={edges}")
    print()


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "tests.txt"
    nb_random = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    test_known_graphs(filename)
    test_random_graphs(nb_random)
