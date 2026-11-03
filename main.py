import sys
from Left_Right import run_planarity
from DMP import run_dmp


def main():
    # graph file: "Graph" by default, or given on the command line
    filename = sys.argv[1] if len(sys.argv) > 1 else "Graph"

    print("=== Algorithm Execution ===")
    print(f"Input file: {filename}\n")
    run_planarity(filename)
    run_dmp(filename)


if __name__ == "__main__":
    main()