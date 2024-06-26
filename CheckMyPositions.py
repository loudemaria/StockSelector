from urllib.request import urlopen, Request
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import yfinance as yf
from yahooquery import Ticker
import sys
import csv
import time
import threading

class Stock:
    ticker_symbol = ""
    sector = ""
    shares_held = ""
    price_paid = ""
    market_price_paid = ""
    market_value = ""
    intrinsic_market_value = ""
    percent_ownership = ""
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

    def calculate_market_value(self):
        try:
            self.market_value = float(self.shares_held) * float(self.list_price)
        except:
            self.market_value = "undefined"

    def calculate_full_price_paid(self):
        try:
            self.market_price_paid = float(self.shares_held) * float(self.price_paid)
        except:
            self.market_price_paid = "undefined"

    def calculate_intrinsic_market_value(self):
        try:
            self.intrinsic_market_value = float(self.shares_held) * float(self.intrinsic_value)
        except:
            self.intrinsic_market_value = "undefined"

    def calculate_percent_ownership(self):
        try:
            float_shares_held = float(self.shares_held)
            float_shares_outstanding = float(self.shares_outstanding)
            if float_shares_outstanding != 0:
                self.percent_ownership = (float_shares_held/float_shares_outstanding)
        except:
            self.percent_ownership = "undefined"

def process_stock():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
    while(1):

        stock_start_time = time.time()

        all_ticker_symbols_lock.acquire(blocking=True, timeout=-1)
        i=len(all_ticker_symbols)
        if(len(all_ticker_symbols) == 0):
            all_ticker_symbols_lock.release()
            break
        symbol = all_ticker_symbols[0]
        price_paid = all_ticker_symbols[1]
        number_of_shares = all_ticker_symbols[2]
        all_ticker_symbols.remove(symbol)
        all_ticker_symbols.remove(price_paid)
        all_ticker_symbols.remove(number_of_shares)
        all_ticker_symbols_lock.release()

        newStock = Stock(aaa_corporate_bond_yield)
        newStock.ticker_symbol = symbol
        newStock.price_paid = price_paid;
        newStock.shares_held = number_of_shares
        analysis_url = "https://finance.yahoo.com/quote/" + symbol + "/analysis"
        req = urllib.request.Request(url=analysis_url, headers=headers)

        try:
            analysis_page = urlopen(req)
            parsed_html = BeautifulSoup(analysis_page, 'html.parser')

            for td in parsed_html.find_all('td'):
                if td.text == "Next 5 Years (per annum)":
                    tempString = td.previous_element.contents[2].text
                    newStock.GE_N5Y = tempString.replace("%", "")
        except:
            pass

        temp_symbol = Ticker(symbol)
        try:
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
            newStock.calculate_market_value()
            newStock.calculate_full_price_paid()
            newStock.calculate_intrinsic_market_value()
            newStock.calculate_percent_ownership()
            newStock.calculate_intrinsic_value_with_cash_flow_per_share()
            newStock.calculate_price_to_cash_flow()

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
        req = urllib.request.Request(url=altman_url, headers=headers)

        newStock.altman_z_score = "Not Found!"
        try:
            altman_page = urlopen(req)
            parsed_html = BeautifulSoup(altman_page, 'html.parser')
            
            for tag in parsed_html.find_all('meta'):
                if "Altman Z-Score as of today" in (tag.get("content", None)):
                    my_string = tag.get("content", None)
                    my_substring = my_string.partition(" is ")[2]
                    my_value = my_substring.partition(". ")[0]
                    newStock.altman_z_score = my_value

        except Exception:
            print(str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": GuruFocus Altman Z-Score not found")
            newStock.altman_z_score = "N/A"
            pass

        lock.acquire(blocking=True, timeout=-1)
        allStocks.append(newStock)
        lock.release()

        print("* " + str(i+len(allStocks)) + " *: " + str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": " + str(newStock.EPS_TTM) + ": " + str(newStock.GE_N5Y) + ": " + str(aaa_corporate_bond_yield) + ": " + str(newStock.list_price) + ": " + str(newStock.altman_z_score))

start_time = time.time()

starting_balance = 31081.46

lock = threading.Lock()
all_ticker_symbols_lock = threading.Lock()
allStocks = []
all_ticker_symbols = []

with open ('mystocks.txt') as my_file:
    for my_line in my_file:
        my_line = my_line.split("|")
        if (len(my_line[0]) < 6):
            my_line[0] = my_line[0].replace(".","-")
            all_ticker_symbols.append(my_line[0])
            all_ticker_symbols.append(my_line[1])
            all_ticker_symbols.append(my_line[2])

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
for i in range (2):
    x = threading.Thread(target=process_stock)
    threads.append(x)
    x.start()

for i, thread in enumerate(threads):
    thread.join()

f = open("my_stocks.csv", "w", newline='')
writer = csv.writer(f)
writer.writerow(['TICKER SYMBOL', 'NAME', 'SHARES HELD', 'PAID PRICE', 'LIST PRICE', 'INTRINSIC VALUE', 'PAID VALUE', 'MARKET VALUE', 'INTRINSIC VALUE POSITION', 'PERCENT OWNERSHIP', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY'])
for currentStock in allStocks:
    writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.shares_held,  currentStock.price_paid, currentStock.list_price, currentStock.intrinsic_value, currentStock.market_price_paid, currentStock.market_value, currentStock.intrinsic_market_value, currentStock.percent_ownership, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.recommendation_key ,currentStock.EV_EBITDA2, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry])
writer.writerow(['STARTING BALANCE', starting_balance])
f.close()

exe_time = time.time() - start_time

print("-------- Analyze my securities program took %s seconds to complete --------" % exe_time)