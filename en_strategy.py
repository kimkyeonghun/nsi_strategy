import math
import copy

dividend_history_dict = {'2020-03-20':1.41, '2020-06-19':1.37, '2020-09-18':1.34, '2020-12-18':1.58, '2021-03-19':1.28, '2021-06-18':1.38,
'2021-09-17':1.43,'2021-12-17':1.64,'2022-03-18':1.37,'2022-06-17':1.58,'2022-09-16':1.60,'2022-12-16':1.78}

def dividen_strategy(SPY, money, fee):
    profit = []
    seed_money = copy.deepcopy(money)
    quantity = 0
    for idx, d in enumerate(SPY.Date):
        if len(profit)==0:
            quantity += money/SPY['Open'].iloc[idx]
            money -= quantity*SPY['Open'].iloc[idx]*(1 + fee)
        else:
            if d.strftime('%Y-%m-%d') in dividend_history_dict.keys():
                money += dividend_history_dict[d.strftime('%Y-%m-%d')]*quantity*0.846

        profit.append((money+quantity*SPY['Close'].iloc[idx])/seed_money)
    SPY['profit'] = profit

    return SPY

def bgsf_signal(df):
    signal = []
    value = None
    for idx, row in df.iterrows():
        if row['predict'] >= 100:
            if len(signal) and signal[-1]=='ASK':
                signal.extend(['HOLD']*(idx-signal_idx-1))
                signal_idx = idx
                signal.append('BID')
            elif not len(signal):
                signal_idx = idx
                signal.append('BID')
            value = row['predict']
        else:
            if value and row['predict'] < value:
                if len(signal) and signal[-1]=='BID':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('ASK')
            elif value and row['predict'] >= value:
                if len(signal) and signal[-1]=='ASK':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('BID')
            value = row['predict']
    signal += ['HOLD']*(len(df)-len(signal))
    df['signal'] = signal
    return df

def bfsg_signal(df):
    signal = []
    value = None
    for idx, row in df.iterrows():
        if row['predict'] >= 100:
            if len(signal) and signal[-1]=='ASK':
                signal.extend(['HOLD']*(idx-signal_idx-1))
                signal_idx = idx
                signal.append('BID')
            elif not len(signal):
                signal_idx = idx
                signal.append('BID')
            value = row['predict']
        else:
            if value and row['predict'] < value:
                if len(signal) and signal[-1]=='ASK':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('BID')
            elif value and row['predict'] >= value:
                if len(signal) and signal[-1]=='BID':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('ASK')
            value = row['predict']

    signal += ['HOLD']*(len(df)-len(signal))
    df['signal'] = signal
    return df

def backtest_inverse(df, money, strategy, fee):
    seed_money = copy.deepcopy(money)
    quantity, inverse_quantity = 0, 0
    position = None
    profit = [1]
    BID_count, ASK_count = 0, 0
    if strategy=='bfsg':
        price = 'Close'
    else:
        price = 'Open'
    for idx, row in df.iterrows():
        if idx+1>= len(df):
            continue
        if row['signal']=='BID':
            if math.isnan(df['Open_x'].iloc[idx+1]) or position==row['signal']:
                continue

            money += round(df['Open_y'].iloc[idx+1]*inverse_quantity*(1-fee), 2)
            inverse_quantity = 0 

            quantity += int(money/df['Open_x'].iloc[idx+1])
            money -= round(df['Open_x'].iloc[idx+1]*quantity*(1+fee), 2)

            position='BID'
            BID_count+=1
        elif row['signal']=='ASK':
            if math.isnan(df[price+'_x'].iloc[idx+1]) or position==row['signal']:
                continue

            money += round(df[price+'_x'].iloc[idx+1]*quantity*(1-fee), 2)
            quantity = 0

            position='ASK'
            ASK_count+=1

            inverse_quantity += int(money/df[price+'_y'].iloc[idx+1])
            money -= round(df[price+'_y'].iloc[idx+1]*inverse_quantity*(1+fee), 2)

        profit.append((money +df['종가'].iloc[idx+1]*quantity)/seed_money)
        
    df['profit'] = profit
    print(f"BID_count: {BID_count}, ASK_count: {ASK_count}")
    print(f"Profit: {profit[-1]}")

    return df

def backtest(df, money, strategy, fee):
    seed_money = copy.deepcopy(money)
    quantity = 0
    position = None
    profit = [1]
    BID_count, ASK_count = 0, 0
    if strategy=='bfsg':
        price = 'Close'
    else:
        price = 'Open'
    for idx, row in df.iterrows():
        if row['Date'].strftime('%Y-%m-%d') in dividend_history_dict and quantity:
            money += dividend_history_dict[row['Date'].strftime('%Y-%m-%d')]*quantity*0.846
        if idx+1>= len(df):
            continue
        if row['signal']=='BID':
            if math.isnan(df['Open'].iloc[idx+1]) or position==row['signal']:
                continue
            
            quantity += int(money/df['Open'].iloc[idx+1])
            money -= round(df['Open'].iloc[idx+1]*quantity*(1+fee), 2)
            
            position='BID'
            BID_count+=1
        elif row['signal']=='ASK':
            if math.isnan(df[price].iloc[idx+1]) or position==row['signal']:
                continue
            
            money += round(df[price].iloc[idx+1]*quantity*(1-fee), 2)
            quantity = 0

            position='ASK'
            ASK_count+=1

        profit.append((money +df['Close'].iloc[idx+1]*quantity)/seed_money)
    df['profit'] = profit

    print(f"BID_count: {BID_count}, ASK_count: {ASK_count}")
    print(f"Profit: {profit[-1]}")

    return df