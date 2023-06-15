import copy
import math

dividend_history_dict = {'2020-07-31':20, '2020-10-30':35, '2021-01-29':25,
        '2021-04-30':200, '2022-04-29': 245, '2022-10-31':70}

def bgsf_signal(df):
    #Buy the greed, sell the fear
    signal = ['BID']
    signal_idx = 0
    value = None
    for idx, row in df.iterrows():
        if row['분류'] >= 100:
            if len(signal) and signal[-1]=='ASK':
                signal.extend(['HOLD']*(idx-signal_idx-1))
                signal_idx = idx
                signal.append('BID')
            elif not len(signal):
                signal_idx = idx
                signal.append('BID')
            value = row['분류']
        else:
            if value and row['분류'] < value:
                if len(signal) and signal[-1]=='BID':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('ASK')
            elif value and row['분류'] >= value:
                if len(signal) and signal[-1]=='ASK':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('BID')
            value = row['분류']
    signal += ['HOLD']*(len(df)-len(signal))
    df['signal'] = signal
    return df

def bfsg_signal(df):
    #Buy the fear, sell the greed
    signal = ['BID']
    signal_idx = 0
    value = None
    for idx, row in df.iterrows():
        if row['분류'] >= 100:
            if len(signal) and signal[-1]=='ASK':
                signal.extend(['HOLD']*(idx-signal_idx-1))
                signal_idx = idx
                signal.append('BID')
            elif not len(signal):
                signal_idx = idx
                signal.append('BID')
            value = row['분류']
        else:
            if value and row['분류'] < value:
                if len(signal) and signal[-1]=='ASK':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('BID')
            elif value and row['분류'] >= value:
                if len(signal) and signal[-1]=='BID':
                    signal.extend(['HOLD']*(idx-signal_idx-1))
                    signal_idx = idx
                    signal.append('ASK')
            value = row['분류']
    signal += ['HOLD']*(len(df)-len(signal))
    df['signal'] = signal
    return df

def dividen_strategy(df, money, fee):
    profit = []
    quantity = 0
    seed_money = copy.deepcopy(money)
    for idx, d in enumerate(df['날짜']):
        if len(profit)==0:
            quantity += money/df['시가'].iloc[idx]
            money -= quantity*df['시가'].iloc[idx]*(1 + fee)
        else:
            if d.strftime('%Y-%m-%d') in dividend_history_dict.keys():
                money += dividend_history_dict[d.strftime('%Y-%m-%d')]*quantity*0.846
        profit.append((money+quantity*df['종가'].iloc[idx])/seed_money)
    df['profit'] = profit

    return df

def backtest_inverse(df, money, strategy, fee):
    seed_money = copy.deepcopy(money)
    quantity, inverse_quantity = 0, 0
    position = None
    profit = [1]
    BID_count, ASK_count = 0, 0
    if strategy=='bfsg':
        price = '종가'
    else:
        price = '시가'
    for idx, row in df.iterrows():
        if idx+1>= len(df):
            continue
        if row['signal']=='BID':
            if math.isnan(df['시가_x'].iloc[idx+1]) or position==row['signal']:
                continue

            money += round(df['시가_y'].iloc[idx+1]*inverse_quantity*(1-fee), 2)
            inverse_quantity = 0 

            quantity += int(money/df['시가_x'].iloc[idx+1])
            money -= round(df['시가_x'].iloc[idx+1]*quantity*(1+fee), 2)

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
        price = '종가'
    else:
        price = '시가'
    for idx, row in df.iterrows():
        if row['날짜'].strftime('%Y-%m-%d') in dividend_history_dict and quantity:
            money += dividend_history_dict[row['날짜'].strftime('%Y-%m-%d')]*quantity*0.846
        if idx+1>= len(df):
            continue
        if row['signal']=='BID':
            if math.isnan(df['시가'].iloc[idx+1]) or position==row['signal']:
                continue

            quantity += int(money/df['시가'].iloc[idx+1])
            money -= round(df['시가'].iloc[idx+1]*quantity*(1+fee), 2)

            position='BID'
            BID_count+=1
        elif row['signal']=='ASK':
            if math.isnan(df[price].iloc[idx+1]) or position==row['signal']:
                continue

            money += round(df[price].iloc[idx+1]*quantity*(1-fee), 2)
            quantity = 0

            position='ASK'
            ASK_count+=1

        profit.append((money +df['종가'].iloc[idx+1]*quantity)/seed_money)

    df['profit'] = profit
    print(f"BID_count: {BID_count}, ASK_count: {ASK_count}")
    print(f"Profit: {profit[-1]}")

    return df