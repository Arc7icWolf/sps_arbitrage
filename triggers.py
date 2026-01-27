from thresholds import THRESHOLDS

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

        diff = abs(deltas[p1] - deltas[p2])

        if diff >= threshold:
            alerts.append({
                "token": token,
                "pool_a": p1,
                "pool_b": p2,
                "delta_a": deltas[p1],
                "delta_b": deltas[p2],
                "diff": diff,
                "threshold": threshold,
            })

    return alerts
