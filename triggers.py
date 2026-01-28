from thresholds import THRESHOLDS
from notify import notify


def check_thresholds(token, deltas):
    """
    deltas = {
        "bsc_sps_wbnb": +0.85,
        "base_sps_usdc": -4.3,
        "uniswap_v4_eth": +2.1,
    }
    """

    if token not in THRESHOLDS:
        return []

    alerts = []

    for (p1, p2), threshold in THRESHOLDS[token].items():
        if p1 not in deltas or p2 not in deltas:
            continue

        d1 = deltas[p1]
        d2 = deltas[p2]
        diff = abs(d1 - d2)

        if diff >= threshold:
            alert = {
                "token": token,
                "pool_a": p1,
                "pool_b": p2,
                "delta_a": d1,
                "delta_b": d2,
                "diff": diff,
                "threshold": threshold,
            }

            alerts.append(alert)

            notify(
                f"[{token}] Delta threshold superato ({threshold:.2f}%)\n"
                f"{p1}: {d1:+.2f}%\n"
                f"{p2}: {d2:+.2f}%\n"
                f"Diff: {diff:.2f}%"
            )     

    return alerts
