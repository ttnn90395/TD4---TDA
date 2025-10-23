import sys
import matplotlib.pyplot as plt


# Return a sorted by time filtration from a file
def read_filtration(filename):
    filtration = []
    with open(filename, "r") as f:
        filtration = []
        for line in f:
            token = line.strip().split()
            filtration.append(
                {
                    "time": float(token[0]),
                    "dim": int(token[1]),
                    "vert": set(map(int, token[2:])),
                }
            )

        # On lit les simplexes jusqu’à ce qu’il n’y ait plus de tokens
        if not all(
            filtration[i]["time"] <= filtration[i + 1]["time"]
            for i in range(len(filtration) - 1)
        ):  # Check if filtration is already sorted
            filtration.sort(key=lambda s: s["time"])
    return filtration


def plot_barcodes(barcodes):
    """
    barcodes : list of tuples (dim, birth, death)
    Exemple :
        barcodes = [
            (0, -18.5, 0),
            (1, -17.2, -10.1),
            (2, -14.5, -8.3)
        ]
    """
    # Trier par dimension pour affichage ordonné
    barcodes.sort(key=lambda x: (x[0], x[1]))

    # Trouver les dimensions présentes
    dims = sorted(set(b[0] for b in barcodes))

    fig, ax = plt.subplots(figsize=(10, 5))

    # Pour chaque dimension H_i, tracer les barres correspondantes
    y_offset = 0
    for dim in dims:
        subset = [(b, d) for (d_i, b, d) in barcodes if d_i == dim]
        for i, (birth, death) in enumerate(subset):
            # Si la mort est infinie (persiste), on met une flèche
            if death == float("inf"):
                ax.arrow(
                    birth,
                    y_offset,
                    10,
                    0,
                    length_includes_head=True,
                    head_width=0.15,
                    head_length=0.4,
                    color="navy",
                    lw=3,
                )
            else:
                ax.hlines(y_offset, birth, death, color="navy", lw=3)
            y_offset += 0.2  # Décalage vertical entre barres
        y_offset += 0.5  # Espace entre dimensions
        ax.text(
            min(b for b, _ in subset) - 1,
            y_offset - 0.5,
            f"H{dim}",
            va="center",
            ha="right",
        )

    ax.set_xlabel("Filtration value")
    ax.set_ylabel("Homology group H_k")
    ax.set_title("Barcode diagram")
    ax.grid(False)
    plt.tight_layout()
    plt.show()
