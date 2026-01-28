import asyncio
from pools import POOLS
from tokens import TOKENS
from balances import read_pool_async
from triggers import check_thresholds

# ==============================
# PARAMETRI
# ==============================

WARMUP_SNAPSHOTS = 3      # numero di snapshot per valutare stabilità
EPSILON_PERCENT = 0.25    # variazione % massima considerata rumore
SNAPSHOT_INTERVAL = 5    # secondi tra uno snapshot e l'altro

# ==============================
# SNAPSHOT
# ==============================

async def take_snapshot():
    tasks = []

    for pool in POOLS.values():
        tasks.append(
            read_pool_async(pool, TOKENS)
        )

    results = await asyncio.gather(*tasks)

    snapshot = {}
    for (name, _), balances in zip(POOLS.items(), results):
        snapshot[name] = balances

    return snapshot

# ==============================
# STABILITÀ
# ==============================

def snapshot_is_stable(snapshots):
    last = snapshots[-1]

    for prev in snapshots[:-1]:
        for pool in last:
            for token in last[pool]:
                base = prev[pool][token]
                curr = last[pool][token]

                if base == 0:
                    continue

                delta_pct = abs(curr - base) / base * 100
                if delta_pct > EPSILON_PERCENT:
                    return False

    return True

# ==============================
# MAIN
# ==============================

async def main(logger=print):
    snapshots = []
    baseline = None

    logger("Warm-up phase (ricerca baseline stabile)...")

    while baseline is None:
        snap = await take_snapshot()
        snapshots.append(snap)

        if len(snapshots) >= WARMUP_SNAPSHOTS:
            window = snapshots[-WARMUP_SNAPSHOTS:]
            if snapshot_is_stable(window):
                baseline = snap
                logger("Baseline fissata.")
            else:
                # manteniamo la finestra mobile
                snapshots.pop(0)

        await asyncio.sleep(SNAPSHOT_INTERVAL)

    logger("\nMonitoraggio variazioni (delta % rispetto alla baseline)\n")

    while True:
        current = await take_snapshot()
        deltas = {}

        for pool in current:
            logger(pool)
            for token in current[pool]:
                base = baseline[pool][token]
                curr = current[pool][token]

                if base == 0:
                    continue

                delta_pct = (curr - base) / base * 100

                deltas.setdefault(token, {})[pool] = delta_pct
                logger(f"  {token}: {delta_pct:+.2f}%")

        logger("-" * 40)

        for token, token_deltas in deltas.items():
            alerts = check_thresholds(token, token_deltas)

        await asyncio.sleep(SNAPSHOT_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
