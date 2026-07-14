## Automation Backend (REST & STREAM WEBSOCKET)

## Test Scope

### 1. Spot Trading API (REST)

Fetch Order Book `(GET /api/v3/depth)`

Place Limit Order `(POST /api/v3/order)`

Fetch Open Orders `(GET /api/v3/openOrders)`

Fetch Trade History `(GET /api/v3/myTrades)`

Fetch Account Balance `(GET /api/v3/account)`

### 2. WebSocket (Market Data & Order Updates)

Subscribe to the Order Book stream `(wss://stream.binance.com:9443/ws/<symbol>@depth)`

Subscribe to the Trade stream `(wss://stream.binance.com:9443/ws/<symbol>@trade)`

Subscribe to User Data stream `(wss://stream.binance.com:9443/ws via listenKey)`

## Notes

listenKey was deprecated since 2026-01-21 https://github.com/binance/binance-spot-api-docs/blob/master/CHANGELOG.md. So I use ws userDataStream.subscribe.signature https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-api/user-data-stream#user-data-stream-subscribe-signature