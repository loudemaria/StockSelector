from urllib.request import urlopen, Request
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from yahooquery import Ticker
import yfinance as yf
import sys
import csv
import time
import threading
from datetime import datetime

class Stock:
    ticker_symbol = ""
    EPS_TTM = ""
    EV_EBITDA2 = ""
    EV2 = ""
    GE_N5Y = ""
    free_cash_flow_yfinance = ""
    totalCash = ""
    intrinsic_value = ""
    list_price = ""
    debt_yfinance = ""
    margin_of_safety = ""
    fifty_two_week_low = ""
    current_price_over_fifty_two_week_low = ""
    day_low_over_fifty_two_week_low = ""
    name = ""
    short_of_float = ""
    day_low = ""
    altman_z_score = ""
    price_to_book = ""
    market_cap = ""
    total_cash_minus_market_cap = ""
    total_cash_per_share = ""
    country = ""
    currency = ""
    shares_outstanding = ""
    recommendation_key = ""
    cash_flow_per_share = ""
    intrinsic_value_cash_flow = ""
    margin_of_safety_cash_flow = ""
    sector = ""
    industry = ""
    price_to_cash_flow = ""

    def __init__(self, aaa_corporate_bond_yield):
        self.corporate_bond_yield = aaa_corporate_bond_yield

    def calculate_intrinsic_value(self):
        try:
            EPS_TTM_float = float(self.EPS_TTM)
            GE_N5Y_float = float(self.GE_N5Y)
            list_price_float = float(self.list_price)
            self.intrinsic_value = str((EPS_TTM_float)*(8.5+GE_N5Y_float)*(4.4)/(self.corporate_bond_yield))
            if list_price_float != 0:
                self.margin_of_safety = ((float(self.intrinsic_value))/(list_price_float))
        except (ValueError, TypeError):
            self.intrinsic_value = "undefined"
            self.margin_of_safety = "undefined"

    def calculate_cash_flow_per_share(self):
        try:
            function_cash_flow = float(self.free_cash_flow_yfinance)
            function_shares_outstanding = float(self.shares_outstanding)
            if function_shares_outstanding != 0:
                self.cash_flow_per_share = (function_cash_flow/function_shares_outstanding)
        except:
            self.cash_flow_per_share = "undefined"

    def calculate_intrinsic_value_with_cash_flow_per_share(self):
        try:
            cash_flow_float = float(self.cash_flow_per_share)
            GE_N5Y_float = float(self.GE_N5Y)
            list_price_float = float(self.list_price)
            self.intrinsic_value_cash_flow = str((cash_flow_float)*(8.5+GE_N5Y_float)*(4.4)/(self.corporate_bond_yield))
            if list_price_float != 0:
                self.margin_of_safety_cash_flow = ((float(self.intrinsic_value_cash_flow))/(list_price_float))
        except (ValueError, TypeError):
            self.intrinsic_value_cash_flow = "undefined"
            self.margin_of_safety_cash_flow = "undefined"

    def calculate_price_to_cash_flow(self):
        try:
            _cash_flow_per_share = float(self.cash_flow_per_share)
            _share_price = float(self.list_price)
            if _cash_flow_per_share != 0:
                self.price_to_cash_flow = (_share_price/_cash_flow_per_share)
        except:
            self.price_to_cash_flow = "undefined"

def process_stock():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
    while(1):

        stock_start_time = time.time()

        print("Going to grab a ticker...")
        all_ticker_symbols_lock.acquire(blocking=True, timeout=60)
        print("Acquired all_ticker_symbols_lock...")
        i=len(all_ticker_symbols)
        print("Grabbed i...")
        if(len(all_ticker_symbols) == 0):
            print("Length of all_ticker_symbols is 0...")
            all_ticker_symbols_lock.release()
            print("Releasing all_ticker_symbols_lock...")
            return
        print("Just before grabbing symbol...")
        symbol = all_ticker_symbols[0]
        print("Grabbed " + symbol)
        all_ticker_symbols.remove(symbol)
        print("Removing " + symbol)
        all_ticker_symbols_lock.release()
        print("Relaasing lock for " + symbol)

        newStock = Stock(aaa_corporate_bond_yield)
        newStock.ticker_symbol = symbol
        analysis_url = "https://finance.yahoo.com/quote/" + symbol + "/analysis"
        req = urllib.request.Request(url=analysis_url, headers=headers)

        try:
            analysis_page = urlopen(req)
            parsed_html = BeautifulSoup(analysis_page, 'html.parser')

            for td in parsed_html.find_all('td'):
                if td.text == "Next 5 Years (per annum)":
                    tempString = td.nextSibling.text
                    newStock.GE_N5Y = tempString.replace("%", "")
        except:
            pass

        print("Gonna try and populate stuff for " + symbol)
        temp_symbol = Ticker(symbol)
        try:
            print("created temp_symbol  " + symbol)
            newStock.EPS_TTM = str(temp_symbol.key_stats[symbol]['trailingEps'])
            newStock.list_price = str(temp_symbol.summary_detail[symbol]['previousClose'])
            newStock.day_low = str(temp_symbol.summary_detail[symbol]['dayLow'])
            newStock.fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
            newStock.price_to_book = str(temp_symbol.key_stats[symbol]['priceToBook'])
            newStock.free_cash_flow_yfinance = str(temp_symbol.financial_data[symbol]['freeCashflow'])
            newStock.debt_yfinance = str(temp_symbol.financial_data[symbol]['totalDebt'])
            newStock.market_cap = str(temp_symbol.summary_detail[symbol]['marketCap'])
            newStock.totalCash = str(temp_symbol.financial_data[symbol]['totalCash'])
            newStock.total_cash_minus_market_cap = str(temp_symbol.financial_data[symbol]['totalCash']-temp_symbol.summary_detail[symbol]['marketCap'])

            if (temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'] != 0):
                newStock.current_price_over_fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['previousClose']/temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
            
            if(temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'] != 0):
                newStock.day_low_over_fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['dayLow']/temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])

            newStock.name = str(temp_symbol.quote_type[symbol]['shortName'])
            newStock.short_of_float = str(temp_symbol.key_stats[symbol]['shortPercentOfFloat'])
            newStock.EV2 = str(temp_symbol.key_stats[symbol]['enterpriseValue'])
            newStock.EV_EBITDA2 = str(temp_symbol.key_stats[symbol]['enterpriseToEbitda'])
            newStock.total_cash_per_share = str(temp_symbol.financial_data[symbol]['totalCashPerShare'])
            newStock.country = str(temp_symbol.asset_profile[symbol]['country'])
            newStock.currency = str(temp_symbol.financial_data[symbol]['financialCurrency'])
            newStock.shares_outstanding = str(temp_symbol.key_stats[symbol]['sharesOutstanding'])
            newStock.recommendation_key = str(temp_symbol.financial_data[symbol]['recommendationKey'])
            newStock.sector = str(temp_symbol.asset_profile[symbol]['sector'])
            newStock.industry = str(temp_symbol.asset_profile[symbol]['industry'])
            newStock.calculate_cash_flow_per_share()
            newStock.calculate_intrinsic_value()
            newStock.calculate_intrinsic_value_with_cash_flow_per_share()
            newStock.calculate_price_to_cash_flow()

            print("Populated ALLLLLL the things for  " + symbol)
        except IndexError:
            print(str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": Index Error")
            pass
        except ValueError:
            print(str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": Value Error")
            pass
        except KeyError:
            print(str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": Key Error")
            pass
        except:
            print(str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": Unexpected Error")
            pass

        altman_url = "https://www.gurufocus.com/term/zscore/" + symbol + "/Altman-Z-Score"
        newStock.altman_z_score = "Not Found!"
        try:
            altman_page = urlopen(altman_url)
            parsed_html = BeautifulSoup(altman_page, 'html.parser')
            
            for tag in parsed_html.find_all('meta'):
                if "Altman Z-Score as of today" in (tag.get("content", None)):
                    my_string = tag.get("content", None)
                    my_substring = my_string.partition("is ")[2]
                    my_value = my_substring.partition(". ")[0]
                    newStock.altman_z_score = my_value

        except Exception:
            print(str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": GuruFocus Altman Z-Score not found")
            pass

        print("Through exceptions for " + symbol)
        lock.acquire(blocking=True, timeout=60)
        allStocks.append(newStock)
        lock.release()

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        print("* " + current_time + ": " + str(i+len(allStocks)) + " *: " + str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": " + str(newStock.EPS_TTM) + ": " + str(newStock.GE_N5Y) + ": " + str(aaa_corporate_bond_yield) + ": " + str(newStock.list_price) + ": " + str(newStock.altman_z_score))
        del newStock

start_time = time.time()

lock = threading.Lock()
all_ticker_symbols_lock = threading.Lock()
allStocks = []
all_ticker_symbols = []

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

yield_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
aaa_corporate_bond_yield = 0
aaa_corporate_bond_yield_url = "https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield"
yield_req = urllib.request.Request(url=aaa_corporate_bond_yield_url, headers=yield_headers)
aaa_corporate_bond_yield_page = urlopen(yield_req)
aaa_corporate_bond_yield_parsed_html = BeautifulSoup(aaa_corporate_bond_yield_page, 'html.parser')
for td in aaa_corporate_bond_yield_parsed_html.find_all('td'):
    if td.text == "Last Value":
        aaa_corporate_bond_yield = td.nextSibling.nextSibling.text
        aaa_corporate_bond_yield = float(aaa_corporate_bond_yield.replace("%", ""))

threads = list()
for i in range (6):
    x = threading.Thread(target=process_stock)
    threads.append(x)
    x.start()

for thread in threads:
    print("Joining thread")
    thread.join()

f = open("stock_selector.csv", "w", newline='')
writer = csv.writer(f)
writer.writerow(['TICKER SYMBOL', 'NAME', 'LIST PRICE', 'INTRINSIC VALUE', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'MARKET CAP', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY'])
for currentStock in allStocks:
    writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.list_price, currentStock.intrinsic_value, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.market_cap, currentStock.recommendation_key ,currentStock.EV_EBITDA2, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry])
f.close()

exe_time = time.time() - start_time
print("-------- Analyze Securities program took %s seconds to complete --------" % exe_time)
