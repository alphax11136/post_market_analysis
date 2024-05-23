import streamlit as st
import pandas as pd
from io import StringIO
import pandas as pd


def calculate_alpha(row):
    lot_size = 40  # Default lot size for FINNIFTY
    
    if 'BANKNIFTY' in row['Portfolio']:
        lot_size = 25
    elif 'FINNIFTY' in row['Portfolio']:
        lot_size = 40
    elif 'MIDCPNIFTY' in row['Portfolio']:
        lot_size = 15
    elif 'NIFTY' in row['Portfolio']:
        lot_size = 25
    
    alpha = (row['TRDPARITY'] - row['ParityAsked']) * row['QTY'] * lot_size
    return alpha


def main():

    st.title("Post Market Analysis")
    
    # uploaded_file = st.file_uploader("Choose a .txt file", type="txt")
    uploaded_files = st.file_uploader("Choose .txt files", type="txt", accept_multiple_files=True)

    if uploaded_files:

        all_data = []

        for uploaded_file in uploaded_files:
            
            dealer_id = uploaded_file.name.split('.txt')[0] 

            replacements = {
                            '_': '', 
                            '4L': '', 
                            '4l': '',
                            'trades': '', 
                            'Trades': '',
                            'TRADES' : ''
                        }

            # Apply all replacements
            for old, new in replacements.items():
                dealer_id = dealer_id.replace(old, new)


            file_content = uploaded_file.read().decode("utf-8")
            lines = file_content.splitlines()

            # Initialize a list to store parsed data
            data = []
            
            # Loop through each line
            for line in lines:
                if '|' in line:  # Skip lines that do not contain '|'
                    # Split the line by the '|' separator
                    fields = line.split('|')
                    
                    # Remove leading and trailing whitespace from each field
                    fields = [field.strip() for field in fields]

                    # Append the fields to the data list
                    data.append(fields)

            # Create a DataFrame from the data list
            df = pd.DataFrame(data, columns=[
                'Timestamp', 'Description', 'TRDPARITY', 'QTY', 'ParityWas', 
                'OpnCls', 'OrdNumL1', 'OrdNumL2', 'OrdNumL3', 'OrdNumL4', 'M2M'
            ])

            # Define a function to clean the values
            def clean_values(series, col_name):
                return series.str.replace(f'{col_name}:', '', regex=False)

            # Apply the function to each column except Timestamp and Description
            for col in df.columns:
                if col not in ['Timestamp', 'Description']:
                    df[col] = clean_values(df[col], col)

            columns_to_remove = ['OrdNumL1','OrdNumL2','OrdNumL3','OrdNumL4','M2M']
            df.drop(columns=columns_to_remove, inplace=True)

            # Convert specific columns to integer
            df['TRDPARITY'] = df['TRDPARITY'].astype(int)/ 100
            df['QTY'] = df['QTY'].astype(int)
            df['ParityWas'] = df['ParityWas'].astype(int)/ 100


            new_columns = {
                'Description': 'Portfolio',
                'ParityWas': 'ParityAsked',
            }

            df = df.rename(columns=new_columns)

            #! Apply the alpha function to each row

            df['alpha'] = df.apply(calculate_alpha, axis=1)

            #! Alpha %

            positive_alpha = round(df[df['alpha'] > 0]['alpha'].sum(),2)
            negative_alpha = round(df[df['alpha'] < 0]['alpha'].sum(),2)
            net_alpha = round(positive_alpha + negative_alpha,2)

            # print(f'% positive_alpha : {positive_alpha}\n% negative_alpha : {negative_alpha}\n% net_alpha : {net_alpha}')

            #! Alpha Events

            positive_alpha_events = f'{round(((df['alpha'] >= 0).sum()/len(df))*100,2)} %'
            negative_alpha_events = f'{round(((df['alpha'] < 0).sum()/len(df))*100,2)} %'

            # print(f'% positive_alpha_events : {positive_alpha_events}\n% negative_alpha_events : {negative_alpha_events}')

            #! Top 5 profitable/Lossers alphas

            grouped_df = df.groupby('Portfolio', as_index=False)['alpha'].sum()
            top_5_df = grouped_df.nlargest(5, 'alpha')
            bottom_5_df = grouped_df.nsmallest(5, 'alpha')

            #! Final dataframe 

            top_alpha_portfolio = top_5_df['Portfolio'].to_list()
            bottom_alpha_portfolio = bottom_5_df['Portfolio'].to_list()

            data = {
                    'dealer_id' : dealer_id,

                    'positive_alpha_events' : [positive_alpha_events],
                    'negative_alpha_events' : [negative_alpha_events],
                    
                    'positive_alpha' : [positive_alpha],
                    'negative_alpha' : [negative_alpha],
                    'net_alpha' : [net_alpha],

                    't1' : [top_alpha_portfolio[0]],
                    't2' : [top_alpha_portfolio[1]],
                    't3' : [top_alpha_portfolio[2]],
                    't4' : [top_alpha_portfolio[3]],
                    't5' : [top_alpha_portfolio[4]],

                    'b1' : [bottom_alpha_portfolio[0]],
                    'b2' : [bottom_alpha_portfolio[1]],
                    'b3' : [bottom_alpha_portfolio[2]],
                    'b4' : [bottom_alpha_portfolio[3]],
                    'b5' : [bottom_alpha_portfolio[4]]   
                }

            df_per_dealer = pd.DataFrame(data)
            all_data.append(df_per_dealer)


        # Concatenate all dataframes into a single dataframe
        df_all_dealer = pd.concat(all_data, ignore_index=True)
        st.dataframe(df_all_dealer)


#########! Main #########!
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()


# streamlit run app.py
