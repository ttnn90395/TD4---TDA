from simplex import Simplex 
import sys

# Return a sorted by time filtration from a file 
def read_filtration(filename: str):
    filtration = []
    with open(filename, "r") as f:
        tokens = []
        for line in f:
            tokens.extend(line.strip().split())
        while tokens:
            filtration.append(Simplex(tokens))

        filtration.sort(key=lambda s: s.val)
    return filtration

