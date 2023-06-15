import re
import pandas as pd

from tqdm import tqdm
import yfinance as yf

import en_strategy as es
from graph import en_make_fig

NAS_PATH = '/nas/DnCoPlatformDev/execution/kyeonghun.kim/investing'
tqdm.pandas()

def clean_text(text):
    text = " ".join(text.split('\n'))
    pattern = r'\([^)]*\)'
    text = re.sub(pattern=pattern, repl='', string=text).strip()
    if text.find('- ') != -1:
        text = text[text.find('- ')+2:]
    elif text.find(' -- ') != -1:
        text = text[text.find(' -- ')+4:]
    elif text.find(' – ') != -1:
        text = text[text.find(' – ')+3:]
    return text

def cal_NSI():

    df = pd.read_csv('./data/total_en_predict.csv', index_col=0)

    after_df = df[df['release_time']>='2019-01-01']
    after_df['release_time'] = pd.to_datetime(after_df['release_time'])
    tmp_df = after_df.set_index('release_time')

    negative = tmp_df[tmp_df['predict'] == 'Negative']
    positive = tmp_df[tmp_df['predict'] == 'Positive']

    negative = negative.resample('1D').count()  # 일 단위 빈도수 리샘플링
    positive = positive.resample('1D').count()  # 일 단위 빈도수 리샘플링

    negative_1D = negative['predict'].rolling(window=7).sum().dropna()
    positive_1D = positive['predict'].rolling(window=7).sum().dropna()
    X_t = (positive_1D - negative_1D)/(positive_1D + negative_1D)

    X_t_2019 = X_t[:'2019-12-31']
    X_t_2020 = X_t[:'2020-12-31']
    X_t_2021 = X_t[:'2021-12-31']
    X_t_2022 = X_t[:'2022-12-31']

    X_bar_2020 = X_t_2019.mean()
    S_2020 = X_t_2019.std()

    X_bar_2021 = X_t_2020.mean()
    S_2021 = X_t_2020.std()

    X_bar_2022 = X_t_2021.mean()
    S_2022 = X_t_2021.std()

    X_bar_2023 = X_t_2022.mean()
    S_2023 = X_t_2022.std()

    # final = ((X_t-X_bar)/S)*10+100
    NSI_2020 = ((X_t['2020-01-01':'2020-12-31']-X_bar_2020)/S_2020)*10+100
    NSI_2021 = ((X_t['2021-01-01':'2021-12-31']-X_bar_2021)/S_2021)*10+100
    NSI_2022 = ((X_t['2022-01-01':'2022-12-31']-X_bar_2022)/S_2022)*10+100
    NSI_2023 = ((X_t['2023-01-01':]-X_bar_2023)/S_2023)*10+100

    final = pd.concat([NSI_2020, NSI_2021, NSI_2022, NSI_2023])

    return final

def main():
    NSI = cal_NSI()

    SPY = yf.Ticker('SPY')
    SPY = SPY.history(period="1d", interval="1d", start='2020-01-02', end='2022-12-10')
    SPY = SPY.reset_index()
    SPY = es.dividen_strategy(SPY, 200000, 0.0005)

    snp500 = yf.Ticker('SPY')
    snpdf = snp500.history(period="1d", interval="1d", start='2020-01-02', end='2022-12-10')
    snpdf.index= snpdf.index.tz_localize(None)
    snpdf = snpdf.reset_index()
    
    snp_inverse = yf.Ticker('SPDN')
    snp_inverse = snp_inverse.history(period="1d", interval="1d", start='2020-01-02', end='2022-12-10')
    snp_inverse.index= snp_inverse.index.tz_localize(None)
    snp_inverse = snp_inverse.reset_index()

    NSI = NSI.reset_index()
    NSI['release_time'] = pd.to_datetime(NSI['release_time'])

    NSI_snp = pd.merge(NSI, snpdf, how='inner', left_on='release_time', right_on='Date')
    NSI_inverse= pd.merge(NSI_snp, snp_inverse, how='inner', left_on='release_time', right_on='Date')

    df = es.bfsg_signal(NSI_snp)
    df = es.backtest(df, 200000, 'bfsg', 0.0005)
    
    en_make_fig(df, SPY, 'bfsg')

if __name__ == '__main__':
    main()