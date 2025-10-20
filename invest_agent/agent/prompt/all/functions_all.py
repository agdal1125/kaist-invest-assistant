EXCHANGE_HISTORY = {
	"type": "function",
	"function": {
		"name": "exchange_history",
		"description": "환전내역를 확인. 기간 설정을 길게하여 함수를 여러번 호출하지 않도록 해야함",
		"parameters": {
			"type": "object",
			"properties": {
				"start_date": {
					"type": "string",
					"description": "YYYY-MM-DD의 형태."
				},
				"end_date": {
					"type": "string",
					"description": "YYYY-MM-DD의 형태."
				}
			},
			"required": [
				"start_date",
				"end_date"
			]
		}
	}
}

EXCHANGE = {
	"type": "function",
	"function": {
		"name": "exchange",
		"description": "환전를 수행",
		"parameters": {
			"type": "object",
			"properties": {
				"currency_code": {
					"type": "string",
					"description": "KRW, USD, JPY, EUR 등 보유통화의 코드"
				},
				"exchange_currency_code": {
					"type": "string",
					"description": "KRW, USD, JPY, EUR 등 환전할 통화의 코드"
				},
				"exchange_amount": {
					"type": "number",
					"description": "환전할 금액 (보유통화기준)"
				}
			},
			"required": [
				"currency_code",
				"exchange_currency_code",
				"exchange_amount"
			]
		}
	}
}

FOREIGN_STOCK_CONCLUSION_HISTORY = {
	"type": "function",
	"function": {
		"name": "foreign_stock_conclusion_history",
		"description": "해외주식의 체결내역을 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"transaction_type": {
					"type": "string",
					"description": "전체/체결/미체결 중 하나를 입력하라."
				},
				"trade_type": {
					"type": "string",
					"description": "전체/매수/매도 중 하나를 입력하라."
				},
				"transaction_date": {
					"type": "string",
					"description": "YYYY-MM-DD의 형태로 입력하라."
				}
			},
			"required": [
				"transaction_type",
				"trade_type",
				"transaction_date"
			]
		}
	}
}

FOREIGN_STOCK_CURRENT_PRICE = {
	"type": "function",
	"function": {
		"name": "foreign_stock_current_price",
		"description": "해외주식의 현재가를 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"country_code": {
					"type": "string",
					"description": "USA, JPN 중 하나를 입력하라."
				},
				"stock_code": {
					"type": "string",
					"description": "TSLA, 7974 등 종목코드를 입력하라."
				}
			},
			"required": [
				"country_code",
				"stock_code"
			]
		}
	}
}

STOCK_CURRENT_PRICE = {
	"type": "function",
	"function": {
		"name": "stock_current_price",
		"description": "주식 현재가를 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"stock_code": {
					"type": "string",
					"description": "034730 등 종목코드를 입력하라."
				}
			},
			"required": [
				"stock_code"
			]
		}
	}
}

DIVIDEND = {
	"type": "function",
	"function": {
		"name": "dividend",
		"description": "배당을 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"confirmed": {
					"type": "string",
					"description": "확정+예상/확정/예상 중 하나"
				},
				"period": {
					"type": "string",
					"description": "YYYY-1, YYYY, YYYY+1 중 하나"
				}
			},
			"required": [
				"confirmed",
				"period"
			]
		}
	}
}

STOCK_COLLECTION = {
	"type": "function",
	"function": {
		"name": "stock_collection",
		"description": "주식모으기 메뉴를 실행",
	}
}

DOMESTIC_STOCK_CONCLUSION_HISTORY = {
	"type": "function",
	"function": {
		"name": "domestic_stock_conclusion_history",
		"description": "국내주식 체결내역을 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"type": {
					"type": "string",
					"description": "전체/체결/미체결 중 하나"
				},
				"sub_type": {
					"type": "string",
					"description": "전체/매수/매도 중 하나"
				},
				"date": {
					"type": "string",
					"description": "YYYY-MM-DD의 형태"
				}
			},
			"required": [
				"type",
				"sub_type",
				"date"
			]
		}
	}
}

DOMESTIC_STOCK_PROFIT_LOSS = {
	"type": "function",
	"function": {
		"name": "domestic_stock_profit_loss",
		"description": "국내주식의 잔고와 손익을 확인",
	}
}

FOREIGN_STOCK_TRANSACTION_HISTORY = {
	"type": "function",
	"function": {
		"name": "foreign_stock_transaction_history",
		"description": "해외주식 거래내역을 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"account": {
					"type": "string",
					"description": ""
				},
				"category": {
					"type": "string",
					"description": "전체/입금/출금/입고/출고/매수/매도 중 하나"
				},
				"type": {
					"type": "string",
					"description": "전체/외화주식/외화채권/외화warrant/외화수익증권/외화뮤추얼 중 하나"
				},
				"period": {
					"type": "string",
					"description": "1주/1개월/3개월/YYYY-MM-DD~YYYY-MM-DD 형태"
				}
			},
			"required": [
				"account",
				"category",
				"type",
				"period"
			]
		}
	}
}

INDEX_EXCHANGE_RATE = {
	"type": "function",
	"function": {
		"name": "index_exchange_rate",
		"description": "지수와 환율을 확인",
	}
}

BOND_ORDER = {
	"type": "function",
	"function": {
		"name": "bond_order",
		"description": "발행어음 매매를 수행",
		"parameters": {
			"type": "object",
			"properties": {
				"product_name": {
					"type": "string",
					"description": "NH QV 발행어음_개인"
				},
				"investment_period": {
					"type": "string",
					"description": "YYYY-MM-DD~YYYY-MM-DD 형태"
				},
				"account": {
					"type": "string",
					"description": "계좌번호"
				},
				"amount": {
					"type": "number",
					"description": "매수금액"
				}
			},
			"required": [
				"product_name",
				"investment_period",
				"account",
				"amount"
			]
		}
	}
}

FOREIGN_BOND_ORDER = {
	"type": "function",
	"function": {
		"name": "foreign_bond_order",
		"description": "외화발행어음 매매를 수행",
		"parameters": {
			"type": "object",
			"properties": {
				"product_name": {
					"type": "string",
					"description": "NH QV USD 발행어음_개인"
				},
				"investment_period": {
					"type": "string",
					"description": ""
				},
				"account": {
					"type": "string",
					"description": ""
				},
				"amount": {
					"type": "number",
					"description": ""
				}
			},
			"required": [
				"product_name",
				"investment_period",
				"account",
				"amount"
			]
		}
	}
}

ACCOUNT_ASSET_HISTORY = {
	"type": "function",
	"function": {
		"name": "account_asset_history",
		"description": "계좌의 자산추이를 확인",
	}
}

TRANSFER = {
	"type": "function",
	"function": {
		"name": "transfer",
		"description": "이체를 수행",
		"parameters": {
			"type": "object",
			"properties": {
				"amount": {
					"type": "number",
					"description": "이체할 금액"
				},
				"bank_name": {
					"type": "string",
					"description": "은행명"
				},
				"account_number": {
					"type": "string",
					"description": "계좌번호"
				},
				"password": {
					"type": "string",
					"description": "비밀번호"
				}
			},
			"required": [
				"amount",
				"bank_name",
				"account_number",
				"password"
			]
		}
	}
}

IPO_GUIDE = {
	"type": "function",
	"function": {
		"name": "ipo_guide",
		"description": "공모청약이용가이드를 확인",
	}
}

TOTAL_ASSET = {
	"type": "function",
	"function": {
		"name": "total_asset",
		"description": "통합자산을 확인",
	}
}

INTEREST_GROUP = {
	"type": "function",
	"function": {
		"name": "interest_group",
		"description": "관심그룹을 확인",
		"parameters": {
			"type": "object",
			"properties": {
				"group_name": {
					"type": "string",
					"description": "국내 종목 실시간 BEST, 국내투자고수의 선택, 국내종목순위, 해외 종목 실시간 Best, etc. + 사용자설정그룹1, 사용자설정그룹2, …"
				}
			},
			"required": [
				"group_name"
			]
		}
	}
}

TRANSACTION_HISTORY = {
	"type": "function",
	"function": {
		"name": "transaction_history",
		"description": "거래내역을 확인",
	}
}

FUNCTIONS_ALL = [
	EXCHANGE_HISTORY,
	EXCHANGE,
	FOREIGN_STOCK_CONCLUSION_HISTORY,
	FOREIGN_STOCK_CURRENT_PRICE,
	STOCK_CURRENT_PRICE,
	DIVIDEND,
	STOCK_COLLECTION,
	DOMESTIC_STOCK_CONCLUSION_HISTORY,
	DOMESTIC_STOCK_PROFIT_LOSS,
	FOREIGN_STOCK_TRANSACTION_HISTORY,
	INDEX_EXCHANGE_RATE,
	BOND_ORDER,
	FOREIGN_BOND_ORDER,
	ACCOUNT_ASSET_HISTORY,
	TRANSFER,
	IPO_GUIDE,
	TOTAL_ASSET,
	INTEREST_GROUP,
	TRANSACTION_HISTORY,
]

