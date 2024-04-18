from urllib.request import urlopen, Request
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import time
import threading
from datetime import datetime
import csv
from yahooquery import Ticker

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
    RSI = ""
    insider_ownership = ""


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
        all_bad_tickers_lock.acquire(blocking=True, timeout=-1)
        print("Acquired all_ticker_symbols_lock...")
        i=len(all_bad_tickers)
        print("Grabbed i...")
        if(len(all_bad_tickers) == 0):
            print("Length of all_ticker_symbols is 0...")
            all_bad_tickers_lock.release()
            print("Releasing all_ticker_symbols_lock...")
            return
        print("Just before grabbing symbol...")
        symbol = all_bad_tickers[0]
        print("Grabbed " + symbol)
        all_bad_tickers.remove(symbol)
        print("Removing " + symbol)
        all_bad_tickers_lock.release()
        print("Releasing lock for " + symbol)

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

        rsi_url = "https://www.gurufocus.com/term/rsi_14/" + symbol + "/14-Day-RSI/"
        req = urllib.request.Request(url=rsi_url, headers=headers)
        newStock.RSI = "Not Found!"

        try:
            rsi_page = urlopen(req)
            rsi_html = BeautifulSoup(rsi_page, 'html.parser')

            for tag in rsi_html.find_all('meta'):
                if "14-Day RSI as of today" in (tag.get("content", None)):
                    my_string = tag.get("content", None)
                    my_substring = my_string.partition("is ")[2]
                    my_value = my_substring.partition(". ")[0]
                    newStock.RSI = my_value
        except:
                newStock.RSI = "N/A"
                pass

        print("Gonna try and populate stuff for " + symbol)
        temp_symbol = Ticker(symbol)
        try:
            print("created temp_symbol  " + symbol)
            newStock.EPS_TTM = str(temp_symbol.key_stats[symbol]['trailingEps'])
            newStock.list_price = str(temp_symbol.summary_detail[symbol]['previousClose'])
            newStock.calculate_intrinsic_value()

            try:
                newStock.free_cash_flow_yfinance = str(temp_symbol.financial_data[symbol]['freeCashflow'])
            except:
                pass

            newStock.shares_outstanding = str(temp_symbol.key_stats[symbol]['sharesOutstanding'])
            newStock.calculate_cash_flow_per_share()
            newStock.calculate_intrinsic_value_with_cash_flow_per_share()
            newStock.calculate_price_to_cash_flow()
            newStock.totalCash = str(temp_symbol.financial_data[symbol]['totalCash'])
            newStock.total_cash_per_share = str(temp_symbol.financial_data[symbol]['totalCashPerShare'])
            newStock.country = str(temp_symbol.asset_profile[symbol]['country'])

            try:
                newStock.price_to_book = str(temp_symbol.key_stats[symbol]['priceToBook'])
            except:
                pass

            try:
                newStock.short_of_float = str(temp_symbol.key_stats[symbol]['shortPercentOfFloat'])
            except:
                pass

            newStock.EV2 = str(temp_symbol.key_stats[symbol]['enterpriseValue'])
            newStock.day_low = str(temp_symbol.summary_detail[symbol]['dayLow'])
            newStock.fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
            newStock.debt_yfinance = str(temp_symbol.financial_data[symbol]['totalDebt'])
            newStock.market_cap = str(temp_symbol.summary_detail[symbol]['marketCap'])
            newStock.name = str(temp_symbol.quote_type[symbol]['shortName'])

            try:
                newStock.EV_EBITDA2 = str(temp_symbol.key_stats[symbol]['enterpriseToEbitda'])
            except:
                pass

            newStock.currency = str(temp_symbol.financial_data[symbol]['financialCurrency'])
            newStock.recommendation_key = str(temp_symbol.financial_data[symbol]['recommendationKey'])
            newStock.sector = str(temp_symbol.asset_profile[symbol]['sector'])
            newStock.industry = str(temp_symbol.asset_profile[symbol]['industry'])

            newStock.total_cash_minus_market_cap = str(temp_symbol.financial_data[symbol]['totalCash']-temp_symbol.summary_detail[symbol]['marketCap'])

            try:    
                newStock.insider_ownership = str(temp_symbol.key_stats[symbol]['heldPercentInsiders'])
            except:
                newStock.insider_ownership = "N/A"
                pass

            if (temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'] != 0):
                newStock.current_price_over_fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['previousClose']/temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
            
            if(temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'] != 0):
                newStock.day_low_over_fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['dayLow']/temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])

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
        req = urllib.request.Request(url=altman_url, headers=headers)

        newStock.altman_z_score = "Not Found!"
        try:
            altman_page = urlopen(req)
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
        lock.acquire(blocking=True, timeout=-1)
        all_bad_stocks.append(newStock)
        lock.release()

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        print("* " + current_time + ": " + str(i+len(all_bad_stocks)) + " *: " + str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": " + str(newStock.EPS_TTM) + ": " + str(newStock.GE_N5Y) + ": " + str(aaa_corporate_bond_yield) + ": " + str(newStock.list_price) + ": " + str(newStock.altman_z_score))
        del newStock

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
worst_stock_url = "https://www.investing.com/equities/top-stock-losers"
#worst_stock_url = "https://www.investing.com/equities/52-week-low"
req = urllib.request.Request(url=worst_stock_url, headers=headers)

all_bad_tickers = []
lock = threading.Lock()
all_bad_tickers_lock = threading.Lock()


worst_stock_page = urlopen(req)
parsed_html = BeautifulSoup(worst_stock_page, 'html.parser')
working_text = parsed_html.text
skipped_first = False
rough_tickers = working_text.split("|")
rough_tickers.pop(0)
for rough_ticker in rough_tickers:
    ticker = ""
    for character in rough_ticker:
        if character.isalpha():
            ticker += character
        else:
            all_bad_tickers.append(ticker)
            break

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

all_bad_stocks = []

start_time = time.time()
threads = list()
for i in range (4):
    x = threading.Thread(target=process_stock)
    threads.append(x)
    x.start()

for thread in threads:
    print("Joining thread")
    thread.join()

f = open("worst_stock_selector.csv", "w", newline='')
writer = csv.writer(f)
writer.writerow(['TICKER SYMBOL', 'NAME', 'LIST PRICE', 'INTRINSIC VALUE', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'MARKET CAP', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY', 'RSI', 'INSIDER OWNERSHIP'])
for currentStock in all_bad_stocks:
    writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.list_price, currentStock.intrinsic_value, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.market_cap, currentStock.recommendation_key ,currentStock.EV_EBITDA2, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry, currentStock.RSI, currentStock.insider_ownership])
f.close()

exe_time = time.time() - start_time
print("-------- Get worst stoch data program took %s seconds to complete --------" % exe_time)