from flask import Flask, render_template 
import requests
import pandas as pd
import humanize
import yfinance as yf

app = Flask(__name__) # Create the app 
app.config['TEMPLATES_AUTO_RELOAD'] = True # This will make sure we don't need to restart the server each time we change something to the layout of the webpage

crypto_data = None # We will reuse this object everytime we render the homepage.
# You can also decide not to reuse it, but we'll have to think about API request limitation 
# and on top of that, having it cached will make it render faster

@app.route("/") # Tell the server to use this function when '/' is the url
def main():
    global crypto_data
    pd.set_option('expand_frame_repr', False)
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"}
    res=requests.get("https://api.nasdaq.com/api/quote/list-type/nasdaq100",headers=headers)
    main_data=res.json()['data']['data']['rows']

    results=[]

    for i in range(len(main_data)):
    
        ticker_symbol = main_data[i]['symbol']
        yf_ticker = yf.Ticker(ticker_symbol)
        ticker_info = yf_ticker.info
        details = {
        "name": ticker_info["longName"],
        "symbol": ticker_info["symbol"],
        "industry": ticker_info["industry"],
        "logo_url": ticker_info["logo_url"],
        #"web_url": ticker_info["website"],
        #"description": ticker_info["longBusinessSummary"],
        "market_cap": humanize.intword(ticker_info["marketCap"]),
        "open_price": humanize.intcomma(ticker_info["open"]),
    }

        results.append(details)

    if crypto_data is None: # If crypto_data is not yet defined, make the API request
        crypto_data = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?sort=market_cap&start=1&cryptocurrency_type=tokens&convert=BTC', headers={'X-CMC_PRO_API_KEY': 'f785d857-d08e-4819-8c00-0d4b24f7bec6'}) # Replace YOUR_API_KEY with the key in your account
        crypto_data = crypto_data.json() # Transform the received data into JSON so we can use it
    return render_template('index.html', crypto_data=crypto_data, results=results) # Render the html


@app.route("/information/<string:crypto>") # crypto will be the name of the variable
def crypto(crypto): # Add the name of the variable so we can use it
    json = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=' + crypto + '&convert=BTC', headers={'X-CMC_PRO_API_KEY': 'f785d857-d08e-4819-8c00-0d4b24f7bec6'})
    json = json.json()
    return render_template('information.html', data=json, crypto=crypto) # Pass two variables to the template: data (which is retrieved from the API) and crypto (Which is the symbol from the url)

# Run the app
if __name__ == "__main__":
    app.run(port=5000) # Run the app on port 5000 (localhost:5000)