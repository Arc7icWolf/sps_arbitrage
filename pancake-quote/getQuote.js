import { ChainId } from '@pancakeswap/chains'
import { WBNB } from '@pancakeswap/tokens'
import { SmartRouter } from '@pancakeswap/smart-router'
import { TradeType } from '@pancakeswap/sdk'
import { createPublicClient, http, parseUnits } from 'viem'

// RPC della BSC
const client = createPublicClient({
  chain: {
    id: ChainId.BSC,
    name: 'BNB Smart Chain',
    network: 'bsc',
    nativeCurrency: {
      decimals: 18,
      name: 'BNB',
      symbol: 'BNB'
    },
    rpcUrls: {
      default: { http: ['https://bsc-dataseed.binance.org'] }
    },
  },
  transport: http(),
})

// Token che vuoi acquistare
const TOKEN_OUT = {
  address: '0x1C45366641014069114c78962bDc371F534Bc81c',
  decimals: 18,
  symbol: 'MYTOKEN'
}

// Token di input (BNB -> WBNB)
const tokenIn = WBNB[ChainId.BSC]
const tokenOut = TOKEN_OUT

// Quantità di BNB da scambiare (0.01 BNB)
const amountIn = parseUnits('0.01', 18) // BNB ha 18 decimali

async function getQuote() {
  console.log('Fetching best quote from PancakeSwap...')

  const quote = await SmartRouter.getBestTrade({
    client,
    currencyAmountIn: {
      currency: tokenIn,
      amount: amountIn
    },
    currencyOut: tokenOut,
    tradeType: TradeType.EXACT_INPUT, // ✅ sostituisce SmartRouterTradeType
  })

  if (!quote) {
    console.log('❌ Nessuna route trovata.')
    return
  }

  console.log('✅ Miglior route trovata:')
  console.log(`Token ricevuti: ${quote.amountOut.toExact()} ${tokenOut.symbol}`)
  console.log(`Prezzo medio: ${quote.executionPrice.toSignificant(6)}`)
  console.log('Route dettagliata:', quote.route.path.map(t => t.symbol).join(' -> '))
}

getQuote().catch(console.error)
