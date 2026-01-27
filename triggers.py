from itertools import combinations
from notify import notify

THRESHOLD_PERCENT = 3.0


def check_thresholds(deltas: dict):
    """
    deltas = {
        "pool1": +0.85,
        "pool2": -4.3,
        "pool3": +2.1
    }
    """

    for (p1, d1), (p2, d2) in combinations(deltas.items(), 2):
        diff = abs(d1 - d2)

        if diff >= THRESHOLD_PERCENT:
            notify(
                f"Delta threshold superato:\n"
                f"{p1}: {d1:+.2f}%\n"
                f"{p2}: {d2:+.2f}%\n"
                f"Diff: {diff:.2f}%"
            )
