# -*- coding: utf-8 -*-
'''
INITIALIZE
'''
# Import required packages
from datetime import datetime
import json
import os
import pandas as pd

# Turn off chained assignment warning
pd.options.mode.chained_assignment = None

'''
CLASS FOR APP
'''
# Load PredictIt data and update trading information
class History:

	# Initialize with most recent data in folder
	def __init__(self, path, starting_cash):

		# Get the file last modified date
		secs = os.stat(path).st_mtime
		mod = datetime.fromtimestamp(secs).strftime("%B %d, %Y %-I:%M%p")

		# Open the csv as a dataframe and clean the ($) and date format
		cols = ['Price', 'ProfitLoss', 'Fees', 'Risk', 'CreditDebit']
		df = clean_df(pd.read_csv(path, parse_dates=['DateExecuted']), cols)
		df['DateExecuted'] = df['DateExecuted'].dt.strftime('%Y-%m-%d %H:%M')

		# Encode for utf-8
		df['MarketName'] = df['MarketName'].str.encode('utf-8')

		# Reverse by the date and add a portfolio value and volume column
		df.sort_index(ascending=False, inplace=True)
		df['Invested'] = df['Risk'].cumsum().abs().round(2)
		df['Cash'] = df['CreditDebit'].cumsum().round(2) + int(starting_cash)
		df['Total'] = df['Invested'] + df['Cash'] 
		df['Volume'] = df['Shares'] * df['Price']

		# Set the variables for total performance
		invested = df['Invested'][0]
		cash = df['Cash'][0]
		total = df['Total'][0]
		perf = df['Total'][0] - starting_cash

		# Convert the dataframe to records
		line_records = df.to_dict(orient='records')
		line_data = json.dumps(line_records, indent=2)

		# Make a monthly df to get values for performance
		df['Month'] = df['DateExecuted'].map(lambda x: x[:7])
		month_df = df.groupby('Month').last().reset_index()[['Month', 'Total']]
		month_df.loc[-1] = ['2019-01', starting_cash]

		# Reset the index and perform the calculations
		month_df.sort_index(ascending=False, inplace=True)
		month_df.reset_index(drop=True, inplace=True)
		month_df['MonthDiff'] = month_df['Total'].diff(-1)
		month_df['InceptDiff'] = month_df['Total'] - starting_cash
		month_df['MonthReturn'] = month_df['MonthDiff'] / month_df['Total'].shift(-1)
		month_df['InceptReturn'] = month_df['InceptDiff'] / starting_cash

		# Round the columns
		month_df['MonthReturn'] = month_df['MonthReturn'].round(3)
		month_df['InceptReturn'] = month_df['InceptReturn'].round(3)

		# Find monthly volume and join to the month df
		volume_df = df.groupby('Month')['Volume'].sum().reset_index()
		month_df = pd.merge(month_df, volume_df, on='Month', how='left')

		# Send to records without the filler row and only take the last year
		month_df.drop(max(month_df.index), inplace=True)
		month_df = month_df.head(12)
		month_records = month_df.to_dict(orient='records')
		month_data = json.dumps(month_records, indent=2)

		# Find out if a contract is binary
		df['MarketID'] = df['URL'].str.split('/').str[-1]
		binary_df = df.loc[df['ContractName'].isin(['Yes', 'No'])]
		binary_df['Binary'] = True
		binary_df = binary_df[['MarketID','Binary']]
		binary_df.drop_duplicates(inplace=True)
		df = df.merge(binary_df, on='MarketID', how='left')
		df['Binary'].fillna(False, inplace=True)

		# If the contract is binary, replace the contract name with the yes/no order
		df.loc[~df['ContractName'].isin(['Yes', 'No']) & df['Binary'] == True, 
			'ContractName'] = df['Type']
		df.loc[df['ContractName'] == 'Sell Yes', 'ContractName'] = 'Yes'
		df.loc[df['ContractName'] == 'Sell No', 'ContractName'] = 'No'

		# Get the share activity for each contract type
		df['ContractType'] = df.apply(lambda x:
			'Yes' if x['Type'][-3:] == 'Yes' else 'No', axis=1)
		df['ShareActivity'] = df.apply(lambda x:
			x['Shares'] if x['Type'][:3] == 'Buy' else -x['Shares'], axis=1)

		# Get rid of closed markets
		closed_series = df['MarketID'].loc[df['Type'] == 'Closed']
		current_df = df.loc[~df['MarketID'].isin(closed_series)]

		# Only keep the active contracts
		contract_df = current_df.groupby(['MarketID', 'ContractName',
			'ContractType'])['ShareActivity'].sum().reset_index()
		contract_df.rename(columns={'ShareActivity': 'CurrentShares'}, inplace=True)
		contract_df = contract_df.loc[contract_df['CurrentShares'] > 0]

		# Get the market name and market investment
		risk_df = df.groupby(['MarketID', 'MarketName'])['Risk'].sum().abs().reset_index()
		contract_df = contract_df.merge(risk_df, on='MarketID', how='left')
		df['AmtTraded'] = df['Shares'] * df['Price']
		stats_df = df.groupby(['MarketID', 'ContractName', 'ContractType']).agg({
			'DateExecuted': 'max', 'AmtTraded': 'sum', 'Shares': 'sum'}).reset_index()
		contract_df = contract_df.merge(stats_df, on=['MarketID', 
			'ContractName', 'ContractType'], how='left')
		contract_df.sort_values(by=['Risk', 'CurrentShares'], ascending=False, inplace=True)

		# Send contracts to records
		contract_records = contract_df.to_dict(orient='records')

		# Get the best and worst performing markets
		value_df = df.groupby(['MarketID', 'MarketName']).agg({
			'Shares': 'sum', 'CreditDebit': 'sum', 'DateExecuted': 'max',
			'ShareActivity': 'sum'}).reset_index()
		value_df = value_df.loc[value_df['ShareActivity'] == 0]
		value_df.sort_values(by='CreditDebit', ascending=False, inplace=True)
		best_df = value_df.head(5)
		value_df.sort_values(by='CreditDebit', ascending=True, inplace=True)
		worst_df = value_df.head(5)
		
		# Send best and worst to records
		best_records = best_df.to_dict(orient='records')
		worst_records = worst_df.to_dict(orient='records')

		# Set the attributes
		self.mod = mod
		self.df = df
		self.invested = invested
		self.cash = cash
		self.total = total
		self.perf = perf
		self.line_records = line_records
		self.line_data = line_data
		self.month_records = month_records
		self.month_data = month_data
		self.contract_records = contract_records
		self.best_records = best_records
		self.worst_records = worst_records

# Function for cleaning the dataframe
def clean_df(df, col_lst):
	for col in col_lst:
		df[col] = df[col].replace('[\$,)]', '', regex=True)
		df[col] = df[col].replace('[(]','-', regex=True)
		df[col] = df[col].astype(float)
	return df


'''
EXECUTION IN TERMINAL
'''
# Run script in terminal for testing with local path and $50
if __name__ == '__main__':
	path = '/Users/joewlos/Documents/joe_web_new/static/data/TradeHistory.csv'
	predictit = History(path, 50.00)

	# Test something
	print predictit.worst_records