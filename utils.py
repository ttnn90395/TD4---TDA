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


def plot_barcodes(barcodes, name=None, log_scale=False, minimum_length=0.00):
    """
    Affiche un diagramme de codes-barres de persistance.
    barcodes : liste de tuples (dim, birth, death)
    Exemple :
        [(0, -18.5, float('inf')), (1, -16, -8), (2, -12, -5)]
    """
    # Trier les barcodes par dimension et temps de naissance
    barcodes = sorted(barcodes, key=lambda x: (x[0], x[1]))

    # Filtrer les barres trop courtes
    filtered = []
    for dim, birth, death in barcodes:
        length = float("inf") if death == float("inf") else (death - birth)
        if length >= minimum_length:
            filtered.append((dim, birth, death))

    barcodes = filtered

    if not barcodes:
        raise ValueError("Empty barcode list")

    # Dimensions distinctes
    dims = list(range(barcodes[-1][0] + 1))

    # Calcul des bornes horizontales
    finite_deaths = [d for (_, _, d) in barcodes if d != float("inf")]
    x_min = min(b for (_, b, _) in barcodes)
    if finite_deaths:
        x_max = max(finite_deaths)
    else:
        x_max = max(b for (_, b, _) in barcodes)

    # garantir une marge non nulle
    span = x_max - x_min
    if span == 0:
        margin = 1.0
    else:
        margin = span * 0.1
    x_min -= margin
    x_max += margin

    # Handle negative values for log scale
    if log_scale:
        if x_min <= 0:
            x_min = 1e-10
        if x_max <= 0:
            x_max = 1.0

    # Préparation du graphique
    fig, ax = plt.subplots(figsize=(12, 6))

    # Palette de couleurs variées
    cmap = plt.cm.get_cmap("tab10", len(dims))
    colors = [cmap(i) for i in range(cmap.N)]

    # Réserver un bloc de hauteur fixe pour chaque dimension
    block_height = 1.5
    total_height = len(dims) * block_height

    for i, dim in enumerate(dims):
        subset = [(b, d) for (d_i, b, d) in barcodes if d_i == dim]
        color = colors[i % len(colors)]

        # Coordonnées verticales pour ce bloc
        y_bottom = total_height - (i + 1) * block_height
        y_top = y_bottom + block_height
        n_bars = len(subset)

        if n_bars > 0:
            # Espacement régulier des barres dans le bloc
            y_positions = [
                y_bottom + (k + 1) * (block_height / (n_bars + 1))
                for k in range(n_bars)
            ]

            for (birth, death), y in zip(subset, y_positions):
                plot_birth = birth
                plot_end = x_max if death == float("inf") else death
                if log_scale and plot_birth <= 0:
                    plot_birth = 1e-10
                if log_scale and plot_end <= 0:
                    plot_end = 1e-10
                ax.hlines(y, plot_birth, plot_end, color=color, lw=3)

                if death == float("inf"):
                    ax.annotate(
                        "",
                        xy=(x_max - margin * 0.05, y),
                        xytext=(x_max - margin * 0.2, y),
                        arrowprops=dict(
                            arrowstyle="->",
                            color=color,
                            lw=2,
                            shrinkA=0,
                            shrinkB=0,
                            mutation_scale=10,
                        ),
                    )

        # Label H_k au milieu du bloc
        ax.text(
            x_min - margin * 0.5,
            (y_bottom + y_top) / 2,
            f"H{dim}",
            fontsize=13,
            va="center",
            ha="right",
            fontweight="bold",
            color=color,
        )

    # Mise en forme
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, total_height)
    ax.set_yticks([])  # pas de graduations verticales
    if log_scale:
        ax.set_xscale("log")
    ax.set_xlabel("Filtration value", fontsize=12)
    ax.set_title(
        "Barcode diagram" + (f" - {name}" if name else ""), fontsize=14, pad=15
    )
    ax.grid(False)

    plt.tight_layout()
    plt.show()
