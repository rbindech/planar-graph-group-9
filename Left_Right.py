import sys

# Bump up recursion limit just in case we hit deep DFS trees
sys.setrecursionlimit(10000)


def empty(interval):
    return interval[0] is None and interval[1] is None


class PlanarityChecker:
    def __init__(self, num_vertices):
        self.V = num_vertices
        self.adj = [[] for _ in range(num_vertices)]

    def add_edge(self, u, v):
        if u != v:            # skip self-loops, they don't affect planarity
            self.adj[u].append(v)
            self.adj[v].append(u)

    #  Phase 1: DFS orientation + compute lowpt / lowpt2 / nesting

    def _orient(self, v):
        e = self.parent_edge[v]
        for w in self.adj[v]:
            vw = (v, w)
            if vw in self.seen or (w, v) in self.seen:   # already oriented
                continue
            self.seen.add(vw)
            self.out[v].append(w)
            self.lowpt[vw] = self.lowpt2[vw] = self.height[v]

            if self.height[w] is None:      # tree edge: go deeper
                self.parent_edge[w] = vw
                self.height[w] = self.height[v] + 1
                self._orient(w)
            else:                 # back edge: hit an ancestor
                self.lowpt[vw] = self.height[w]

            # Brandes' nesting formula (chordal edges get +1)
            self.nesting[vw] = 2 * self.lowpt[vw] + (self.lowpt2[vw] < self.height[v])

            if e is not None:                            # update lowpts of parent edge
                if self.lowpt[vw] < self.lowpt[e]:
                    self.lowpt2[e] = min(self.lowpt[e], self.lowpt2[vw])
                    self.lowpt[e] = self.lowpt[vw]
                elif self.lowpt[vw] > self.lowpt[e]:
                    self.lowpt2[e] = min(self.lowpt2[e], self.lowpt[vw])
                else:
                    self.lowpt2[e] = min(self.lowpt2[e], self.lowpt2[vw])


    #  Phase 3: test Left / Right side constraints

    def _conflicting(self, interval, b):
        return not empty(interval) and self.lowpt[interval[1]] > self.lowpt[b]

    def _test(self, v):
        e = self.parent_edge[v]
        for i, w in enumerate(self.out[v]):
            ei = (v, w)
            self.bottom[ei] = len(self.S)

            if ei == self.parent_edge[w]:    # tree edge: recurse
                if not self._test(w):
                    return False
            else:         # back edge: push to stack
                self.lowpt_edge[ei] = ei
                self.S.append([[None, None], [ei, ei]])

            if self.lowpt[ei] < self.height[v]:   # ei has returning back edges
                if i == 0:
                    self.lowpt_edge[e] = self.lowpt_edge[ei]
                elif not self._merge(ei, e):
                    return False

        if e is not None:
            self._trim(e)
        return True

    def _merge(self, ei, e):
        """Add side constraints for edge ei. Returns False if conflict found."""
        S, ref, lowpt = self.S, self.ref, self.lowpt
        P = [[None, None], [None, None]]      # [left, right]

        # Merge back edges of ei into right side of P
        while True:
            Q = S.pop()
            if not empty(Q[0]):
                Q.reverse()
            if not empty(Q[0]):     # conflict on both sides -> impossible
                return False
            if lowpt[Q[1][0]] > lowpt[e]:
                if empty(P[1]):
                    P[1] = Q[1][:]
                else:
                    ref[P[1][0]] = Q[1][1]
                P[1][0] = Q[1][0]
            else:
                ref[Q[1][0]] = self.lowpt_edge[e]
            if len(S) == self.bottom[ei]:
                break

        # Merge edges conflicting with ei into left side of P
        while S and (self._conflicting(S[-1][0], ei) or self._conflicting(S[-1][1], ei)):
            Q = S.pop()
            if self._conflicting(Q[1], ei):
                Q.reverse()
            if self._conflicting(Q[1], ei):    # trapped on both sides -> impossible
                return False
            ref[P[1][0]] = Q[1][1]
            if Q[1][0] is not None:
                P[1][0] = Q[1][0]
            if empty(P[0]):
                P[0] = Q[0][:]
            else:
                ref[P[0][0]] = Q[0][1]
            P[0][0] = Q[0][0]

        if not (empty(P[0]) and empty(P[1])):
            S.append(P)
        return True

    def _trim(self, e):
        #Drop back edges returning to vertex u = e[0] (no longer needed)
        S, ref, lowpt = self.S, self.ref, self.lowpt
        u = e[0]

        def lowest(P):
            if empty(P[0]):
                return lowpt[P[1][0]]
            if empty(P[1]):
                return lowpt[P[0][0]]
            return min(lowpt[P[0][0]], lowpt[P[1][0]])

        while S and lowest(S[-1]) == self.height[u]:   # prune full pairs that stop at u
            S.pop()

        if S:   # trim the top pair if needed
            P = S.pop()
            for a, b in ((0, 1), (1, 0)):
                side, other = P[a], P[b]
                while side[1] is not None and side[1][1] == u:
                    side[1] = ref.get(side[1])
                if side[1] is None and side[0] is not None:
                    ref[side[0]] = other[0]
                    side[0] = None
            S.append(P)

        if lowpt[e] < self.height[u] and S:     # keep track of side for edge e
            hl, hr = S[-1][0][1], S[-1][1][1]
            ref[e] = hl if hl is not None and (hr is None or lowpt[hl] > lowpt[hr]) else hr

    # ----------------------------------------------------------------
    def is_planar(self):
        n = self.V
        self.height = [None] * n
        self.parent_edge = [None] * n
        self.out = [[] for _ in range(n)]
        self.seen = set()
        self.lowpt, self.lowpt2, self.nesting = {}, {}, {}
        self.lowpt_edge, self.ref, self.bottom = {}, {}, {}
        self.S = []

        roots = []  # pick one root per connected component
        for r in range(n):
            if self.height[r] is None:
                self.height[r] = 0
                roots.append(r)
                self._orient(r)

        # Sort adjacencies based on nesting depth before testing
        for v in range(n):
            self.out[v].sort(key=lambda w: self.nesting[(v, w)])

        # Graph is planar only if every component passes
        return all(self._test(r) for r in roots)


def read_graphs_from_file(filename="graph.txt"):
    graphs = []
    current_graph = None

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                i += 1
                continue

            parts = line.split()
            if len(parts) == 2:
                V, E = int(parts[0]), int(parts[1])
                current_graph = PlanarityChecker(V)
                i += 1

                edges_read = 0
                while edges_read < E and i < len(lines):
                    edge_line = lines[i].strip()
                    if not edge_line or edge_line.startswith('#'):
                        i += 1
                        continue

                    u, v = map(int, edge_line.split())
                    current_graph.add_edge(u, v)
                    edges_read += 1
                    i += 1

                graphs.append(current_graph)
            else:
                i += 1
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []

    return graphs


def run_planarity(filename="Graph"):
    #Main function that will be called by main.py
    print("--- Planarity Test (Left-Right Algorithm) ---")
    graphs = read_graphs_from_file(filename)

    if not graphs:
        print("No graphs were loaded.")
        return

    for idx, graph in enumerate(graphs, start=1):
        result = graph.is_planar()
        status = "PLANAR" if result else "NON-PLANAR"
        print(f"Graph {idx} (V={graph.V}) : {status}")

    print("------------------------------------------------\n")
