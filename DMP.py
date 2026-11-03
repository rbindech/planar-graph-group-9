"""
Planarity test - Demoucron, Malgrange & Pertuiset algorithm (1964).

Idea: start from a cycle (drawn as 2 faces: inside / outside), then repeatedly
take a piece of the graph not drawn yet ("fragment") and draw one path of it
inside a face that can receive it. If some fragment fits in no face, the graph
is not planar. If every fragment gets drawn, the graph is planar.

DMP requires a 2-connected graph, so the graph is first split into its
biconnected components: a graph is planar iff each of them is planar.
"""

import sys
from collections import deque

sys.setrecursionlimit(10000)


class DMPPlanarityChecker:
    def __init__(self, num_vertices):
        self.V = num_vertices
        self.adj = [set() for _ in range(num_vertices)]
        self.faces = []  # faces found for each component (filled if planar)

    def add_edge(self, u, v):
        if u == v:
            return  # a loop never changes planarity
        self.adj[u].add(v)
        self.adj[v].add(u)

    def num_edges(self):
        return sum(len(n) for n in self.adj) // 2

    # ------------------------------------------------------------------
    # 1) Biconnected components (Tarjan, with a stack of edges)
    # ------------------------------------------------------------------
    def biconnected_components(self):
        disc = [-1] * self.V
        low = [0] * self.V
        timer = [0]
        edge_stack = []
        components = []

        def dfs(u, parent):
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            for v in self.adj[u]:
                if v == parent:
                    continue
                if disc[v] == -1:
                    edge_stack.append((u, v))
                    dfs(v, u)
                    low[u] = min(low[u], low[v])
                    if low[v] >= disc[u]:
                        # u separates the subtree of v: pop one component
                        comp = []
                        while True:
                            e = edge_stack.pop()
                            comp.append(e)
                            if e == (u, v):
                                break
                        components.append(comp)
                elif disc[v] < disc[u]:
                    edge_stack.append((u, v))
                    low[u] = min(low[u], disc[v])

        for s in range(self.V):
            if disc[s] == -1:
                dfs(s, -1)
        return components

    # ------------------------------------------------------------------
    # 2) Find any cycle with a DFS (first back edge found)
    # ------------------------------------------------------------------
    @staticmethod
    def find_cycle(adj, start):
        parent = {start: None}
        on_path = set()

        def dfs(u):
            on_path.add(u)
            for v in adj[u]:
                if v == parent[u]:
                    continue
                if v in on_path:
                    # back edge u -> v : climb up the parents from u to v
                    cycle = [u]
                    while cycle[-1] != v:
                        cycle.append(parent[cycle[-1]])
                    return cycle
                if v not in parent:
                    parent[v] = u
                    res = dfs(v)
                    if res:
                        return res
            on_path.discard(u)
            return None

        return dfs(start)

    # ------------------------------------------------------------------
    # 3) Fragments of the graph relative to what is already drawn
    # ------------------------------------------------------------------
    @staticmethod
    def find_fragments(adj, drawn_vertices, drawn_edges):
        """
        A fragment is either:
          - a single edge not drawn yet whose 2 ends are already drawn (chord)
          - a connected group of vertices not drawn yet, with every edge that
            touches it.
        Returns a list of (contacts, vertices) where contacts = drawn vertices
        the fragment touches, vertices = its non-drawn vertices (empty for a chord).
        """
        fragments = []

        # chords
        for u in drawn_vertices:
            for v in adj[u]:
                if u < v and v in drawn_vertices and frozenset((u, v)) not in drawn_edges:
                    fragments.append(({u, v}, set()))

        # groups of non-drawn vertices (BFS that never enters drawn vertices)
        seen = set()
        for s in adj:
            if s in drawn_vertices or s in seen:
                continue
            group, contacts = {s}, set()
            seen.add(s)
            queue = deque([s])
            while queue:
                x = queue.popleft()
                for y in adj[x]:
                    if y in drawn_vertices:
                        contacts.add(y)
                    elif y not in seen:
                        seen.add(y)
                        group.add(y)
                        queue.append(y)
            fragments.append((contacts, group))

        return fragments

    # ------------------------------------------------------------------
    # 4) A path inside a fragment between two of its contact vertices
    # ------------------------------------------------------------------
    @staticmethod
    def path_in_fragment(adj, contacts, group):
        contacts = list(contacts)
        if not group:  # chord: the path is the edge itself
            return contacts[0], contacts[1], []

        a = contacts[0]
        # BFS from a, walking only through the fragment's own vertices
        prev = {}
        queue = deque()
        for x in adj[a]:
            if x in group and x not in prev:
                prev[x] = a
                queue.append(x)
        while queue:
            x = queue.popleft()
            for y in adj[x]:
                if y in group and y not in prev:
                    prev[y] = x
                    queue.append(y)
                elif y != a and y in contacts:
                    # reached a second contact b: rebuild a -> ... -> x -> b
                    inner = [x]
                    while prev[inner[-1]] != a:
                        inner.append(prev[inner[-1]])
                    inner.reverse()
                    return a, y, inner
        raise RuntimeError("fragment with a single contact: graph not 2-connected")

    # ------------------------------------------------------------------
    # 5) Draw path a -> inner -> b inside a face: the face is split in 2
    # ------------------------------------------------------------------
    @staticmethod
    def split_face(face, a, b, inner):
        i, j = face.index(a), face.index(b)
        n = len(face)
        arc_ab = [face[(i + k) % n] for k in range((j - i) % n + 1)]  # a ... b
        arc_ba = [face[(j + k) % n] for k in range((i - j) % n + 1)]  # b ... a
        face1 = arc_ab + inner[::-1]  # a ... b then back to a through the path
        face2 = arc_ba + inner        # b ... a then back to b through the path
        return face1, face2

    # ------------------------------------------------------------------
    # DMP on one biconnected component
    # ------------------------------------------------------------------
    def dmp_component(self, edges):
        adj = {}
        for u, v in edges:
            adj.setdefault(u, set()).add(v)
            adj.setdefault(v, set()).add(u)
        n, m = len(adj), len(edges)

        if m < 3:            # a single edge: always planar
            return True, []
        if m > 3 * n - 6:    # necessary condition from Euler's formula
            return False, []

        cycle = self.find_cycle(adj, next(iter(adj)))
        drawn_vertices = set(cycle)
        drawn_edges = {frozenset((cycle[k], cycle[(k + 1) % len(cycle)]))
                       for k in range(len(cycle))}
        faces = [list(cycle), list(cycle)]  # inside and outside of the cycle

        while True:
            fragments = self.find_fragments(adj, drawn_vertices, drawn_edges)
            if not fragments:
                return True, faces  # everything is drawn

            # admissible faces = faces whose border contains all the contacts
            admissible = []
            for contacts, group in fragments:
                ok = [f for f in range(len(faces)) if contacts <= set(faces[f])]
                if not ok:
                    return False, []  # this fragment fits nowhere
                admissible.append(ok)

            # priority to a fragment that has only one possible face
            k = next((k for k, ok in enumerate(admissible) if len(ok) == 1), 0)
            contacts, group = fragments[k]
            f = admissible[k][0]

            a, b, inner = self.path_in_fragment(adj, contacts, group)
            face1, face2 = self.split_face(faces[f], a, b, inner)
            faces[f] = face1
            faces.append(face2)

            path = [a] + inner + [b]
            drawn_vertices.update(path)
            for x, y in zip(path, path[1:]):
                drawn_edges.add(frozenset((x, y)))

    # ------------------------------------------------------------------
    def is_planar(self):
        n, m = self.V, self.num_edges()
        if n >= 3 and m > 3 * n - 6:
            return False
        self.faces = []
        for comp in self.biconnected_components():
            planar, faces = self.dmp_component(comp)
            if not planar:
                self.faces = []
                return False
            self.faces.append(faces)
        return True


def read_graphs_from_file(filename="Graph"):
    """Same format as Left_Right.py: 'V E' then E lines 'u v'. '#' = comment."""
    graphs = []
    try:
        with open(filename, "r") as f:
            lines = [l.strip() for l in f]
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []

    lines = [l for l in lines if l and not l.startswith("#")]
    i = 0
    while i < len(lines):
        V, E = map(int, lines[i].split())
        g = DMPPlanarityChecker(V)
        for k in range(E):
            u, v = map(int, lines[i + 1 + k].split())
            g.add_edge(u, v)
        graphs.append(g)
        i += 1 + E
    return graphs


def run_dmp(filename="Graph"):
    """Main function that will be called by main.py"""
    print("--- Planarity Test (DMP Algorithm) ---")
    graphs = read_graphs_from_file(filename)
    if not graphs:
        print("No graphs were loaded.")
        return

    for idx, graph in enumerate(graphs, start=1):
        result = graph.is_planar()
        status = "PLANAR" if result else "NON-PLANAR"
        print(f"Graph {idx} (V={graph.V}, E={graph.num_edges()}) : {status}")
        if result:
            for c, faces in enumerate(graph.faces, start=1):
                if faces:
                    print(f"   component {c}: {len(faces)} faces -> {faces}")
    print("------------------------------------------------\n")
