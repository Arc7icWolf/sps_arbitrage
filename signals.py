from pools import POOLS
from tokens import TOKENS
from balances import read_pool

def main():
    for name, pool in POOLS.items():
        balances = read_pool(pool, TOKENS)

        print(f"\n{name}")
        for sym, bal in balances.items():
            print(f"  {sym} : {bal}")

if __name__ == "__main__":
    main()
