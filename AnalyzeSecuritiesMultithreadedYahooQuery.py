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
import requests
#import sys

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
            if self.corporate_bond_yield != 0:
                self.intrinsic_value = str((EPS_TTM_float)*(8.5+GE_N5Y_float)*(4.4)/(self.corporate_bond_yield))
            else:
                self.intrinsic_value = "undefined"
            if list_price_float != 0:
                self.margin_of_safety = ((float(self.intrinsic_value))/(list_price_float))
            else:
                self.margin_of_safety = "undefined"
        except:
            self.intrinsic_value = "undefined"
            self.margin_of_safety = "undefined"

    def calculate_cash_flow_per_share(self):
        try:
            function_cash_flow = float(self.free_cash_flow_yfinance)
            function_shares_outstanding = float(self.shares_outstanding)
            if function_shares_outstanding != 0:
                self.cash_flow_per_share = (function_cash_flow/function_shares_outstanding)
            else:
                self.cash_flow_per_share = "undefined"
        except:
            self.cash_flow_per_share = "undefined"

    def calculate_intrinsic_value_with_cash_flow_per_share(self):
        try:
            cash_flow_float = float(self.cash_flow_per_share)
            GE_N5Y_float = float(self.GE_N5Y)
            list_price_float = float(self.list_price)
            if self.corporate_bond_yield != 0:
                self.intrinsic_value_cash_flow = str((cash_flow_float)*(8.5+GE_N5Y_float)*(4.4)/(self.corporate_bond_yield))
            else:
                self.intrinsic_value_cash_flow = "undefined"
            if list_price_float != 0:
                self.margin_of_safety_cash_flow = ((float(self.intrinsic_value_cash_flow))/(list_price_float))
            else:
                self.margin_of_safety_cash_flow = "undefined"

        except:
            self.intrinsic_value_cash_flow = "undefined"
            self.margin_of_safety_cash_flow = "undefined"

    def calculate_price_to_cash_flow(self):
        try:
            _cash_flow_per_share = float(self.cash_flow_per_share)
            _share_price = float(self.list_price)
            if _cash_flow_per_share != 0:
                self.price_to_cash_flow = (_share_price/_cash_flow_per_share)
            else:
                self.price_to_cash_flow = "undefined"
        except:
            self.price_to_cash_flow = "undefined"

def process_stock():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    while(1):

        #time.sleep(60)
        print(datetime.now().strftime("%H:%M:%S%f") + " " + threading.current_thread().name)
        stock_start_time = time.time()


        all_ticker_symbols_lock.acquire(blocking=True, timeout=60)
        i=len(all_ticker_symbols)
        if(len(all_ticker_symbols) == 0):
            all_ticker_symbols_lock.release()
            print(datetime.now().strftime("%H:%M:%S%f") + " " + "All Ticker Symbols length = 0. Exiting from loop for " + threading.current_thread().name)
            return
        symbol = all_ticker_symbols[0]
        all_ticker_symbols.remove(symbol)
        all_ticker_symbols_lock.release()

        newStock = Stock(aaa_corporate_bond_yield)
        newStock.ticker_symbol = symbol

        analysis_url = "https://www.gurufocus.com/term/earning_growth_5y_est/" + symbol
        req = urllib.request.Request(url=analysis_url, headers=headers)
        newStock.GE_N5Y = "N/A"

        try:
            analysis_page = urlopen(req)
            parsed_html = BeautifulSoup(analysis_page, 'html.parser')

            for tag in parsed_html.find_all('meta'):
                if "EPS Growth Rate (Future 3Y To 5Y Estimate) as of today" in (tag.get("content", None)):
                    my_string = tag.get("content", None)
                    my_substring = my_string.partition(" is ")[2]
                    my_value = my_substring.partition(". ")[0]
                    newStock.GE_N5Y = str(my_value)
                    break

        except:
            newStock.GE_N5Y = "N/A"
            pass

        if (newStock.GE_N5Y == "N/A"):
            analysis_url = "https://www.zacks.com/stock/quote/" + symbol + "/detailed-earning-estimates"
            req = urllib.request.Request(url=analysis_url, headers=headers)
            try:
                analysis_page = urlopen(req)
                parsed_html = BeautifulSoup(analysis_page, 'html.parser')

                for td in parsed_html.find_all('td'):
                    if td.text == "Next 5 Years":
                        newStock.GE_N5Y = str(td.nextSibling.nextSibling.text)
                        if (td.nextSibling.nextSibling.text == "NA"):
                            newStock.GE_N5Y = "N/A"
                        break

            except:
                newStock.GE_N5Y = "N/A"
                pass

        if (newStock.GE_N5Y == "N/A"):
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
                newStock.GE_N5Y = "N/A"
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
                    my_substring = my_string.partition(" is ")[2]
                    my_value = my_substring.partition(". ")[0]
                    newStock.RSI = my_value
        except:
                newStock.RSI = "N/A"
                pass

        try:
            temp_symbol = Ticker(symbol)
        except:
            continue
        
        try:
            try:
                newStock.EPS_TTM = str(temp_symbol.key_stats[symbol]['trailingEps'])
            except:
                newStock.EPS_TTM = "N/A"
                pass

            try:
                newStock.list_price = str(temp_symbol.summary_detail[symbol]['previousClose'])
            except:
                newStock.list_price = "N/A"
                pass

            try:
                newStock.free_cash_flow_yfinance = str(temp_symbol.financial_data[symbol]['freeCashflow'])
            except:
                newStock.free_cash_flow_yfinance = "N/A"
                pass

            try:
                newStock.shares_outstanding = str(temp_symbol.key_stats[symbol]['sharesOutstanding'])
            except:
                newStock.shares_outstanding = "N/A"
                pass

            try:
                newStock.totalCash = str(temp_symbol.financial_data[symbol]['totalCash'])
            except:
                newStock.totalCash = "N/A"
                pass

            try:
                newStock.total_cash_per_share = str(temp_symbol.financial_data[symbol]['totalCashPerShare'])
            except:
                newStock.total_cash_per_share = "N/A"
                pass

            try:
                newStock.country = str(temp_symbol.asset_profile[symbol]['country'])
            except:
                newStock.country = "N/A"
                pass

            try:
                newStock.price_to_book = str(temp_symbol.key_stats[symbol]['priceToBook'])
            except:
                newStock.price_to_book = "N/A"
                pass

            try:
                newStock.short_of_float = str(temp_symbol.key_stats[symbol]['shortPercentOfFloat'])
            except:
                newStock.short_of_float = "N/A"
                pass

            try:
                newStock.EV2 = str(temp_symbol.key_stats[symbol]['enterpriseValue'])
            except:
                newStock.EV2 = "N/A"
                pass

            try:
                newStock.day_low = str(temp_symbol.summary_detail[symbol]['dayLow'])
            except:
                newStock.day_low = "N/A"
                pass

            try:
                newStock.fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
            except:
                newStock.fifty_two_week_low = "N/A"
                pass

            try:
                newStock.debt_yfinance = str(temp_symbol.financial_data[symbol]['totalDebt'])
            except:
                newStock.debt_yfinance = "N/A"
                pass

            try:
                newStock.market_cap = str(temp_symbol.summary_detail[symbol]['marketCap'])
            except:
                newStock.market_cap = "N/A"
                pass

            try:
                newStock.name = str(temp_symbol.quote_type[symbol]['shortName'])
            except:
                newStock.name = "N/A"
                pass

            try:
                newStock.EV_EBITDA2 = str(temp_symbol.key_stats[symbol]['enterpriseToEbitda'])
            except:
                newStock.EV_EBITDA2 = "N/A"
                pass

            try:
                newStock.currency = str(temp_symbol.financial_data[symbol]['financialCurrency'])
            except:
                newStock.currency = "N/A"
                pass

            try:    
                newStock.recommendation_key = str(temp_symbol.financial_data[symbol]['recommendationKey'])
            except:
                newStock.recommendation_key = "N/A"
                pass

            try:
                newStock.sector = str(temp_symbol.asset_profile[symbol]['sector'])
            except:
                newStock.sector = "N/A"
                pass

            try:    
                newStock.industry = str(temp_symbol.asset_profile[symbol]['industry'])
            except:
                newStock.industry = "N/A"
                pass

            try:    
                newStock.insider_ownership = str(temp_symbol.key_stats[symbol]['heldPercentInsiders'])
            except:
                newStock.insider_ownership = "N/A"
                pass

            try:
                newStock.total_cash_minus_market_cap = str(temp_symbol.financial_data[symbol]['totalCash']-temp_symbol.summary_detail[symbol]['marketCap'])
            except:
                newStock.total_cash_minus_market_cap = "N/A"
                pass

            try:
                if (temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'] != 0):
                    newStock.current_price_over_fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['previousClose']/temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
                else:
                    newStock.current_price_over_fifty_two_week_low = "undefined"
            except:
                newStock.current_price_over_fifty_two_week_low = "N/A"
                pass
            
            try:
                if(temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'] != 0):
                    newStock.day_low_over_fifty_two_week_low = str(temp_symbol.summary_detail[symbol]['dayLow']/temp_symbol.summary_detail[symbol]['fiftyTwoWeekLow'])
                else:
                    newStock.day_low_over_fifty_two_week_low = "undefined"
            except:
                newStock.day_low_over_fifty_two_week_low = "N/A"
                pass

            newStock.calculate_intrinsic_value()
            newStock.calculate_cash_flow_per_share()
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
        except Exception:
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

        lock.acquire(blocking=True, timeout=60)
        allStocks.append(newStock)
        lock.release()

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S%f")

        print("* " + threading.current_thread().name + " " + current_time + ": " + str(i+len(allStocks)) + " *: " + str(i) + ": " + str((time.time() - stock_start_time))[:5] + ": "+ symbol + ": " + str(newStock.EPS_TTM) + ": " + str(newStock.GE_N5Y) + ": " + str(aaa_corporate_bond_yield) + ": " + str(newStock.list_price) + ": " + str(newStock.altman_z_score))
        del newStock

start_time = time.time()


#sys.stdout = open('./exe_out.txt', 'w')

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
for i in range (4):
    x = threading.Thread(target=process_stock)
    threads.append(x)
    x.start()

for thread in threads:
    thread.join()
    print(datetime.now().strftime("%H:%M:%S%f") + " Joined thread " + thread.name)

try:
    f = open("stock_selector.csv", "w", newline='')
    writer = csv.writer(f)
    writer.writerow(['TICKER SYMBOL', 'NAME', 'LIST PRICE', 'INTRINSIC VALUE', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'MARKET CAP', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY', 'RSI', 'INSIDER OWNERSHIP'])
    for currentStock in allStocks:
        writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.list_price, currentStock.intrinsic_value, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.market_cap, currentStock.recommendation_key ,currentStock.EV_EBITDA2, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry, currentStock.RSI, currentStock.insider_ownership])
    f.close()
except:
    input("It is likely that you left stock_selector.csv open.  Please close, or rename it and press Enter to continue...")
    f = open("stock_selector.csv", "w", newline='')
    writer = csv.writer(f)
    writer.writerow(['TICKER SYMBOL', 'NAME', 'LIST PRICE', 'INTRINSIC VALUE', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'MARKET CAP', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY', 'RSI', 'INSIDER OWNERSHIP'])
    for currentStock in allStocks:
        writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.list_price, currentStock.intrinsic_value, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.market_cap, currentStock.recommendation_key ,currentStock.EV_EBITDA2, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry, currentStock.RSI, currentStock.insider_ownership])
    f.close()

exe_time = time.time() - start_time
print("-------- Analyze Securities program took %s seconds to complete --------" % exe_time)
