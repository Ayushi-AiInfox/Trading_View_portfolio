from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
import jwt
from django.contrib import messages
from django.conf import settings
from accounts.models import * 
import yfinance as yf
import pandas as pd
import json
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import random
from decimal import Decimal


def get_live_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        live_price = stock.fast_info['last_price']
        return live_price
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"



def fetch_historical_stock_prices(tickers, start_date=None, end_date=None):
    if start_date is None:
        start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    prices = {}
    for ticker in tickers:
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            prices[ticker] = stock_data['Close'].to_dict()
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            prices[ticker] = {}
    return prices



def get_time_frames():
    today = datetime.today()
    return {
        '1W': (today - timedelta(days=7), today),
        '1M': (today - timedelta(days=30), today),
        '3M': (today - timedelta(days=90), today),
        'YTD': (datetime(today.year, 1, 1), today),
        '1Y': (today - timedelta(days=365), today),
        'Max': (None, today)
    }


def get_portfolio_value_on_date(portfolio, stock_prices, date):
    total_value = Decimal(0)
    date_as_timestamp = pd.Timestamp(date)

    for holding in portfolio.holdings.all():
        ticker = holding.stock.ticker
        price_data = stock_prices.get(ticker, {})

        # Fetch the price for the exact date
        price_on_date = price_data.get(date_as_timestamp, 0)
        
        total_value += Decimal(price_on_date) * holding.quantity
    
    return total_value


def get_weekly_data(stock_prices, start_date, end_date):
    weekly_data = []
    current_date = start_date

    while current_date <= end_date:
        week_start = current_date - timedelta(days=current_date.weekday())  # Get Monday of the week
        week_end = week_start + timedelta(days=6)  
        week_prices = []

        for ticker, price_data in stock_prices.items():
            week_prices.append(price_data.get(week_start, 0))  # Use 0 if no price available
        
        weekly_data.append(week_prices)
        current_date = week_end + timedelta(days=1)
    
    return weekly_data



def calculate_performance(start_value, end_value):
    if start_value == 0:
        return 0
    return round(((end_value - start_value) / start_value) * 100, 2)


def get_monthly_data(stock_prices, start_date, end_date):
    monthly_data = []
    current_month = start_date.month
    current_year = start_date.year
    while (current_year < end_date.year) or (current_year == end_date.year and current_month <= end_date.month):
        month_start = datetime(current_year, current_month, 1)
        month_end = datetime(current_year, current_month, 1) + pd.DateOffset(months=1) - timedelta(days=1)
        month_prices = []
        for ticker, price_data in stock_prices.items():
            monthly_price = [price for date, price in price_data.items() if month_start <= date <= month_end]
            if monthly_price:
                month_prices.append(sum(monthly_price) / len(monthly_price))  
            else:
                month_prices.append(0)  
        
        monthly_data.append(month_prices)
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
    return monthly_data




def get_portfolio_performance(portfolio, stock_prices):
    time_frames = get_time_frames()  
    performance_data = {}

    for time_frame, (start_date, end_date) in time_frames.items():
        start_value = get_portfolio_value_on_date(portfolio, stock_prices, start_date) if start_date else 0
        end_value = get_portfolio_value_on_date(portfolio, stock_prices, end_date)
        if time_frame == '1W':
            labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            data = get_weekly_data(stock_prices, start_date, end_date)
        elif time_frame == '1M':
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
            data = get_weekly_data(stock_prices, start_date, end_date)
        elif time_frame == '3M':
            
            pass
        

        performance_data[time_frame] = {
            "labels": labels,
            "data": data,
            "performance": {
                "value": f"{calculate_performance(start_value, end_value):+.2f}%",
                "date": end_date.strftime("%b %d, %Y"),
                "positive": end_value > start_value
            }
        }

    return performance_data



def portfolio_performance_view(request):
    portfolio = Portfolio.objects.all()[0]
    stock_tickers = [holding.stock.ticker for holding in portfolio.holdings.all()]
    stock_prices = fetch_historical_stock_prices(stock_tickers)
    performance_data = get_portfolio_performance(portfolio, stock_prices)
    print(performance_data)
    return render(request, 'portfoliopage.html', {'performance_data': performance_data})


def calculate_portfolio_performance(portfolio, stock_prices):
    total_cost = Decimal(0)
    current_market_value = Decimal(0)
    for holding in portfolio.holdings.all():
        ticker = holding.stock.ticker
        current_price = stock_prices.get(ticker, 0)
        cmv = holding.quantity * Decimal(current_price)
        current_market_value += cmv
        total_cost += holding.quantity * holding.average_price
    if total_cost == 0:
        return 0
    performance = ((current_market_value - total_cost) / total_cost) * 100
    return round(performance, 2)

def get_technical_rating(price, sma_50, sma_200):
    if price > sma_50 > sma_200:
        return "Strong Buy"
    elif price > sma_50:
        return "Buy"
    elif price < sma_50:
        return "Sell"
    else:
        return "Hold"

def get_stock_sectors(tickers):
    stock_sectors =[]
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector', 'Unknown')  
            stock_sectors.append(sector)
        except Exception as e:
            stock_sectors[ticker] = f"Error: {str(e)}" 
    return stock_sectors

def get_stock_regions(tickers):
    stock_regions = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            region = info.get('country', 'Unknown')  
            stock_regions.append(region)
        except Exception as e:
            stock_regions[ticker] = f"Error: {str(e)}"  
    return stock_regions

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()

class PivotalStrategy(Strategy):
    def init(self):
        self.pivot_points = []
        self.support_levels = []
        self.resistance_levels = []
    
    def calculate_pivots(self, high, low, close):
        pp = (high + low + close) / 3
        s1 = 2 * pp - high
        r1 = 2 * pp - low
        s2 = pp - (high - low)
        r2 = pp + (high - low)
        return pp, s1, r1, s2, r2

    def next(self):
        if len(self.data.Close) < 2:
            return
        prev_high = self.data.High[-2]
        prev_low = self.data.Low[-2]
        prev_close = self.data.Close[-2]
        pp, s1, r1, s2, r2 = self.calculate_pivots(prev_high, prev_low, prev_close)
        self.pivot_points.append(pp)
        self.support_levels.append(s1)
        self.resistance_levels.append(r1)
        if self.data.Close[-1] > r1 and not self.position:
            self.buy()
        if self.data.Close[-1] < s1 and self.position:
            self.sell()

def symbol_list():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    sp500_data = pd.read_csv(url)
    sp500_symbols = sp500_data['Symbol'].tolist()
    valid_symbols = []
    for symbol in sp500_symbols:
        try:
            yf.Ticker(symbol) 
            valid_symbols.append(symbol)
        except Exception as e:
            print(f"Invalid symbol: {symbol}, Error: {e}")
    return valid_symbols 



KEYS = getattr(settings, "KEY", None)
def AdminDashboardView(request):
    if request.session.has_key('token'):
        message = request.session.get('message')
        message1 = request.session.get('message1')
        try:
            del request.session['message']
        except:
            pass
        try:
            del request.session['message1']
        except:
            pass
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified" or usr.role!='admin':
                return redirect('../../accounts/login')
        except:
            return redirect('../../accounts/login')
        portfolio_data = PortfolioSettings.objects.all()[0]
        ticker = portfolio_data.symbol
        interval_data  = portfolio_data.interval

        if interval_data == '1140':
            interval_data='1d'
        elif interval_data == '7200':
            interval_data = '5d'
        elif interval_data == '10080':
            interval_data = '1w'

        current_datetime = datetime.now()
        val = 4000
        if  interval_data == '5d' :
            val=5000
        date_before_59_days = current_datetime - timedelta(days=val)
        date_format = "%Y-%m-%d"
        previous_date = current_datetime - timedelta(days=1)
        previous_date  = previous_date.strftime(date_format)
        date_before_59_days_formatted = date_before_59_days.strftime(date_format)
        data = yf.download(ticker, start=date_before_59_days, end=previous_date, interval=interval_data)
        data = data.reset_index()
        if 'Date' in data.columns:
            data['time'] = data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        data['Date'] = pd.to_datetime(data['Date'])  
        data.set_index('Date', inplace=True) 
        #data = data.drop(columns=('Adj Close',ticker))
        data.columns = [col[0] for col in data.columns]
        bt = Backtest(data, PivotalStrategy, commission=.000,
              exclusive_orders=True,cash=10000000)
        stats = bt.run() 
        chart_data = data.to_dict(orient="records") 
        chart_data = [{"open":i.get("Open"),"high":i.get("High"),"low":i.get("Low"),"close":i.get("Close"),"volume":i.get("Volume"),"time":i.get("time")} for i in chart_data]
        colors = ["#F44336", "#4CAF50"]
        volume_data = [{"value":i.get("volume"),"time":i.get("time"),"color":random.choice(colors)} for i in chart_data]
        d= dict(stats)      
        trades_data = d.get('_trades')
        trades_data = trades_data.to_dict(orient="records")
        data_dict = {}  
        data_dict['Return'] = d['Return [%]']
        data_dict['total_trades'] = d["# Trades"]
        data_dict['best_trades']= d['Best Trade [%]']
        data_dict['buy_hold_return']=d["Buy & Hold Return [%]"]
        data_dict['Max_dropdown'] = d['Max. Drawdown [%]']
        data_dict['win_rate'] = d["Win Rate [%]"]
        data_dict['max_dropdown_duration'] = d['Max. Drawdown Duration']
        data_dict['average_dropdown_duration']=d["Avg. Drawdown Duration"]
        data_dict['worst_trades'] = d["Worst Trade [%]"]
        data_dict['profit_factor'] = d["Profit Factor"]
        symbols = symbol_list()
        t_data = []
        pivotal_data=[]
        for i in trades_data:
            f={"time":(i.get("EntryTime") + timedelta(days=1)).strftime(date_format),"position":"belowBar","color":"#4285F4","shape":"arrowUp","text":"L"}
            s = {"time":i.get("ExitTime").strftime(date_format),"position":"aboveBar","color":"#FF4444","shape":"arrowDown","text":"S"}
            p = {"time":i.get("EntryTime").strftime(date_format),"price":i.get("EntryPrice")}
            t_data.append(f)
            t_data.append(s) 
            pivotal_data.append(p)    
        pivotal_data=pivotal_data[-5:]
    

        
        # for i in symbols:
        #     try:
        #         Stock.objects.create(ticker=i,name=i)
        #     except:
        #         pass 
        return render(
        request,'admin_dashboard.html',
        {
        'message':message,'message1':message1,
        "user":usr,"trades_data":trades_data,
        "data_dict":data_dict,
        "symbols":symbols,
        'portfolio':portfolio_data,
        "interval_data":interval_data,
        "chart_data":chart_data,
        "trades_data":t_data,
        "volume_data":volume_data,
        "pivotal_data":pivotal_data
        })


    else:
        return redirect('../../accounts/login')

def SaveSymbol(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        symbol_name = data.get('symbol')
        
        if symbol_name:
            symbol = PortfolioSettings.objects.all()[0]
            symbol.symbol = symbol_name
            symbol.save()
            return JsonResponse({"success":True,"message":"Symbol Saved successfully"})
        return JsonResponse({'success': False, 'message': 'Invalid symbol name'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def save_multi_screen(request):
    if request.method=='POST':
        data = json.loads(request.body)
        symbol_name = data.get('symbol')
        if symbol_name:
            symbol = MultiScreen.objects.all()[0]
            symbol.symbol= symbol_name
            symbol.save()
            return JsonResponse({"success":True,"message":"Symbol Saved successfully"})
        return JsonResponse({'success': False, 'message': 'Invalid symbol name'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})    



def screen2(request):
    if request.session.has_key('token'):
        message = request.session.get('message')
        message1 = request.session.get('message1')
        try:
            del request.session['message']
        except:
            pass
        try:
            del request.session['message1']
        except:
            pass
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified" or usr.role!='admin':
                return redirect('../../accounts/login')
        except:
            return redirect('../../accounts/login')

        portfolio_data = PortfolioSettings.objects.all()[0]
        ticker = portfolio_data.symbol
        interval_data  = portfolio_data.interval
        if interval_data == '1140':
            interval_data='1d'
        elif interval_data == '7200':
            interval_data = '5d'
        elif interval_data == '10080':
            interval_data = '1w'
        current_datetime = datetime.now()
        val = 4000
        if  interval_data == '5d' :
            val=5000
        date_before_59_days = current_datetime - timedelta(days=val)
        date_format = "%Y-%m-%d"
        previous_date = current_datetime - timedelta(days=1)
        previous_date  = previous_date.strftime(date_format)
        date_before_59_days_formatted = date_before_59_days.strftime(date_format)
        data = yf.download(ticker, start=date_before_59_days, end=previous_date, interval=interval_data)
        data = data.reset_index()
        if 'Date' in data.columns:
            data['time'] = data['Date'].dt.strftime('%Y-%m-%d')
        data['Date'] = pd.to_datetime(data['Date'])  
        data.set_index('Date', inplace=True) 
        data = data.drop(columns=('Adj Close',ticker))
        data.columns = [col[0] for col in data.columns]
        data = data.to_dict(orient="records")
        data = [{"time":i.get("time"),"value":i.get("Close")} for i in data]
        return render(request,'screen2.html',{"data":data})
    else:
        return redirect('../../accounts/login')





def screen3(request):
    if request.session.has_key('token'):
        message = request.session.get('message')
        message1 = request.session.get('message1')
        try:
            del request.session['message']
        except:
            pass
        try:
            del request.session['message1']
        except:
            pass
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified" or usr.role!='admin':
                return redirect('../../accounts/login')
        except:
            return redirect('../../accounts/login')
        portfolio_data = MultiScreen.objects.all()[0]
        ticker = portfolio_data.symbol
        all_symbols=symbol_list()
        all_symbols = all_symbols[:10]
        current_datetime = datetime.now()
        date_before_59_days = current_datetime - timedelta(days=4000)
        previous_date = current_datetime - timedelta(days=1)
        data = yf.download(ticker, start=date_before_59_days, end=previous_date, interval="1d")
        data = data.reset_index()
        if 'Date' in data.columns:
            data['time'] = data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        data['Date'] = pd.to_datetime(data['Date'])  
        data.set_index('Date', inplace=True) 
        data.columns = [col[0] for col in data.columns]


        chart_data = data.to_dict(orient="records") 
        chart_data = [{"open":i.get("Open"),"high":i.get("High"),"low":i.get("Low"),"close":i.get("Close"),"volume":i.get("Volume"),"time":i.get("time")} for i in chart_data]

        final_data = []
        for symbol in all_symbols:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            price = hist["Close"].iloc[-1]
            sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]
            sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1]
            info = stock.info
            prev_close = info.get("regularMarketPreviousClose")
            volume = info.get("volume")
            market_cap = info.get("marketCap")
            sector = info.get("sector")
            if prev_close:
                price_change = price - prev_close
                percent_change = (price_change / prev_close) * 100
            else:
                price_change = "N/A"
                percent_change = "N/A"
            vol_price = volume * price if volume and price else "N/A"
            technical_rating = get_technical_rating(price, sma_50, sma_200)

            data = {"symbol":symbol,"price":price,"price_change":price_change,"percent_change":percent_change,"volume":volume,"vol_price":vol_price,"market_cap":market_cap,"technical_rating":technical_rating,"sector":sector}
            final_data.append(data)  
        #print(final_data)  
        return render(request,'screen3.html',{"final_data":final_data,"chart_data":chart_data})
    else:
        return redirect('../../accounts/login')



def saveInterval(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        interval_data = data.get('interval')
        print(interval_data)
        if interval_data == '1d':
            interval_data = '1140'
        elif interval_data == '5d':
            interval_data = '7200'
        # elif interval_data == '1w':
        #     interval_data = '10080'
        # elif interval_data == '5m':
        #     interval_data = '5'
        # elif interval_data == '10m':
        #     interval_data ='10'
        # elif interval_data == '15m':
        #     interval_data = '15'
        # elif interval_data == '30m':
        #     interval_data = '30'
        # elif interval_data == '1h':
        #     interval_data = '60'
        # elif interval_data == '2h':
        #     interval_data = '120'
        # elif interval_data == '4h':
        #     interval_data = '240'
        # elif interval_data == '1d':
        #     interval_data = '1140'

        if interval_data:
            interval = PortfolioSettings.objects.all()[0]
            interval.interval = interval_data
            interval.save()
            return JsonResponse({"success":True,"message":"Symbol Saved successfully"})
        return JsonResponse({'success': False, 'message': 'Invalid interval name'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})





def portfolio(request):
    if request.session.has_key('token'):
        message = request.session.get('message')
        message1 = request.session.get('message1')
        try:
            del request.session['message']
        except:
            pass
        try:
            del request.session['message1']
        except:
            pass
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified" or usr.role!='admin':
                return redirect('../../accounts/login')
        except:
            return redirect('../../accounts/login')
        portfolios = User.objects.filter(email = d.get("email"))

        data = Holding.objects.all()
        gross_active_investment= 0
        stocks = 0 
        portfolio_value = 0
        for i in data:
            val=get_live_price(i.stock.ticker)
            gross_active_investment += float(i.quantity)*float(val)
            stocks += float(i.quantity)
            portfolio_value += float(i.quantity)*float(val)
        trans = Transaction.objects.all()
        buyed = 0
        selled = 0
        for i in trans:
            if i.transaction_type.lower() == "buy":
                buyed+=float(i.quantity)*float(i.price)
            elif i.transaction_type.lower() == "sell":
                selled += float(i.quantity) * float(i.price)
        overall = selled-buyed
        portfolio_value+=overall
        profit_percentage  = (overall/buyed)*100
        share_wise_investment = {"data":[i.quantity for i in data],"labels":[i.stock.ticker for i in data]}
        
        sector_wise = get_stock_sectors(share_wise_investment.get('labels'))
        sector_wise = {"data":share_wise_investment.get('data'),"labels":sector_wise}
        region_wise = get_stock_regions(share_wise_investment.get('labels'))
        region_wise = {"data":share_wise_investment.get('data'),"labels":region_wise}

        return render(request, 'portfolio.html', 
        {'gross_active_investment': gross_active_investment,
        "stocks":stocks,"portfolio_value":portfolio_value,
        "profit_percentage":profit_percentage,"expenses":buyed,
        "share_wise_investment":share_wise_investment,"sector_wise_investment":sector_wise,"region_wise":region_wise
        })

    else:
        return redirect('../../accounts/login')





def profile(request):
    if request.session.has_key('token'):
        message = request.session.get('message')
        message1 = request.session.get('message1')
        try:
            del request.session['message']
        except:
            pass
        try:
            del request.session['message1']
        except:
            pass
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified" or usr.role!='admin':
                return redirect('../../accounts/login')
        except:
            return redirect('../../accounts/login')
        return render(request,'profile.html')
    else:
        return redirect('../../accounts/login')
        
        


    
  

