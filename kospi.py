from pykrx import stock
import pandas as pd

import ko_strategy as ks
from graph import ko_make_fig

def cal_NSI():
    predict_df = pd.read_csv('data/total_predict.csv', index_col=0)
    predict_df['일자'] = pd.to_datetime(predict_df['일자'], format='%Y%m%d')
    predict_df = predict_df.set_index('일자')

    negative = predict_df[predict_df['분류'] == 'negative']
    positive = predict_df[predict_df['분류'] == 'positive']

    negative = negative.resample('1D').count()  # 일 단위 빈도수 리샘플링
    positive = positive.resample('1D').count()  # 일 단위 빈도수 리샘플링

    negative_1D = negative['분류'].rolling(window=7).sum().dropna()
    positive_1D = positive['분류'].rolling(window=7).sum().dropna()

    X_t = (positive_1D - negative_1D)/(positive_1D + negative_1D)

    #재표준화
    X_t_2019 = X_t[:'2020-06-30']
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
    NSI_2020 = ((X_t['2020-07-01':'2020-12-31']-X_bar_2020)/S_2020)*10+100
    NSI_2021 = ((X_t['2021-01-01':'2021-12-31']-X_bar_2021)/S_2021)*10+100
    NSI_2022 = ((X_t['2022-01-01':'2022-12-31']-X_bar_2022)/S_2022)*10+100
    NSI_2023 = ((X_t['2023-01-01':]-X_bar_2023)/S_2023)*10+100

    df = pd.concat([NSI_2020, NSI_2021, NSI_2022, NSI_2023])
    df = df.reset_index()
    df['일자'] = pd.to_datetime(df['일자'])

    return df


def main():
    NSI = cal_NSI()
    #TODO: end_date will be today or yesterday
    #277630: TIGER 코스피
    kospi = stock.get_etf_ohlcv_by_date("20200701", '20230116', "277630")
    kospi = kospi.reset_index()
    KOSPI = ks.dividen_strategy(kospi, 200000, 0.0005)
    #123310: TIGER 코스피인버스
    kospi_inverse = stock.get_etf_ohlcv_by_date("20200701", '20230116','123310')

    NSI_kospi = pd.merge(NSI, kospi, how='right', left_on='일자', right_on='날짜')
    NSI_inverse = pd.merge(NSI_kospi, kospi_inverse, how='right', left_on='일자', right_on='날짜')
    
    #if 배당?
    
    df = ks.bfsg_signal(NSI_kospi)
    df = ks.backtest(df, 200000, 'bfsg', 0.0005)
    ko_make_fig(df, KOSPI, 'bfsg')

if __name__ == '__main__':
    main()
