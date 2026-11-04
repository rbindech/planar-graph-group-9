import sys

# The DFS below is recursive, so on big graphs it can go very deep.
# Python's default limit (1000) is too small, so we raise it.
sys.setrecursionlimit(10000)


def empty(interval):
    """Check if an interval is empty.

    An interval is stored as [low_edge, high_edge].
    It is considered empty when both of its ends are None.
    """
    return interval[0] is None and interval[1] is None


class PlanarityChecker:
    def __init__(self, num_vertices):
        """Create an empty graph with num_vertices vertices (numbered 0 to num_vertices - 1) and no edges."""
        self.num_vertices = num_vertices
        # adjacency[v] is the list of all neighbors of vertex v
        self.adjacency = [[] for _ in range(num_vertices)]

    def add_edge(self, vertex_a, vertex_b):
        """Add an undirected edge between vertex_a and vertex_b (stored in both adjacency lists)."""
        if vertex_a != vertex_b:            # skip self-loops, they never affect planarity
            self.adjacency[vertex_a].append(vertex_b)
            self.adjacency[vertex_b].append(vertex_a)

    #  Phase 1: DFS orientation + compute lowpoint / second_lowpoint / nesting depth
    #  (every edge gets oriented in the direction the DFS crosses it, and we
    #   record how high up the DFS tree each edge can "return" to)

    def _orient(self, vertex):
        """Run the first DFS from vertex (recursively).

        It orients every edge, marks it as a tree edge or a back edge, and computes
        the lowpoint, second lowpoint and nesting depth of each edge.
        """
        parent_edge = self.parent_edge[vertex]      # edge used to reach this vertex (None for a root)
        for neighbor in self.adjacency[vertex]:
            edge = (vertex, neighbor)
            # each undirected edge must only be oriented once, so skip it if
            # we already handled it from either side
            if edge in self.oriented_edges or (neighbor, vertex) in self.oriented_edges:
                continue
            self.oriented_edges.add(edge)
            self.out_neighbors[vertex].append(neighbor)
            # by default an edge "returns" no higher than the height of its starting vertex
            self.lowpoint[edge] = self.second_lowpoint[edge] = self.height[vertex]

            if self.height[neighbor] is None:      # tree edge: neighbor is not visited yet, so go deeper
                self.parent_edge[neighbor] = edge
                self.height[neighbor] = self.height[vertex] + 1
                self._orient(neighbor)
            else:                 # back edge: neighbor is an ancestor that was already visited
                self.lowpoint[edge] = self.height[neighbor]

            # Brandes' nesting formula (chordal edges get +1)
            # this value is used later to sort the edges of each vertex
            self.nesting_depth[edge] = 2 * self.lowpoint[edge] + (self.second_lowpoint[edge] < self.height[vertex])

            # propagate the lowpoints of this edge up to the parent edge
            if parent_edge is not None:
                if self.lowpoint[edge] < self.lowpoint[parent_edge]:
                    # new lowest value found, the old lowest becomes a candidate for the second lowest
                    self.second_lowpoint[parent_edge] = min(self.lowpoint[parent_edge], self.second_lowpoint[edge])
                    self.lowpoint[parent_edge] = self.lowpoint[edge]
                elif self.lowpoint[edge] > self.lowpoint[parent_edge]:
                    self.second_lowpoint[parent_edge] = min(self.second_lowpoint[parent_edge], self.lowpoint[edge])
                else:
                    self.second_lowpoint[parent_edge] = min(self.second_lowpoint[parent_edge], self.second_lowpoint[edge])


    #  Phase 3: test Left / Right side constraints
    #  (we go through the graph again and try to put every back edge on the
    #   left or on the right side without creating a conflict)

    def _conflicting(self, interval, edge):
        """Return True if the given interval of back edges conflicts with edge (they cannot be on the same side)."""
        # an interval conflicts with an edge if its highest back edge
        # returns strictly higher than the lowpoint of that edge
        return not empty(interval) and self.lowpoint[interval[1]] > self.lowpoint[edge]

    def _test(self, vertex):
        """Run the second DFS from vertex (recursively) and try to assign every back edge to the left or right side.

        Returns False as soon as a conflict is found (the graph is not planar), True otherwise.
        """
        parent_edge = self.parent_edge[vertex]
        for index, neighbor in enumerate(self.out_neighbors[vertex]):
            current_edge = (vertex, neighbor)
            # remember the stack size before processing this edge,
            # so we know later which pairs belong to it
            self.stack_bottom[current_edge] = len(self.conflict_stack)

            if current_edge == self.parent_edge[neighbor]:    # tree edge: recurse
                if not self._test(neighbor):
                    return False
            else:         # back edge: push it on the stack as its own conflict pair
                self.lowpoint_edge[current_edge] = current_edge
                self.conflict_stack.append([[None, None], [current_edge, current_edge]])

            if self.lowpoint[current_edge] < self.height[vertex]:   # current_edge has back edges returning above vertex
                if index == 0:
                    # first edge: the parent edge simply inherits its lowpoint edge
                    self.lowpoint_edge[parent_edge] = self.lowpoint_edge[current_edge]
                elif not self._merge(current_edge, parent_edge):
                    return False

        if parent_edge is not None:
            self._trim(parent_edge)
        return True

    def _merge(self, current_edge, parent_edge):
        """Add side constraints for current_edge, by merging the conflict pairs on top of the stack.

        The pairs created by current_edge are merged together, then the pairs that conflict
        with it are merged on the other side. Returns False if a conflict is found.
        """
        stack, reference, lowpoint = self.conflict_stack, self.reference_edge, self.lowpoint
        merged_pair = [[None, None], [None, None]]      # [left, right]

        # Merge back edges of current_edge into the right side of merged_pair
        while True:
            popped_pair = stack.pop()
            if not empty(popped_pair[0]):
                popped_pair.reverse()       # try to swap sides so the left one becomes empty
            if not empty(popped_pair[0]):     # still something on both sides -> impossible
                return False
            if lowpoint[popped_pair[1][0]] > lowpoint[parent_edge]:
                if empty(merged_pair[1]):
                    merged_pair[1] = popped_pair[1][:]
                else:
                    reference[merged_pair[1][0]] = popped_pair[1][1]
                merged_pair[1][0] = popped_pair[1][0]
            else:
                # this edge can be aligned with the lowpoint edge of the parent
                reference[popped_pair[1][0]] = self.lowpoint_edge[parent_edge]
            if len(stack) == self.stack_bottom[current_edge]:
                break

        # Merge edges conflicting with current_edge into the left side of merged_pair
        while stack and (self._conflicting(stack[-1][0], current_edge) or self._conflicting(stack[-1][1], current_edge)):
            popped_pair = stack.pop()
            if self._conflicting(popped_pair[1], current_edge):
                popped_pair.reverse()
            if self._conflicting(popped_pair[1], current_edge):    # conflict on both sides -> impossible
                return False
            reference[merged_pair[1][0]] = popped_pair[1][1]
            if popped_pair[1][0] is not None:
                merged_pair[1][0] = popped_pair[1][0]
            if empty(merged_pair[0]):
                merged_pair[0] = popped_pair[0][:]
            else:
                reference[merged_pair[0][0]] = popped_pair[0][1]
            merged_pair[0][0] = popped_pair[0][0]

        if not (empty(merged_pair[0]) and empty(merged_pair[1])):
            stack.append(merged_pair)
        return True

    def _trim(self, parent_edge):
        """Clean the conflict stack once we are done with the vertex at the start of parent_edge.

        Drop the back edges that return to vertex parent_vertex = parent_edge[0]
        (we are done with this vertex, so they cannot cause conflicts anymore).
        """
        stack, reference, lowpoint = self.conflict_stack, self.reference_edge, self.lowpoint
        parent_vertex = parent_edge[0]

        def lowest(pair):
            """Return the lowest return height among the two sides of a conflict pair."""
            if empty(pair[0]):
                return lowpoint[pair[1][0]]
            if empty(pair[1]):
                return lowpoint[pair[0][0]]
            return min(lowpoint[pair[0][0]], lowpoint[pair[1][0]])

        while stack and lowest(stack[-1]) == self.height[parent_vertex]:   # remove whole pairs that stop at parent_vertex
            stack.pop()

        if stack:   # the pair on top may still contain some edges ending at parent_vertex, so trim it
            top_pair = stack.pop()
            for side_index, other_index in ((0, 1), (1, 0)):
                side, other_side = top_pair[side_index], top_pair[other_index]
                while side[1] is not None and side[1][1] == parent_vertex:
                    side[1] = reference.get(side[1])
                if side[1] is None and side[0] is not None:
                    reference[side[0]] = other_side[0]
                    side[0] = None
            stack.append(top_pair)

        if lowpoint[parent_edge] < self.height[parent_vertex] and stack:     # remember which side parent_edge is on
            left_high, right_high = stack[-1][0][1], stack[-1][1][1]
            reference[parent_edge] = left_high if left_high is not None and (right_high is None or lowpoint[left_high] > lowpoint[right_high]) else right_high

    # ----------------------------------------------------------------
    def is_planar(self):
        """Main method: return True if the graph is planar, False otherwise.

        It resets all the data structures, then runs the three phases
        (orientation, sorting, left/right test) on every connected component.
        """
        num_vertices = self.num_vertices
        self.height = [None] * num_vertices          # DFS depth of each vertex (None = not visited yet)
        self.parent_edge = [None] * num_vertices     # tree edge used to reach each vertex
        self.out_neighbors = [[] for _ in range(num_vertices)]   # oriented (outgoing) edges of each vertex
        self.oriented_edges = set()                  # edges that were already oriented
        self.lowpoint, self.second_lowpoint, self.nesting_depth = {}, {}, {}
        self.lowpoint_edge, self.reference_edge, self.stack_bottom = {}, {}, {}
        self.conflict_stack = []                     # stack of left/right conflict pairs

        roots = []  # pick one root per connected component
        for root in range(num_vertices):
            if self.height[root] is None:
                self.height[root] = 0
                roots.append(root)
                self._orient(root)

        # Phase 2: sort the outgoing edges of each vertex by nesting depth before testing
        for vertex in range(num_vertices):
            self.out_neighbors[vertex].sort(key=lambda neighbor: self.nesting_depth[(vertex, neighbor)])

        # Graph is planar only if every component passes
        return all(self._test(root) for root in roots)


def read_graphs_from_file(filename="graph.txt"):
    """Read all the graphs of a text file and return them as a list of PlanarityChecker objects.

    File format: a line "V E" (number of vertices and edges), followed by E lines "u v".
    Empty lines and lines starting with '#' are ignored, and several graphs can follow each other.
    Returns an empty list if the file does not exist.
    """
    graphs = []
    current_graph = None

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        line_index = 0
        while line_index < len(lines):
            line = lines[line_index].strip()
            if not line or line.startswith('#'):
                line_index += 1
                continue

            parts = line.split()
            if len(parts) == 2:     # header line of a new graph
                num_vertices, num_edges = int(parts[0]), int(parts[1])
                current_graph = PlanarityChecker(num_vertices)
                line_index += 1

                edges_read = 0
                while edges_read < num_edges and line_index < len(lines):
                    edge_line = lines[line_index].strip()
                    if not edge_line or edge_line.startswith('#'):
                        line_index += 1
                        continue

                    vertex_a, vertex_b = map(int, edge_line.split())
                    current_graph.add_edge(vertex_a, vertex_b)
                    edges_read += 1
                    line_index += 1

                graphs.append(current_graph)
            else:
                line_index += 1
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []

    return graphs


def run_planarity(filename="Graph"):
    """Load every graph from the file, test each one and print PLANAR or NON-PLANAR.

    This is the entry point that will be called by main.py.
    """
    print("--- Planarity Test (Left-Right Algorithm) ---")
    graphs = read_graphs_from_file(filename)

    if not graphs:
        print("No graphs were loaded.")
        return

    for graph_number, graph in enumerate(graphs, start=1):
        result = graph.is_planar()
        status = "PLANAR" if result else "NON-PLANAR"
        print(f"Graph {graph_number} (V={graph.num_vertices}) : {status}")

    print("------------------------------------------------\n")
