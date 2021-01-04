from django.shortcuts import render
from multiprocessing import Process
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
import praw
import enchant
import yfinance as yf

#Global Variables
reddit = praw.Reddit(client_id = 'LXGTI71Cz1Nsjw',
                     client_secret = 'gv-iTYdVH0r7ln3rQsdSslNuZzQl_Q',
                     user_agent = 'StockUp',
                     username = 'aveni121',
                     password = 'Lumenta313!')

subred = reddit.subreddit('pennystocks')
new_posts = subred.new(limit = 50)
is_word = enchant.Dict('en_US')

ticker_objects = []

class Ticker:
    def __init__(self, symbol, name, desc, table, vol_change, gain):
        self.symbol = symbol
        self.name = name
        self.desc = desc
        self.table = table
        self.vol_change = vol_change
        self.gain = gain

def is_ticker(word):
    if len(word) < 6 and len(word) > 2 and word.isupper():
        if is_word.check(word):
            return False
        else:
            return True

def format_ticker(word):
    for char in word:
        if not char.isalpha():
            word = word.replace(char, "")
    return word
        
def scan_for_tickers(tickers_found):
    for post in new_posts:
        print(f'Scanning: "{post.title}"')  
        comments = post.comments
        for comment in comments:
            content = comment.body.split(" ")
            for word in content:
                if is_ticker(word):
                    word = format_ticker(word)
                    if word not in tickers_found:
                        print(f'Possible Stock Found: {word}')
                        tickers_found.append(word)
    return tickers_found

# Create your views here.
def index(requests):
    if requests.method == 'POST':
        return HttpResponseRedirect(reverse('scanner:loading'))
    return render(requests, "scanner/index.html")

def loading(requests):
    if requests.method == 'POST':
        tickers_found = []
        tickers_found = scan_for_tickers(tickers_found)
        global ticker_objects
        for ticker in tickers_found:
            try:
                print(f"Retrieving Data: '{ticker}'")
                stock = yf.Ticker(ticker)
                stock_info = stock.info
                hist = stock.history(period="15d")
                hist['Average'] = (hist['Open'] + hist['Close'])/2
                hist['Gain(Daily)'] = round((((hist['Close']/hist['Open'])-1) * 100), 2)
                biweekly_gain = round(hist['Gain(Daily)'].sum(),2)
                biweekly_avg_vol = hist['Volume'].iloc[0:-2].mean()
                biweekly_vol_change = round(((hist['Volume'].iloc[-1]/biweekly_avg_vol)-1) * 100, 2)
                table = hist[['Open', 'High', 'Close','Average', 'Gain(Daily)', 'Volume']]
                ticker_objects.append(Ticker(ticker, stock_info['shortName'], stock_info['longBusinessSummary'], table.to_html(), biweekly_vol_change, biweekly_gain))
            except:
                pass
        return render(requests, 'scanner/results.html', {
                'tickers': ticker_objects
        })

    else:
        return render(requests, "scanner/loading.html")

def process():
    pass
    
def results(requests):
    pass
