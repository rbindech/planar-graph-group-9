import sys

sys.setrecursionlimit(10000)

class PlanarityChecker:
    def __init__(self, num_vertices):
        self.V = num_vertices
        self.adj = [[] for _ in range(num_vertices)]
        self.depth = [-1] * num_vertices
        self.parent = [-1] * num_vertices
        self.back_edges = []

    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)

    def dfs(self, u, p, d):
        self.depth[u] = d
        self.parent[u] = p
        for v in self.adj[u]:
            if v == p:
                continue
            if self.depth[v] == -1:
                self.dfs(v, u, d + 1)
            elif self.depth[v] < self.depth[u]:
                self.back_edges.append((u, v))

    def is_planar(self):
        if self.V > 0 and self.depth[0] == -1:
            self.dfs(0, -1, 0)

        vertices_by_depth = sorted(range(self.V), key=lambda x: self.depth[x], reverse=True)
        stack = []
        constraints = {}

        for v in vertices_by_depth:
            edges_from_v = [e for e in self.back_edges if e[0] == v]
            edges_from_v.sort(key=lambda e: self.depth[e[1]])

            for edge in edges_from_v:
                for active_edge in stack:
                    d1, a1 = edge
                    d2, a2 = active_edge
                    
                    dep_d1, dep_a1 = self.depth[d1], self.depth[a1]
                    dep_d2, dep_a2 = self.depth[d2], self.depth[a2]
                    
                    is_nested = False
                    if dep_a1 < dep_a2 < dep_d1 < dep_d2:
                        is_nested = True
                    elif dep_a2 < dep_a1 < dep_d2 < dep_d1:
                        is_nested = True
                    
                    if is_nested:
                        if edge in constraints and active_edge in constraints:
                            if constraints[edge] == constraints[active_edge]:
                                return False
                        elif edge in constraints:
                            constraints[active_edge] = 1 - constraints[edge]
                        elif active_edge in constraints:
                            constraints[edge] = 1 - constraints[active_edge]
                        else:
                            constraints[edge] = 0
                            constraints[active_edge] = 1
                
                stack.append(edge)

            while stack:
                top_edge = stack[-1]
                if self.depth[top_edge[1]] >= self.depth[v]:
                    stack.pop()
                else:
                    break

        return True

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
    """Main function that will be called by main.py"""
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