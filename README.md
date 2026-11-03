# Informatics ITS Graph Theory class Group 9

## 1. Identity
* **Course:** Informatics ITS Graph Theory class Group 9
* **Group Members:**
  * Emmanuel SANTINI - 5999261124
  * [Student Name 2 - NRP 2]
  * [Student Name 3 - NRP 3]

---

## 2. Short explanation about algorithm

### 1. Left-Right Planarity Test

We implemented the **Left-Right (LR) Planarity Test** (de Fraysseix and Rosenstiehl, simplified by Brandes).

Instead of searching for Kuratowski subgraphs or performing reductions, this algorithm checks whether the back-edges of a DFS tree can be partitioned into two distinct sides, **Left** and **Right**, without crossing:
1. **DFS Orientation:** A Depth-First Search traversal builds a DFS tree and classifies edges into tree edges and back-edges (returning to ancestors).
2. **Nesting Depth:** Each edge receives a nesting order based on the reachability of its return points (`lowpt`).
3. **Side Constraints:** The algorithm traverses the graph bottom-up and pushes edge constraints onto a stack. A graph is planar if every back-edge can be assigned to either the Left or Right side without contradiction. If an edge conflicts with both sides, the graph is non-planar.

### 2. DMP Algorithm (Demoucron, Malgrange & Pertuiset)

**$$$$$$$**

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
