# market_data_fetcher.py
import yfinance as yf
import pandas as pd
import numpy as np 
from datetime import datetime, timedelta

def fetch_us_10y_treasury_yield():
    """
    Récupère le rendement actuel du bon du Trésor américain à 10 ans.
    Utilise le ticker ^TNX sur Yahoo Finance.
    Retourne le rendement en décimal (ex: 0.045 pour 4.5%).
    """
    ticker_symbol = '^TNX' # Ticker pour le rendement du Trésor US à 10 ans
    try:
        # Récupérer les données sur une courte période pour obtenir le dernier prix de clôture
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5) # Quelques jours d'historique
        
        data = yf.download(ticker_symbol, start=start_date, end=end_date)
        
        if not data.empty:
            latest_yield_value = float(data['Close'].iloc[-1].item()) 
            print(f"Rendement US 10Y récupéré : {latest_yield_value:.4f}%")
            return latest_yield_value / 100 # Convertir en décimal
        else:
            print(f"Avertissement: Aucune donnée trouvée pour {ticker_symbol}.")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération du rendement US 10Y: {e}")
        return None


def fetch_live_data(tickers_list): 
    """
    Récupère les prix spot actuels et les rendements de dividende pour une liste de tickers.

    Paramètres:
    tickers_list (list): Liste des symboles boursiers (tickers) à récupérer.

    Retourne:
    dict: Un dictionnaire où les clés sont les tickers et les valeurs sont un autre dictionnaire
          contenant 'spot_price' et 'dividend_yield'.
          Retourne des données de secours en cas d'échec de la récupération.
    """
    live_data = {}
    print(f"Fetching live data for: {', '.join(tickers_list)} from Yahoo Finance...")

    for ticker in tickers_list:
        try:
            yf_ticker = yf.Ticker(ticker)
            ticker_info = yf_ticker.info

            # --- Récupérer le prix spot ---
            spot_price = None
            if 'currentPrice' in ticker_info and pd.notna(ticker_info['currentPrice']):
                spot_price = float(ticker_info['currentPrice'])
            elif 'regularMarketPrice' in ticker_info and pd.notna(ticker_info['regularMarketPrice']):
                spot_price = float(ticker_info['regularMarketPrice'])
            else:
                data_download = yf.download(ticker, period="5d", progress=False, actions=False)
                if not data_download.empty:
                    # Prioriser 'Adj Close' si disponible, sinon 'Close'
                    if 'Adj Close' in data_download.columns:
                        temp_spot = data_download['Adj Close'].iloc[-1]
                    elif 'Close' in data_download.columns:
                        temp_spot = data_download['Close'].iloc[-1]
                    else:
                        temp_spot = np.nan # Assigner NaN si aucune colonne de prix n'est trouvée

                    if pd.notna(temp_spot):
                        spot_price = float(temp_spot)
                    else:
                        print(f"Warning: Could not find valid spot price in .download() for {ticker}.")
                else:
                    print(f"Warning: No data downloaded for {ticker} for period '5d'.")

            # --- Récupérer le rendement de dividende ---
            
            dividend_yield = ticker_info.get('dividendYield') # Commence par le plus direct
            if dividend_yield is None or pd.isna(dividend_yield):
                dividend_yield = ticker_info.get('trailingAnnualDividendYield') # Fallback pour les dividendes passés

            if dividend_yield is None or pd.isna(dividend_yield):
                dividend_yield = 0.00 # <-- Votre valeur par défaut de 4.00% si aucune info n'est trouvée

            if dividend_yield > 0.1: 
                dividend_yield /= 100.0 

            # Assurez-vous que le prix spot est valide avant d'ajouter à live_data
            if spot_price is not None and pd.notna(spot_price) and spot_price > 0:
                live_data[ticker] = {
                    "spot_price": spot_price,
                    "dividend_yield": dividend_yield
                }
                print(f"  {ticker}: Spot={spot_price:.2f}, Dividend Yield={dividend_yield:.4f}")
            else:
                print(f"Warning: Failed to retrieve a valid positive spot price for {ticker}.")

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            print(f"  Skipping {ticker} due to error. It will use a placeholder/default if available.")

    if not live_data:
        print("Error: No live data was successfully retrieved for any ticker.")
        print("Using placeholder prices and default dividends for calculations.")
        return {
            "LDOS": {"spot_price": 149.16, "dividend_yield": 0.0105},
            "BAH": {"spot_price": 103.30, "dividend_yield": 0.0201},
            "KTOS": {"spot_price": 41.76, "dividend_yield": 0.00},
            "DFEN": {"spot_price": 45.60, "dividend_yield": 0.00} 
        }
    
    print("Live data fetched successfully.")
    return live_data


def fetch_live_option_data(option_positions, spot_prices_by_ticker):
    """
    Récupère les prix live (bid/ask/mid) pour une liste de positions d'options spécifiques.
    Prend en entrée les positions d'options et les prix spot déjà récupérés.

    Paramètres:
    option_positions (list): Liste des dictionnaires de positions d'options
                             (doit contenir 'ticker', 'strike', 'expiry', 'type').
    spot_prices_by_ticker (dict): Dictionnaire des prix spot actuels des sous-jacents.

    Retourne:
    dict: Un dictionnaire où les clés sont un identifiant unique de l'option
          (ex: "LDOS-180-2025-12-19-call") et les valeurs sont un dictionnaire
          contenant 'bid', 'ask', 'lastPrice', 'mid_price'.
    """
    live_option_data = {}
    print("\nFetching live option data from Yahoo Finance...")

    for pos in option_positions:
        ticker = pos["ticker"]
        strike = pos["strike"]
        expiry_date_str = pos["expiry"] # Format 'YYYY-MM-DD'
        option_type = pos["type"] # 'call' ou 'put'

        # Vérifier que nous avons le prix spot du sous-jacent, nécessaire pour la cohérence
        if ticker not in spot_prices_by_ticker:
            print(f"Option Data Error: Spot price for {ticker} not found in fetched underlying data. Skipping option {ticker} {strike} {expiry_date_str}.")
            continue

        try:
            yf_ticker = yf.Ticker(ticker)
            
            # --- Vérifier si la date d'expiration est disponible ---
            available_expiries = yf_ticker.options
            if expiry_date_str not in available_expiries:
                print(f"Option Data Warning: Expiry date {expiry_date_str} not found in available options for {ticker}. Skipping this option.")
                live_option_data[f"{ticker}-{strike}-{expiry_date_str}-{option_type}"] = {
                    "bid": np.nan, "ask": np.nan, "lastPrice": np.nan, "mid_price": np.nan, "found": False
                }
                continue 

            option_chain = yf_ticker.option_chain(expiry_date_str)
            
            # Sélectionner le bon type d'option (calls ou puts)
            if option_type == 'call':
                options_df = option_chain.calls
            elif option_type == 'put':
                options_df = option_chain.puts
            else:
                print(f"Option Data Error: Unknown option type '{option_type}' for {ticker} {strike} {expiry_date_str}. Skipping.")
                continue

            # Trouver l'option spécifique par Strike
            # Assurez-vous que le strike de pos est bien un float ou qu'il est converti
            target_option = options_df.loc[options_df['strike'] == float(strike)]

            if target_option.empty:
                print(f"Option Data Warning: {option_type.capitalize()} option with strike {strike} and expiry {expiry_date_str} not found in YF chain for {ticker}.")
                live_option_data[f"{ticker}-{strike}-{expiry_date_str}-{option_type}"] = {
                    "bid": np.nan, "ask": np.nan, "lastPrice": np.nan, "mid_price": np.nan, "found": False
                }
                continue # Passer à l'option suivante

            
            target_option_row = target_option.iloc[0]

            bid = target_option_row['bid']
            ask = target_option_row['ask']
            last_price = target_option_row['lastPrice']
            
            mid_price = np.nan
            if pd.notna(bid) and pd.notna(ask) and bid > 0 and ask > 0:
                mid_price = (bid + ask) / 2
                print(f"  Found {ticker} {strike} {expiry_date_str} ({option_type}): Bid={bid:.2f}, Ask={ask:.2f}, Mid={mid_price:.2f}")
            elif pd.notna(last_price) and last_price > 0:
                mid_price = last_price
                print(f"  Found {ticker} {strike} {expiry_date_str} ({option_type}): Using Last Price={last_price:.2f}")
            else:
                print(f"  Warning: No valid price (bid/ask/lastPrice > 0) for {ticker} {strike} {expiry_date_str}.")
                mid_price = np.nan 

            # Construire une clé unique pour l'option
            option_key = f"{ticker}-{strike}-{expiry_date_str}-{option_type}"
            live_option_data[option_key] = {
                "bid": bid,
                "ask": ask,
                "lastPrice": last_price,
                "mid_price": mid_price,
                "found": True
            }

        except Exception as e:
            print(f"Error fetching data for option {ticker} {strike} {expiry_date_str}: {e}")
            live_option_data[f"{ticker}-{strike}-{expiry_date_str}-{option_type}"] = {
                "bid": np.nan, "ask": np.nan, "lastPrice": np.nan, "mid_price": np.nan, "found": False
            }

    print("Live option data fetching complete.")
    return live_option_data


# Pour tester ce module indépendamment
if __name__ == "__main__":
    print("--- Test de market_data_fetcher.py ---")
    
    # Test du rendement du Trésor US à 10 ans
    yield_10y = fetch_us_10y_treasury_yield()
    if yield_10y is not None:
        print(f"Rendement du Trésor US à 10 ans actuel: {yield_10y:.4f}")
    else:
        print("Impossible de récupérer le rendement du Trésor US à 10 ans.")

    # Définition des positions pour le test de fetch_live_data et fetch_live_option_data
    # Assurez-vous que les strikes pour les options sont des floats si possible, sinon la conversion float(strike) est importante
    test_portfolio_positions = [
        {"ticker": "LDOS", "type": "call", "qty": 50, "strike": 180.0, "expiry": "2025-12-19"},
        {"ticker": "BAH", "type": "call", "qty": 16, "strike": 120.0, "expiry": "2025-12-19"},
        {"ticker": "KTOS", "type": "call", "qty": 12, "strike": 55.0, "expiry": "2026-01-16"},
        {"ticker": "DFEN", "type": "etf"}, 
        {"ticker": "AAPL", "type": "stock"}, 
    ]

    # Collecter tous les tickers uniques des sous-jacents
    unique_tickers = list(set([p["ticker"] for p in test_portfolio_positions]))

    # Test de fetch_live_data pour les sous-jacents
    live_market_data = fetch_live_data(unique_tickers)
    print("\nDonnées récupérées pour les sous-jacents:")
    for ticker, values in live_market_data.items():
        print(f"  {ticker}: Spot Price={values['spot_price']:.2f}, Dividend Yield={values['dividend_yield']:.4f}")

    # Préparer les données spot pour fetch_live_option_data
    spot_prices_for_options = {ticker: data["spot_price"] for ticker, data in live_market_data.items()}

    # Filtrer uniquement les positions d'options pour fetch_live_option_data
    test_option_positions = [p for p in test_portfolio_positions if p["type"] in ["call", "put"]]

    # Test de fetch_live_option_data
    live_options_data = fetch_live_option_data(test_option_positions, spot_prices_for_options)
    print("\nDonnées récupérées pour les options:")
    for opt_key, values in live_options_data.items():
        status = "Trouvé" if values["found"] else "Non trouvé"
        print(f"  {opt_key}: Mid Price={values['mid_price']:.2f}, Bid={values['bid']:.2f}, Ask={values['ask']:.2f} (Status: {status})")
