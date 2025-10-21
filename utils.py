from simplex import Simplex 
import sys

# Return a sorted by time filtration from a file 
def read_filtration(filename):
    filtration = []
    with open(filename, "r") as f:
        filtration = []
        for line in f:
            token = line.strip().split()
            filtration.append({"time": float(token[0]), "dim": int(token[1]), "vert": set(map(int, token[2:]))})

        # On lit les simplexes jusqu’à ce qu’il n’y ait plus de tokens
        if not all(filtration[i]["time"] <= filtration[i+1]["time"] for i in range(len(filtration)-1)): # Check if filtration is already sorted
            filtration.sort(key=lambda s: s["time"])
    return filtration

filtration = read_filtration("filtration.txt")
for simplex in filtration:
    print(simplex)

