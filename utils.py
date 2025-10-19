from simplex import Simplex 

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



## Question 1 - Boundary matrix
def boundary_matrix(filtration : list[Simplex]) -> list[list[int]]:

    # Sort the filtration by time insertion
    filtration = sorted(filtration, key=lambda s: s.val)

    n = len(filtration)
    
    boundary = []

    for j, simplex in enumerate(filtration):
        boundary.append([])
        for i, face in enumerate(filtration):
            if i != j and face.dim == simplex.dim - 1 and face.vert.issubset(simplex.vert):
                boundary[j].append(i)

    return boundary


## Question 2,3 - Reduction algorithm
def reduce_boundary_matrix(boundary : list[list[int]]) -> list[list[int]]:
    
    reduced_boundary = boundary.copy()
    m = len(reduced_boundary)

    low = [max(col) if col else -1 for col in reduced_boundary]

    for j in range(m):
        while low[j] != -1 and low[j] in low[:j]:

            i = low.index(low[j])

            # Perform column addition (mod 2) : XOR
            reduced_boundary[j] = list(set(reduced_boundary[j]) ^ set(reduced_boundary[i]))
            low[j] = max(reduced_boundary[j]) if reduced_boundary[j] else -1

    return reduced_boundary # à optimiser


## Question 4 - Barcode extraction
def extract_barcodes(reduced_boundary : list[list[int]], filtration : list[Simplex]) -> list[tuple[int, int, int]]:

    seen_indexes = set()
    barcodes = []

    for j in range(len(reduced_boundary)):
        seen_indexes.add(j)
        if reduced_boundary[j]:
            low_j = max(reduced_boundary[j])
            seen_indexes.add(low_j)
            barcode = (filtration[j].dim, j, low_j)  # (index, death index, dimension)
            barcodes.append(barcode)

    unseen_indexes = set(range(len(filtration))) - seen_indexes
    for i in unseen_indexes:
        barcode = (filtration[i].dim, i, -1)  # (index, death index = ∞, dimension)
        barcodes.append(barcode)
    return barcodes


def print_barcodes(barcodes : list[tuple[int, int, int]], filtration : list[Simplex]) -> None:
    for (dim, birth_idx, death_idx) in barcodes:
        birth_time = filtration[birth_idx].val
        death_time = filtration[death_idx].val if death_idx != -1 else float('inf')
        print(f"{dim} {birth_time} {death_time}")


## TODO : report, answer questions, complexity analysis, plots, analysis of graphs, 2 3 pages. 
# >>> jupyter notebook

def main():
    F = read_filtration("filtration.txt")
    B = boundary_matrix(F)
    print(B)
    R = reduce_boundary_matrix(B)
    print(R)
    barcodes = extract_barcodes(R, F)
    print(barcodez )
    print_barcodes(barcodes, F)

if __name__ == "__main__":
    main()