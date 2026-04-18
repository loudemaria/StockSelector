from urllib.request import urlopen, Request
import urllib.request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import yfinance as yf
import sys
import csv
import time
import threading
from datetime import datetime
import requests
import git
import ssl

def get_headers():
    # Creating headers.
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,'
                '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'accept-language': 'en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
      'dpr': '1',
      'sec-fetch-dest': 'document',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-site': 'none',
      'sec-fetch-user': '?1',
      'upgrade-insecure-requests': '1',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    return headers

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
        all_ticker_symbols_lock.acquire(blocking=True, timeout=60)
        print("Acquired all_ticker_symbols_lock...")
        i=len(all_ticker_symbols)
        print("Grabbed i...")
        if(len(all_ticker_symbols) == 0):
            print("Length of all_ticker_symbols is 0...")
            all_ticker_symbols_lock.release()
            print("Releasing all_ticker_symbols_lock...")
            break
        print("Just before grabbing symbol...")
        symbol = all_ticker_symbols[0]
        print("Grabbed " + symbol)
        all_ticker_symbols.remove(symbol)
        print("Removing " + symbol)
        all_ticker_symbols_lock.release()
        print("Relaasing lock for " + symbol)

        newStock = Stock(aaa_corporate_bond_yield)
        newStock.ticker_symbol = symbol

        analysis_url = "https://finviz.com/quote.ashx?t=" + symbol
        req = urllib.request.Request(url=analysis_url, headers=get_headers())
        newStock.GE_N5Y = "N/A"

        try:
            analysis_page = urlopen(req)
            parsed_html = BeautifulSoup(analysis_page, 'html.parser')

            for td in parsed_html.find_all('td'):
                if td.text == "EPS next 5Y":
                    tempString = td.nextSibling.text
                    if (tempString != "-"):
                        newStock.GE_N5Y = tempString.replace("%", "")
        except:
            newStock.GE_N5Y = "N/A"
            pass

        if (newStock.GE_N5Y == "N/A"):
            try:
                analysis_url = "https://www.gurufocus.com/term/earning_growth_5y_est/" + symbol
                req = urllib.request.Request(url=analysis_url, headers=get_headers())
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
            req = urllib.request.Request(url=analysis_url, headers=get_headers())
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

        rsi_url = "https://www.gurufocus.com/term/rsi_14/" + symbol + "/14-Day-RSI/"
        newStock.RSI = "Not Found!"

        try:
            rsi_page = urlopen(rsi_url)
            rsi_html = BeautifulSoup(rsi_page, 'html.parser')

            for tag in rsi_html.find_all('meta'):
                if "14-Day RSI as of today" in (tag.get("content", None)):
                    my_string = tag.get("content", None)
                    my_substring = my_string.partition("is ")[2]
                    my_value = my_substring.partition(". ")[0]
                    newStock.RSI = my_value
        except:
            pass

        print("Gonna try and populate stuff for " + symbol)
        temp_symbol = yf.Ticker(symbol)
        try:
            print("created temp_symbol  " + symbol)
            temp_info = temp_symbol.info
            temp_fast_info = temp_symbol.fast_info
            print("got info for  " + symbol)
            newStock.EPS_TTM = str(temp_info['trailingEps'])
            newStock.list_price = str(temp_symbol.fast_info.previous_close)
            newStock.day_low = str(temp_symbol.fast_info.day_low)
            newStock.fifty_two_week_low = str(temp_symbol.fast_info.year_low)
            newStock.price_to_book = str(temp_info['priceToBook'])
            newStock.free_cash_flow_yfinance = str(temp_info['freeCashflow'])
            newStock.debt_yfinance = str(temp_info['totalDebt'])
            newStock.market_cap = str(temp_symbol.fast_info.market_cap)
            newStock.totalCash = str(temp_info['totalCash'])
            newStock.total_cash_minus_market_cap = str(temp_info['totalCash']-temp_symbol.fast_info.market_cap)

            if (temp_symbol.fast_info.year_low != 0):
                newStock.current_price_over_fifty_two_week_low = str(temp_symbol.fast_info.previous_close/temp_symbol.fast_info.year_low)
            
            if(temp_symbol.fast_info.day_low != 0):
                newStock.day_low_over_fifty_two_week_low = str(temp_symbol.fast_info.day_low/temp_symbol.fast_info.year_low)

            newStock.name = str(temp_info['shortName'])
            newStock.short_of_float = str(temp_info['shortPercentOfFloat'])
            newStock.EV2 = str(temp_info['enterpriseValue'])
            newStock.EV_EBITDA2 = str(temp_info['enterpriseToEbitda'])
            newStock.total_cash_per_share = str(temp_info['totalCashPerShare'])
            newStock.country = str(temp_info['country'])
            newStock.currency = str(temp_symbol.fast_info.currency)
            newStock.shares_outstanding = str(temp_info['sharesOutstanding'])
            newStock.recommendation_key = str(temp_info['recommendationKey'])
            print("JUST before sector and industry for  " + symbol)
            newStock.sector = str(temp_info['sector'])
            newStock.industry = str(temp_info['industry'])

            try:    
                newStock.insider_ownership = str(temp_symbol.key_stats[symbol]['heldPercentInsiders'])
            except:
                newStock.insider_ownership = "N/A"
                pass

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

ssl._create_default_https_context = ssl._create_unverified_context
yield_headers = get_headers()
aaa_corporate_bond_yield = 0
aaa_corporate_bond_yield_url = "https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield"
yield_req = urllib.request.Request(url=aaa_corporate_bond_yield_url, headers=yield_headers)
aaa_corporate_bond_yield_page = urlopen(yield_req)
aaa_corporate_bond_yield_parsed_html = BeautifulSoup(aaa_corporate_bond_yield_page, 'html.parser')
for td in aaa_corporate_bond_yield_parsed_html.find_all('td'):
    if td.text == "Last Value":
        aaa_corporate_bond_yield = td.nextSibling.nextSibling.text
        aaa_corporate_bond_yield = float(aaa_corporate_bond_yield.replace("%", ""))

EBITDA_multiples_url = "https://fullratio.com/ebitda-multiples-by-industry"
EBITDA_multiples_req = urllib.request.Request(url=EBITDA_multiples_url, headers=yield_headers)
EBITDA_multiples_page = urlopen(EBITDA_multiples_req)
EBITDA_multiples_parsed_html = BeautifulSoup(EBITDA_multiples_page, 'html.parser')

modCounter=0
EBITDA_map = {}
industry_name = ""
EBITDA_value = ""
for table in EBITDA_multiples_parsed_html.find_all('table', class_='table table-striped mt-3 mb-3 metric-by-industry'):
    for td in table.find_all('td'):
        if (modCounter % 3 == 0):
            industry_name = td.text
        if (modCounter % 3 == 1):
            EBITDA_value = td.text
            EBITDA_map[industry_name] = EBITDA_value
        modCounter +=1

threads = list()
for i in range (4):
    x = threading.Thread(target=process_stock)
    threads.append(x)
    x.start()

for thread in threads:
    thread.join()
    print(datetime.now().strftime("%H:%M:%S%f") + " Joined thread " + thread.name)


date_str = time.strftime("%m_%d_%Y")
out_file_name = "stock_selector_" + date_str + ".csv"

try:
    f = open(out_file_name, "w", newline='')
    writer = csv.writer(f)
    writer.writerow(['TICKER SYMBOL', 'NAME', 'LIST PRICE', 'INTRINSIC VALUE', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'MARKET CAP', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'EV/EBITDA RATIO', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY', 'RSI', 'INSIDER OWNERSHIP'])
    for currentStock in allStocks:
        writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.list_price, currentStock.intrinsic_value, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.market_cap, currentStock.recommendation_key ,currentStock.EV_EBITDA, currentStock.EV_EBITDA_ratio, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry, currentStock.RSI, currentStock.insider_ownership])
    f.close()
except:
    input("It is likely that you left stock_selector.csv open.  Please close, or rename it and press Enter to continue...")
    f = open(out_file_name, "w", newline='')
    writer = csv.writer(f)
    writer.writerow(['TICKER SYMBOL', 'NAME', 'LIST PRICE', 'INTRINSIC VALUE', 'EPS TTM', 'GROWTH ESTIMATES NEXT 5 YEARS', 'MARGIN OF SAFETY', 'PRICE TO BOOK', 'PRICE TO CASH FLOW', 'ALTMAN Z-SCORE', 'ENTERPRISE VALUE', 'FREE CASH_FLOW', 'TOTAL CASH', 'TOTAL CASH MINUS MARKET CAP', 'TOTAL CASH PER SHARE', 'TOTAL LIABILITIES', 'PRICE/52 WEEK LOW', 'DAY LOW/52 WEEK LOW', 'DAY LOW', '52 WEEK LOW', 'PERCENT SHORT OF FLOAT', 'CASH FLOW PER SHARE', 'SHARES OUTSTANDING', 'CURRENCY', 'COUNTRY', 'MARKET CAP', 'RECOMMENDATION KEY', 'ENTERPRISE VALUE/EBITDA', 'EV/EBITDA RATIO', 'INTRINSIC_VALUE_BY_CASH_FLOW', 'MARGIN_OF_SAFETY_BY_CASH_FLOW', 'SECTOR', 'INDUSTRY', 'RSI', 'INSIDER OWNERSHIP'])
    for currentStock in allStocks:
        writer.writerow([currentStock.ticker_symbol, currentStock.name, currentStock.list_price, currentStock.intrinsic_value, currentStock.EPS_TTM, currentStock.GE_N5Y, currentStock.margin_of_safety, currentStock.price_to_book, currentStock.price_to_cash_flow, currentStock.altman_z_score, currentStock.EV2, currentStock.free_cash_flow_yfinance, currentStock.totalCash, currentStock.total_cash_minus_market_cap, currentStock.total_cash_per_share, currentStock.debt_yfinance, currentStock.current_price_over_fifty_two_week_low, currentStock.day_low_over_fifty_two_week_low, currentStock.day_low, currentStock.fifty_two_week_low, currentStock.short_of_float, currentStock.cash_flow_per_share, currentStock.shares_outstanding, currentStock.currency, currentStock.country, currentStock.market_cap, currentStock.recommendation_key ,currentStock.EV_EBITDA, currentStock.EV_EBITDA_ratio, currentStock.intrinsic_value_cash_flow, currentStock.margin_of_safety_cash_flow, currentStock.sector, currentStock.industry, currentStock.RSI, currentStock.insider_ownership])
    f.close()

try:
    repo = git.Repo('.')
    repo.index.add(repo.untracked_files)
    commit_message = "Adding Stock Selector for day " + date_str
    repo.index.commit(commit_message)
    origin = repo.remote(name='origin')
    origin.push()
except:
    pass

exe_time = time.time() - start_time
print("-------- Analyze Securities program took %s seconds to complete --------" % exe_time)
