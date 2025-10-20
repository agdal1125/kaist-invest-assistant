

STOCK_BUY = {
	"type": "function",
	"function": {
		"name": "stock_buy",
		"description": "매수 주문 수행. 주식의 종목명이나 종목코드는 필요치않음.",
		"parameters": {
			"type": "object",
			"properties": {
				"ticker": {
					"type": "string",
					"description": "주식의 티커명. 예: MSFT, NVDA, META"
				},
				"order_code": {
					"type": "string",
					"description": "주문코드: 01(보통가), 05(시장가) 등."
				},
				"quantity": {
					"type": "number",
					"description": "주문할 수량."
				},
				"price": {
					"type": "number",
					"description": "주문할 단가. 필수적이지 않은 경우 -1을 입력하라."
				}
			},
			"required": [
				"ticker",
				"order_code",
				"quantity",
				"price"
			]
		}
	}
}

STOCK_SELL = {
	"type": "function",
	"function": {
		"name": "stock_sell",
		"description": "매도 주문 수행. 주식의 종목명이나 종목코드는 필요치않음.",
		"parameters": {
			"type": "object",
			"properties": {
				"ticker": {
					"type": "string",
					"description": "주식의 티커명. 예: MSFT, NVDA, META"
				},
				"order_code": {
					"type": "string",
					"description": "주문코드: 01(보통가), 05(시장가) 등."
				},
				"quantity": {
					"type": "number",
					"description": "주문할 수량"
				},
				"price": {
					"type": "number",
					"description": "주문할 단가. 필수적이지 않은 경우 -1을 입력하라."
				}
			},
			"required": [
				"ticker",
				"order_code",
				"quantity",
				"price"
			]
		}
	}
}


FUNCTIONS_TRADE = [
	STOCK_BUY,
	STOCK_SELL,
]