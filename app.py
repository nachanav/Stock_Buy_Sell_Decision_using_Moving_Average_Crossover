import streamlit as st
import mplfinance as mpf
import pandas as pd
import datetime
from PIL import Image


@st.cache(show_spinner=False)
def get_graph(df, no_days):
    plot_df = df.iloc[-no_days:]
    plot_df = plot_df.set_index('Date')
    filename = 'CandelPlot.png'
    mpf.plot(plot_df,type='candle',mav=(21, 55), style="yahoo", figratio=(60,20), linecolor='#00ff00', savefig=filename)
    
def buy_sell_decision(st, lt, close, last):
    # checking for null values
    if st == 'None' or lt == 'None':
        return 'Dont trade', close, last
    
    if st >= lt:
        if close >= st:
          return 'Buy', last, None

        elif close <= st:
          return 'sell', None, last

    if lt > st :
        return 'Dont trade', close, last
    
def get_SMA_df(df):
    moving_average_df = df
    moving_average_df['St21'] = moving_average_df['Close'].rolling(window = 21, min_periods = 21).mean()
    moving_average_df['Lt55'] = moving_average_df['Close'].rolling(window = 55, min_periods = 55).mean()
    moving_average_df = moving_average_df.fillna('None')
    
    # computing buy asd sell days
    st_list = moving_average_df['St21'].to_list()
    lt_list = moving_average_df['Lt55'].to_list()
    close_price_list = moving_average_df['Close'].to_list()
    last_price_list = moving_average_df['Last'].to_list()

    buy_sell_list = []
    buy_price_list = []
    sell_price_list = []

    for idx, value in enumerate(st_list):
        dec_label, buy_price, sell_price = buy_sell_decision(st_list[idx], lt_list[idx], close_price_list[idx], last_price_list[idx])

        buy_sell_list.append(dec_label)
        buy_price_list.append(buy_price)
        sell_price_list.append(sell_price)

    moving_average_df['buy/sell'], moving_average_df['buy_price'], moving_average_df['sell_price'] = buy_sell_list, buy_price_list, sell_price_list
    return moving_average_df

def get_action_dict(sma_df, date):
    df = sma_df.set_index('Date')
    try:
        row = df.loc[datetime.datetime(date.year, date.month, date.day)]
        action_dict = {}
        action_dict['symbol'] = row['Symbol']
        action_dict['action'] = row['buy/sell']
        if action_dict['action'] == 'Buy':
            price = row['buy_price']
        else:
            price = row['sell_price']
        
        action_dict['price'] = price
    except:
        action_dict = None
    return action_dict

def main():
    st.set_page_config(
        page_title="Project",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.write('Upload a CSV file')

    col1, col2 = st.columns(2)
    
    with col1:
        spectra = st.file_uploader("upload file", type={"csv", "txt"})
        if spectra is not None:
            df = pd.read_csv(spectra)
            df['Date'] = df['Date'].astype('datetime64[ns]')
            sma_df =get_SMA_df(df)
        
            plot_days = st.slider('Select No. of days to plot graph', 56, len(df), 100)
            st.write("Plot graph for last", plot_days, 'days')
            
        get_image = st.button('Get graph')
        
    if spectra is not None:    
        with col2:
            trade_date = st.date_input("Select Day for trading", max(df['Date']), min_value=min(df['Date']), max_value=max(df['Date']))
            get_action = st.button('Check trade or No trade')
            ref_flag = False
            
            if get_action:
                dict_action = get_action_dict(sma_df, trade_date)
                if dict_action == None:
                    st.error("Something Went Wrong please try with different date", icon="🚨")
                else:
                    symbol = dict_action['symbol']
                    action = dict_action['action']
                    price = dict_action['price']
                    st.success(f'''
                                * Symbol : {symbol}
                                * Action : **{action}**
                                * {action} Price : {price} 
                            ''')
                    ref_flag, get_image = True, True
                            
    if get_image:
        get_graph(df, plot_days)
        image = Image.open('CandelPlot.png')
        st.image(image, use_column_width='auto', caption='Blue Line = 21-SMA, Orange Line = 55-SMA')
        
if __name__ == '__main__':
    main()