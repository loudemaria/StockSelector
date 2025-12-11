import requests
import numpy as np
from scipy.stats import linregress
from bs4 import BeautifulSoup

api_key = 'JNOHODP86K2H317K'

allStocks = []
all_ticker_symbols = []

nasdaqlisted_url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
otherlisted_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
filename1 = "nasdaqlisted.txt"
filename2 = "otherlisted.txt"

response = requests.get(nasdaqlisted_url)
html = response.content
soup = BeautifulSoup(html, "html.parser")
text = soup.get_text()
lines = text.splitlines()
non_empty_lines = [line for line in lines if line.strip()]
result = "\n".join(non_empty_lines)
with open("nasdaqlisted.txt", "w") as f:
    f.write(result)

response = requests.get(otherlisted_url)
html = response.content
soup = BeautifulSoup(html, "html.parser")
text = soup.get_text()
lines = text.splitlines()
non_empty_lines = [line for line in lines if line.strip()]
result = "\n".join(non_empty_lines)
with open("otherlisted.txt", "w") as f:
    f.write(result)

with open ('nasdaqlisted.txt') as my_file:
    for my_line in my_file:
        my_line = my_line.split("|")
        if (len(my_line[0]) < 6):
            my_line[0] = my_line[0].replace(".","-")
            all_ticker_symbols.append(my_line[0])

with open ('otherlisted.txt') as my_file:
    for my_line in my_file:
        my_line = my_line.split("|")
        if (len(my_line[0]) < 6):
            my_line[0] = my_line[0].replace(".","-")
            all_ticker_symbols.append(my_line[0])



for ticker_symbol in all_ticker_symbols:
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol=' + ticker_symbol+ '&apikey=' + api_key
    r = requests.get(url)
    data = r.json()
    if len(data) > 0:
        operating_cash_flow = data['quarterlyReports'][0]['operatingCashflow']
        capital_expenditures = data['quarterlyReports'][0]['capitalExpenditures']
        print(int(operating_cash_flow) - int(capital_expenditures))


fcf = []


for i in range(22):
    operating_cash_flow = data['quarterlyReports'][i]['operatingCashflow']
    capital_expenditures = data['quarterlyReports'][i]['capitalExpenditures']
    fcf.append(int(operating_cash_flow) - int(capital_expenditures))

fcf_latest = int(operating_cash_flow) - int(capital_expenditures)

# Perform linear regression
slope, intercept, r_value, p_value, std_err = linregress(time_index, data_series)

# The 'slope' is the linear growth rate
linear_growth_rate = slope

print(f"The linear growth rate is: {linear_growth_rate:.2f}")
