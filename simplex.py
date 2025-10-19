import sys

class Simplex:
    def __init__(self, tokens):
        self.val = float(tokens.pop(0))
        self.dim = int(tokens.pop(0))
        self.vert = set(int(tokens.pop(0)) for _ in range(self.dim + 1))

    def __str__(self):
        return f"{{val={self.val}; dim={self.dim}; {sorted(self.vert)}}}"

