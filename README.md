# Informatics ITS Graph Theory class Group 9

## 1. Identity
* **Course:** Informatics ITS Graph Theory class Group 9
* **Group Members:**
  * Emmanuel SANTINI - 5999261124
  * Rida BINDECH - 5999261011
  * Calixte BERTHIER - 5999261123

---

## 2. Short explanation about algorithm

### 1. Left-Right Planarity Test

We implemented the **Left-Right (LR) Planarity Test** (de Fraysseix and Rosenstiehl, simplified by Brandes).

Instead of searching for Kuratowski subgraphs or performing reductions, this algorithm checks whether the back-edges of a DFS tree can be partitioned into two distinct sides, **Left** and **Right**, without crossing:
1. **DFS Orientation:** A Depth-First Search traversal builds a DFS tree and classifies edges into tree edges and back-edges (returning to ancestors).
2. **Nesting Depth:** Each edge receives a nesting order based on the reachability of its return points (`lowpt`).
3. **Side Constraints:** The algorithm traverses the graph bottom-up and pushes edge constraints onto a stack. A graph is planar if every back-edge can be assigned to either the Left or Right side without contradiction. If an edge conflicts with both sides, the graph is non-planar.

### 2. DMP Algorithm (Demoucron, Malgrange & Pertuiset)

We implemented the **DMP Planarity Test** (Demoucron, Malgrange and Pertuiset, 1964).

Instead of looking for a forbidden subgraph, this algorithm tries to **build a planar drawing step by step**, face by face. If at some point a part of the graph cannot be placed in any face, the graph is non-planar:
1. **Preprocessing:** If `E > 3V - 6` (with `V >= 3`), the graph is immediately non-planar (consequence of Euler's formula). Otherwise, the graph is split into its **biconnected components** (Tarjan's algorithm), because a graph is planar if and only if each of its biconnected components is planar. A component made of a single edge is always planar.
2. **Initial cycle:** A DFS finds any cycle of the component (the first back-edge found closes it). This cycle is drawn first and splits the plane into **2 faces**: inside and outside.
3. **Fragments:** The parts of the graph not drawn yet are grouped into fragments. A fragment is either a single edge whose two endpoints are already drawn (a *chord*), or a connected group of non-drawn vertices together with all the edges touching it. The drawn vertices a fragment touches are its **contact vertices**.
4. **Admissible faces:** A fragment can be placed in a face only if the border of this face contains **all** of its contact vertices. If a fragment has no admissible face, the graph is **non-planar** and the algorithm stops.
5. **Choice of the fragment:** A fragment with only one admissible face is placed first, since it has no other option. If every fragment has several admissible faces, any of them can be chosen: the DMP theorem guarantees that this choice never turns a planar graph into a failure.
6. **Embedding:** A path is drawn through the chosen fragment between two of its contact vertices (found with a BFS). This path is drawn inside the chosen face and **splits it into two new faces**.
7. **End:** Steps 3 to 6 are repeated until no fragment is left. The graph is then **planar**, and the program also displays the list of faces of each component. The number of faces always satisfies Euler's formula `F = E - V + 2`.

**Complexity:** The original algorithm runs in `O(V²)`. Our implementation is simpler and recomputes all fragments after each embedded path, which makes it slower in theory (around `O(V³)`) but still fast for the graph sizes used in this project.

---

## 3. Prerequisite to run the code
* **Python 3.8+**
* Standard libraries only (`sys`, `random`). No external package is required to run the main code.
* *(Optional)* `networkx` if you want to run the automated benchmark oracle in `test_planarity.py` (`pip install networkx`).

---

## 4. Instructions to run the code

*Note for macOS / Linux users: Use `python3` (on Windows, `python` or `py` usually works).*

### Run with the default sample file (`Graph`)
```bash
python main.py
```

To run on a specific input file:
```bash
python main.py Graph
# or
python main.py tests.txt
```

### 5. Run the test suite (optional)
To run automated validation against known graphs and random graphs:
```bash
python test_planarity.py tests.txt 2000
```

---

## 6. Input file format
Graphs are defined as follows:
* A header line with two integers: `V` (number of vertices) and `E` (number of edges).
* Followed by `E` lines, each containing an edge `u v` (0-indexed).
* Lines starting with `#` are treated as comments.

Example (`Graph`):
```text
6 9
0 1
1 2
2 0
3 4
4 5
5 3
0 3
1 4
2 5
```

---

---

## 7. Result of sample run

Executing `python main.py Graph` produces:

```text
=== Algorithm Execution ===
Input file: Graph

--- Planarity Test (Left-Right Algorithm) ---
Graph 1 (V=6) : PLANAR
------------------------------------------------

--- Planarity Test (DMP Algorithm) ---
Graph 1 (V=6, E=9) : PLANAR
   component 1: 5 faces -> [[0, 1, 2], [0, 2, 5, 3], [1, 4, 3, 0], [2, 1, 4, 5], [3, 4, 5]]
------------------------------------------------
```

---

## 8. AI tools usage disclosure

AI tools were used to help structure the README, reformat algorithm explanations for clarity, and assist in drafting test cases. All core logic, graph algorithms, and validation checks were carried out by the team.
