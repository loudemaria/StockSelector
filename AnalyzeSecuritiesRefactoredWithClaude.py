"""
Improved Stock Analysis Script with Advanced Rate Limiting
Author: Refactored version with rate limit handling
Date: 2026-02-10

Key features for handling rate limits:
1. Exponential backoff and retry logic
2. Configurable delays between requests
3. Smaller batch sizes with adaptive processing
4. Request throttling and queue management
5. Graceful degradation when rate limited
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
from functools import wraps
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'stock_analysis_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class RateLimiter:
    """Rate limiter to control request frequency"""
    
    def __init__(self, requests_per_minute=30):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0
        self.lock = threading.Lock()
        
    def wait(self):
        """Wait if necessary to respect rate limits"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()


def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Decorator for exponential backoff retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logging.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    
                    # Exponential backoff with jitter
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
            
        return wrapper
    return decorator


class StockAnalyzer:
    """Main class for analyzing stocks with advanced rate limiting"""
    
    def __init__(self, max_workers=4, batch_size=20, requests_per_minute=30):
        """
        Initialize the analyzer with conservative settings
        
        Args:
            max_workers: Number of concurrent threads (reduced from 8 to 4)
            batch_size: Number of tickers per batch (reduced from 100 to 20)
            requests_per_minute: Max requests per minute (default 30)
        """
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.results = []
        self.failed_tickers = []
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.aaa_yield = 5.0  # Default value
        self.ebitda_multiples = {}
        self.processed_count = 0
        self.lock = threading.Lock()
        
        # Try to get AAA yield and EBITDA multiples (with rate limiting)
        try:
            self.aaa_yield = self.get_aaa_bond_yield()
        except:
            logging.warning("Using default AAA yield of 5.0%")
        
        try:
            self.ebitda_multiples = self.get_ebitda_multiples()
        except:
            logging.warning("Could not load EBITDA multiples")
    
    def get_ticker_list(self):
        """Fetch all NASDAQ and other exchange tickers"""
        logging.info("Fetching ticker lists from NASDAQ...")
        
        tickers = []
        
        nasdaq_url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
        other_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
        
        for url in [nasdaq_url, other_url]:
            try:
                self.rate_limiter.wait()
                response = requests.get(url, timeout=15)
                lines = response.text.strip().split('\n')
                
                for line in lines[1:]:
                    parts = line.split('|')
                    if len(parts) > 0 and len(parts[0]) < 6:
                        ticker = parts[0].replace('.', '-')
                        if ticker and ticker not in ['Symbol', '']:
                            tickers.append(ticker)
            except Exception as e:
                logging.error(f"Error fetching tickers from {url}: {e}")
        
        tickers = list(set(tickers))
        logging.info(f"Found {len(tickers)} unique tickers")
        return tickers
    
    @retry_with_backoff(max_retries=3, base_delay=2)
    def get_aaa_bond_yield(self):
        """Get AAA corporate bond yield with retry logic"""
        try:
            url = "https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            self.rate_limiter.wait()
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for td in soup.find_all('td'):
                if td.text == "Last Value":
                    yield_text = td.find_next_sibling('td').text
                    yield_value = float(yield_text.replace('%', ''))
                    logging.info(f"AAA Corporate Bond Yield: {yield_value}%")
                    return yield_value
        except Exception as e:
            logging.warning(f"Could not fetch AAA yield: {e}")
            return 5.0
    
    @retry_with_backoff(max_retries=2, base_delay=2)
    def get_ebitda_multiples(self):
        """Get industry EBITDA multiples with retry logic"""
        try:
            url = "https://fullratio.com/ebitda-multiples-by-industry"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            self.rate_limiter.wait()
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            ebitda_map = {}
            tables = soup.find_all('table', class_='table table-striped mt-3 mb-3 metric-by-industry')
            
            for table in tables:
                tds = table.find_all('td')
                for i in range(0, len(tds), 3):
                    if i + 1 < len(tds):
                        industry = tds[i].text.strip()
                        value = tds[i + 1].text.strip()
                        try:
                            ebitda_map[industry] = float(value)
                        except:
                            pass
            
            logging.info(f"Loaded {len(ebitda_map)} industry EBITDA multiples")
            return ebitda_map
        except Exception as e:
            logging.warning(f"Could not fetch EBITDA multiples: {e}")
            return {}
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_altman_z_score(self, info, financials, balance_sheet):
        """Calculate Altman Z-Score for bankruptcy prediction"""
        try:
            market_cap = info.get('marketCap', 0)
            total_assets = balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else 0
            
            if total_assets == 0 or market_cap == 0:
                return None
            
            current_assets = balance_sheet.loc['Current Assets'].iloc[0] if 'Current Assets' in balance_sheet.index else 0
            current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0] if 'Current Liabilities' in balance_sheet.index else 0
            working_capital = current_assets - current_liabilities
            x1 = working_capital / total_assets
            
            retained_earnings = balance_sheet.loc['Retained Earnings'].iloc[0] if 'Retained Earnings' in balance_sheet.index else 0
            x2 = retained_earnings / total_assets
            
            ebit = financials.loc['EBIT'].iloc[0] if 'EBIT' in financials.index else 0
            x3 = ebit / total_assets
            
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'].iloc[0] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else 0
            x4 = market_cap / total_liabilities if total_liabilities != 0 else 0
            
            revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else 0
            x5 = revenue / total_assets
            
            z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
            
            return round(z_score, 2)
        except Exception as e:
            return None
    
    def calculate_intrinsic_value_graham(self, eps, growth, price):
        """Benjamin Graham's intrinsic value formula"""
        try:
            if self.aaa_yield == 0 or eps is None or growth is None:
                return None, None
            
            intrinsic_value = eps * (8.5 + 2 * growth) * 4.4 / self.aaa_yield
            margin_of_safety = intrinsic_value / price if price > 0 else None
            
            return round(intrinsic_value, 2), round(margin_of_safety, 2) if margin_of_safety else None
        except:
            return None, None
    
    def calculate_dcf_value(self, cash_flow_df, shares_outstanding):
        """Calculate intrinsic value using discounted cash flow"""
        try:
            if cash_flow_df is None or 'Free Cash Flow' not in cash_flow_df.index:
                return None, None
            
            fcf_series = cash_flow_df.loc['Free Cash Flow'].dropna().sort_index()
            
            if len(fcf_series) < 4:
                return None, None
            
            x = np.arange(len(fcf_series))
            y = fcf_series.values
            slope, intercept = np.polyfit(x, y, 1)
            
            last_fcf = fcf_series.iloc[-1]
            growth_rate = slope / last_fcf if last_fcf != 0 else 0
            
            discount_rate = 0.10
            fcf_per_share = last_fcf / shares_outstanding if shares_outstanding > 0 else 0
            
            if growth_rate >= discount_rate:
                return None, None
            
            present_value = fcf_per_share / (discount_rate - growth_rate)
            
            if 'Basic Average Shares' in cash_flow_df.index:
                shares_series = cash_flow_df.loc['Basic Average Shares'].dropna().sort_index()
                if len(shares_series) >= 4:
                    x_shares = np.arange(len(shares_series))
                    y_shares = shares_series.values
                    shares_slope, _ = np.polyfit(x_shares, y_shares, 1)
                    dilution_rate = shares_slope / shares_series.iloc[-1] if shares_series.iloc[-1] != 0 else 0
                    
                    diluted_pv = fcf_per_share / (((1 + discount_rate) * (1 + dilution_rate)) - (1 + growth_rate))
                    return round(present_value, 2), round(diluted_pv, 2)
            
            return round(present_value, 2), None
        except Exception as e:
            return None, None
    
    @retry_with_backoff(max_retries=3, base_delay=2, max_delay=30)
    def analyze_single_stock(self, ticker):
        """Analyze a single stock with retry logic and rate limiting"""
        self.rate_limiter.wait()  # Wait before each request
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if 'currentPrice' not in info and 'previousClose' not in info:
                return None
            
            current_price = info.get('currentPrice') or info.get('previousClose', 0)
            
            # Add delay before getting history
            time.sleep(random.uniform(0.5, 1.5))
            hist = stock.history(period='3mo')
            
            if hist.empty or current_price == 0:
                return None
            
            rsi = self.calculate_rsi(hist['Close'].values) if len(hist) >= 15 else None
            
            # Get financials with additional delay
            time.sleep(random.uniform(0.5, 1.0))
            try:
                financials = stock.financials
                balance_sheet = stock.balance_sheet
                altman_z = self.calculate_altman_z_score(info, financials, balance_sheet)
            except:
                altman_z = None
            
            # Get cash flow with additional delay
            time.sleep(random.uniform(0.5, 1.0))
            try:
                cash_flow = stock.cashflow
                dcf_value, diluted_dcf = self.calculate_dcf_value(cash_flow, info.get('sharesOutstanding', 0))
            except:
                dcf_value, diluted_dcf = None, None
            
            eps = info.get('trailingEps')
            growth_estimate = info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else None
            
            iv_graham, margin_of_safety = self.calculate_intrinsic_value_graham(eps, growth_estimate, current_price)
            
            fcf = info.get('freeCashflow', 0)
            shares = info.get('sharesOutstanding', 0)
            fcf_per_share = fcf / shares if shares > 0 else None
            price_to_fcf = current_price / fcf_per_share if fcf_per_share and fcf_per_share > 0 else None
            
            week_52_low = info.get('fiftyTwoWeekLow', 0)
            price_to_52w_low = current_price / week_52_low if week_52_low > 0 else None
            
            ev_ebitda = info.get('enterpriseToEbitda')
            industry = info.get('industry', '')
            ev_ebitda_ratio = None
            if ev_ebitda and industry in self.ebitda_multiples:
                industry_avg = self.ebitda_multiples[industry]
                ev_ebitda_ratio = ev_ebitda / industry_avg if industry_avg > 0 else None
            
            result = {
                'ticker': ticker,
                'name': info.get('shortName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': industry,
                'country': info.get('country', 'N/A'),
                'currency': info.get('currency', 'N/A'),
                'current_price': round(current_price, 2),
                'day_low': info.get('dayLow'),
                'day_high': info.get('dayHigh'),
                '52_week_low': week_52_low,
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                'price_to_52w_low': round(price_to_52w_low, 2) if price_to_52w_low else None,
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'shares_outstanding': shares,
                'eps_ttm': eps,
                'earnings_growth_5y': growth_estimate,
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'free_cash_flow': fcf,
                'fcf_per_share': round(fcf_per_share, 2) if fcf_per_share else None,
                'price_to_fcf': round(price_to_fcf, 2) if price_to_fcf else None,
                'total_cash': info.get('totalCash'),
                'total_cash_per_share': info.get('totalCashPerShare'),
                'total_debt': info.get('totalDebt'),
                'intrinsic_value_graham': iv_graham,
                'margin_of_safety': margin_of_safety,
                'dcf_present_value': dcf_value,
                'dcf_diluted_value': diluted_dcf,
                'ev_to_ebitda': ev_ebitda,
                'ev_ebitda_ratio': round(ev_ebitda_ratio, 2) if ev_ebitda_ratio else None,
                'altman_z_score': altman_z,
                'rsi_14': rsi,
                'beta': info.get('beta'),
                'short_ratio': info.get('shortRatio'),
                'short_percent_float': info.get('shortPercentOfFloat'),
                'held_percent_insiders': info.get('heldPercentInsiders'),
                'held_percent_institutions': info.get('heldPercentInstitutions'),
                'recommendation': info.get('recommendationKey', 'N/A'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
            }
            
            with self.lock:
                self.processed_count += 1
            
            logging.info(f"✓ [{self.processed_count}] Analyzed {ticker}: ${current_price} | MOS: {margin_of_safety}")
            return result
            
        except Exception as e:
            logging.warning(f"✗ Failed to analyze {ticker}: {str(e)}")
            self.failed_tickers.append(ticker)
            return None
    
    def process_batch(self, tickers):
        """Process a batch of tickers one at a time (no batch download to avoid rate limits)"""
        logging.info(f"Processing batch of {len(tickers)} tickers sequentially...")
        
        results = []
        for ticker in tickers:
            result = self.analyze_single_stock(ticker)
            if result:
                results.append(result)
            
            # Additional delay between tickers in same batch
            time.sleep(random.uniform(1.0, 2.0))
        
        return results
    
    def analyze_all_stocks(self, ticker_list=None):
        """Main method to analyze all stocks with conservative rate limiting"""
        if ticker_list is None:
            ticker_list = self.get_ticker_list()
        
        logging.info(f"Starting analysis of {len(ticker_list)} stocks")
        logging.info(f"Settings: {self.max_workers} workers, batch size {self.batch_size}, "
                    f"{self.rate_limiter.requests_per_minute} req/min")
        start_time = time.time()
        
        batches = [ticker_list[i:i + self.batch_size] 
                   for i in range(0, len(ticker_list), self.batch_size)]
        
        logging.info(f"Created {len(batches)} batches of ~{self.batch_size} tickers each")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_batch = {executor.submit(self.process_batch, batch): i 
                              for i, batch in enumerate(batches)}
            
            for future in as_completed(future_to_batch):
                batch_num = future_to_batch[future]
                try:
                    batch_results = future.result()
                    self.results.extend(batch_results)
                    logging.info(f"✓ Completed batch {batch_num + 1}/{len(batches)} "
                               f"({len(self.results)} stocks analyzed)")
                except Exception as e:
                    logging.error(f"✗ Batch {batch_num} failed: {e}")
        
        elapsed = time.time() - start_time
        logging.info(f"Analysis complete! Processed {len(self.results)} stocks in {elapsed:.1f} seconds")
        logging.info(f"Failed: {len(self.failed_tickers)} tickers")
        logging.info(f"Average time per stock: {elapsed/len(ticker_list):.2f}s")
        
        return self.results
    
    def save_to_csv(self, filename=None):
        """Save results to CSV file"""
        if not self.results:
            logging.warning("No results to save!")
            return
        
        if filename is None:
            filename = f"stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df = pd.DataFrame(self.results)
        
        priority_cols = ['ticker', 'name', 'current_price', 'market_cap', 
                        'intrinsic_value_graham', 'margin_of_safety', 
                        'eps_ttm', 'earnings_growth_5y', 'altman_z_score']
        
        other_cols = [col for col in df.columns if col not in priority_cols]
        df = df[priority_cols + other_cols]
        
        df.to_csv(filename, index=False)
        logging.info(f"Results saved to {filename}")
        return filename


def main():
    """Main execution function"""
    print("=" * 80)
    print("STOCK ANALYSIS TOOL - Rate-Limited Edition")
    print("=" * 80)
    
    # Conservative settings to avoid rate limits
    analyzer = StockAnalyzer(
        max_workers=2,           # Reduced workers
        batch_size=10,           # Smaller batches
        requests_per_minute=20   # Conservative rate limit
    )
    
    # For testing - use a small subset first
    print("\n⚠️  RECOMMENDATION: Test with small sample first!")
    print("Uncomment one of the options below in the code:\n")
    
    # OPTION 1: Test with just 10 stocks (RECOMMENDED FOR TESTING)
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']
    results = analyzer.analyze_all_stocks(ticker_list=test_tickers)
    
    # OPTION 2: Analyze first 100 stocks from full list
    # all_tickers = analyzer.get_ticker_list()
    # results = analyzer.analyze_all_stocks(ticker_list=all_tickers[:100])
    
    # OPTION 3: Analyze ALL stocks (will take several hours)
    # results = analyzer.analyze_all_stocks()
    
    # Save results
    output_file = analyzer.save_to_csv()
    
    # Print summary
    if results:
        df = pd.DataFrame(results)
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Total stocks analyzed: {len(df)}")
        print(f"Failed tickers: {len(analyzer.failed_tickers)}")
        
        if len(df) > 0:
            print(f"\nTop stocks by Margin of Safety:")
            top_mos = df.nlargest(min(10, len(df)), 'margin_of_safety')[
                ['ticker', 'name', 'current_price', 'intrinsic_value_graham', 'margin_of_safety']
            ]
            print(top_mos.to_string(index=False))
        
        print(f"\nOutput saved to: {output_file}")


if __name__ == "__main__":
    main()