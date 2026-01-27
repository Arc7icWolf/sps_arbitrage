import asyncio
from pools import POOLS
from tokens import TOKENS
from balances import read_pool_async

async def main():
    tasks = []

    for name, pool in POOLS.items():
        tasks.append(
            read_pool_async(pool, TOKENS)
        )

    results = await asyncio.gather(*tasks)

    for (name, _), balances in zip(POOLS.items(), results):
        print(f"\n{name}")
        for sym, bal in balances.items():
            print(f"  {sym} : {bal}")

if __name__ == "__main__":
    asyncio.run(main())
