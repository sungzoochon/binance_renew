import ccxt 
import time
import datetime
import pandas as pd
api_key = '6zHOZK1HIAidFdxoGxHR5GB85VOqCZ7VbbKXdBz8Ne6XfFUG4feKcPfVw15o0Ew1'
secret = 'PevYip6CONYhgYKdNTVnGjIYGS03hptq09jqUgsCUlLFlJJXJ7KcTXUyGmJmEVcl'
binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': False,
    'options': {
        'defaultType': 'future'
    }
})
def CCI(coin):
 btc_ohlcv = binance.fetch_ohlcv(coin, '15m',limit = 15)
 df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
 TP = (df['high'] + df['low'] + df['close'])/3      
 SMA = TP.rolling(15).mean()
 MAD = TP.rolling(15).apply(lambda x: pd.Series(x).mad())
 CCI = ((TP - SMA) / (0.015 * MAD))
 return CCI[14]
def BOLL(coin):
 btc_ohlcv = binance.fetch_ohlcv(coin, '15m',limit = 21)
 df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
 MA = df['close'].rolling(window=20,min_periods=1).mean()
 SD = df['close'].rolling(window = 20, min_periods=1).std()
 UB = MA + (SD*2)
 LB = MA - (SD*2)
 return UB[20],MA[20],LB[20],df['close'][20]
def RSI(coin):
 btc_ohlcv = binance.fetch_ohlcv(coin, '15m', limit = 200)
 df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
 delta = df['close'].diff(1)
 delta = delta.dropna()
 up = delta.copy()
 down = delta.copy()
 up[ up < 0 ] = 0
 down[ down > 0 ] = 0
 time_period = 14
 AVG_Gain = up.ewm(com=time_period-1, min_periods=time_period).mean()
 AVG_Loss = abs(down.ewm(com=time_period-1, min_periods=time_period).mean())
 RS = AVG_Gain / AVG_Loss
 RSI = 100.0 - (100.0/(1.0 + RS))
 return RSI
def stochastic(data, k_window, d_window, window):
    min_val  = data.rolling(window=window, center=False ).min()
    max_val = data.rolling(window=window, center=False).max()
    stoch = ( (data - min_val) / (max_val - min_val) ) * 100
    K = stoch.rolling(window=k_window, center=False).mean()  
    D = K.rolling(window=d_window, center=False).mean() 
    return K, D
def cal_amount(usdt_balance, cur_price):
   try: 
    amount = ((usdt_balance * 1000000)/cur_price) / 1000000
    return amount 
   except Exception as e:
     None
def enter_position(exchange, coin,coin_amount, position):
   if position == 'long': 
        coin2 = coin.replace("/","")
        binance.fapiPrivate_post_leverage({  
            'symbol': coin2,  
            'leverage': Leverage,  
        })
        exchange.create_market_buy_order(
            symbol= coin, 
            amount= coin_amount * Leverage * 0.95,                
            params={'type': 'future'})
        LONG_AMOUNT.append((coin_amount*Leverage)*0.95)
        LONG_BUY_LIST.append(coin)
        LONG_PRICE_LIST.append(cur_price)
       # print(coin,"수량:",round(cal_amount(one_usdt, cur_price),3),"USDT값:",one_usdt,"롱",now.hour,":",now.minute)         
   if position == 'short': 
        coin2 = coin.replace("/","")
        binance.fapiPrivate_post_leverage({  
            'symbol': coin2,  
            'leverage': Leverage,  
        })
        exchange.create_market_sell_order(
            symbol= coin, 
            amount= coin_amount * Leverage * 0.95,             
            params={'type': 'future'})
        SHORT_AMOUNT.append((coin_amount*Leverage)*0.95)
        SHORT_BUY_LIST.append(coin)
        SHORT_PRICE_LIST.append(cur_price) 
       # print(coin,"수량:",round(cal_amount(one_usdt, cur_price),3),"USDT값:",one_usdt,"숏",now.hour,":",now.minute)
def exit_position(exchange,i,position):
  if position == 'short':
      coin = SHORT_BUY_LIST[i]
      exchange.create_market_buy_order(symbol=coin, amount=SHORT_AMOUNT[i])
  if position == 'long': 
      coin = LONG_BUY_LIST[i]   
      exchange.create_market_sell_order(symbol=coin, amount=LONG_AMOUNT[i])

LIST = ['BTC','ETH','XRP','SOL','EOS','BNB','ETC','LINK','ATOM','MATIC','HNT','ADA','CHZ','ATA','RSR','DOT','GMT','AVAX','APE','NEAR','ALGO','LTC','UNI','BLZ','FIL','BEL','CRV','LUNA2','OP','ENS','REEF','AXS']
LONG_BUY_LIST = []
SHORT_BUY_LIST = []
LONG_PRICE_LIST = []
SHORT_PRICE_LIST = []
LONG_AMOUNT = []
SHORT_AMOUNT = []
Long_candidate_list = []
Short_candidate_list = []
Long_Max = []
Short_Max = []
Leverage = 3

while True:
 try:    
  for i in LIST:
   I = i + '/USDT'
   now = datetime.datetime.now()   
   time.sleep(0.5) 
   K,D = stochastic(RSI(I),3,3,14)
   balance = binance.fetch_balance()        
   usdt = balance['total']['USDT'] 
   ticker = binance.fetch_ticker(I)
   cur_price = ticker['last']
   
   if (-240 <= CCI(I) <= -210) and (cur_price < BOLL(I)[2]) and ((K[199] + D[199])/2 < 5) and (I not in LONG_BUY_LIST) and (len(LONG_BUY_LIST) + len(SHORT_BUY_LIST) < 5) and I not in Long_candidate_list:
    ticker = binance.fetch_ticker(I)
    cur_price = ticker['last']
    Long_candidate_list.append(I)
    Long_Max.append(cur_price)
 
   if (240 >= CCI(I) >= 220) and (cur_price > BOLL(I)[0]) and ((K[199] + D[199])/2 > 95) and (I not in SHORT_BUY_LIST) and (len(SHORT_BUY_LIST) + len(LONG_BUY_LIST) < 5) and  I not in Short_candidate_list and now.hour != 9:
    ticker = binance.fetch_ticker(I)
    cur_price = ticker['last']
    Short_candidate_list.append(I) 
    Short_Max.append(cur_price)  
    
   for i in range(len(LONG_BUY_LIST)):
    if len(LONG_BUY_LIST) > i:
     ticker = binance.fetch_ticker(LONG_BUY_LIST[i])
     cur_price = ticker['last']
     K,D = stochastic(RSI(LONG_BUY_LIST[i]),3,3,14)
     if CCI(LONG_BUY_LIST[i]) >= 200 or cur_price > BOLL(LONG_BUY_LIST[i])[0]:
      exit_position(binance,i,position='long')
      print(LONG_BUY_LIST[i],"up")
      LONG_BUY_LIST.remove(LONG_BUY_LIST[i])
      LONG_PRICE_LIST.remove(LONG_PRICE_LIST[i])
      LONG_AMOUNT.remove(LONG_AMOUNT[i])
      continue
     if cur_price/LONG_PRICE_LIST[i] < 0.95:  
      exit_position(binance,i,position='long')
      print(LONG_BUY_LIST[i],"down")
      LONG_BUY_LIST.remove(LONG_BUY_LIST[i])
      LONG_PRICE_LIST.remove(LONG_PRICE_LIST[i])
      LONG_AMOUNT.remove(LONG_AMOUNT[i])

   for i in range(len(SHORT_BUY_LIST)):
    if len(SHORT_BUY_LIST) > i:
     ticker = binance.fetch_ticker(SHORT_BUY_LIST[i])
     cur_price = ticker['last']
     if CCI(SHORT_BUY_LIST[i]) <= -200 or cur_price < BOLL(SHORT_BUY_LIST[i])[2]:
      exit_position(binance,i,position='short')
      print(SHORT_BUY_LIST[i],"up")
      SHORT_BUY_LIST.remove(SHORT_BUY_LIST[i])
      SHORT_PRICE_LIST.remove(SHORT_PRICE_LIST[i])
      SHORT_AMOUNT.remove(SHORT_AMOUNT[i])
      continue
     if cur_price/SHORT_PRICE_LIST[i] > 1.05:
      exit_position(binance,i,position='short')
      print(SHORT_BUY_LIST[i],"down")
      SHORT_BUY_LIST.remove(SHORT_BUY_LIST[i])
      SHORT_PRICE_LIST.remove(SHORT_PRICE_LIST[i])
      SHORT_AMOUNT.remove(SHORT_AMOUNT[i]) 

   for i in Long_candidate_list:
    ticker = binance.fetch_ticker(i)
    cur_price = ticker['last']
    if cur_price < Long_Max[Long_candidate_list.index(i)]:
       Long_Max[Long_candidate_list.index(i)] = cur_price        
    if cur_price/Long_Max[Long_candidate_list.index(i)] > 1.005:  
       one_usdt = usdt/5           
       enter_position(binance,i,cal_amount(one_usdt, cur_price)*0.95,position = 'long') 
       Long_Max.remove(Long_Max[Long_candidate_list.index(i)])
       Long_candidate_list.remove(i)
       
   for i in Short_candidate_list:
    ticker = binance.fetch_ticker(i)
    cur_price = ticker['last']
    if cur_price > Short_Max[Short_candidate_list.index(i)]:
       Short_Max[Short_candidate_list.index(i)] = cur_price
    if cur_price/Short_Max[Short_candidate_list.index(i)] < 0.995:
       one_usdt = usdt/5
       enter_position(binance,i,cal_amount(one_usdt, cur_price)*0.95,position = 'short') 
       Short_Max.remove(Short_Max[Short_candidate_list.index(i)])     
       Short_candidate_list.remove(i)
           
  
 except Exception as e:
    #print(e)
    time.sleep(1)
    

  



 
