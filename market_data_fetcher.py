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
            # Le rendement est généralement dans la colonne 'Close'
            # Convertir explicitement en float pour éviter l'erreur de formatage
            latest_yield_value = float(data['Close'].iloc[-1].item()) # <-- Modification ici
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
                # Fallback robuste au cas où .info ne donne pas de prix actuel
                # Utiliser une période plus longue pour augmenter les chances d'avoir des données
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
            # Yahoo Finance peut utiliser 'dividendYield' ou 'trailingAnnualDividendYield'
            # Les rendements sont souvent en décimales 
            dividend_yield = ticker_info.get('dividendYield') # Commence par le plus direct
            if dividend_yield is None or pd.isna(dividend_yield):
                dividend_yield = ticker_info.get('trailingAnnualDividendYield') # Fallback pour les dividendes passés

            if dividend_yield is None or pd.isna(dividend_yield):
                dividend_yield = 0.00 # Valeur par défaut si aucune information de dividende n'est trouvée

            if dividend_yield > 0.1: # Si c'est 2.13, ou 1.07, etc. (> 10%)
                dividend_yield /= 100.0 # Convertir en décimal (ex: 0.0213)

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
        # Fallback manuel si la récupération ÉCHOUÉ POUR TOUS LES TICKERS.
        # Vous devriez rendre ce fallback plus intelligent si c'est pour la production.
        return {
            "LDOS": {"spot_price": 149.16, "dividend_yield": 0.0105}, # Exemples basés sur vos infos
            "BAH": {"spot_price": 103.30, "dividend_yield": 0.0201},
            "KTOS": {"spot_price": 41.76, "dividend_yield": 0.00},
            "DFEN": {"spot_price": 45.60, "dividend_yield": 0.00} # Les ETF n'ont généralement pas de 'dividendYield' direct ici, donc 0.00 est un bon défaut
        }
    
    print("Live data fetched successfully.")
    return live_data

# Pour tester ce module indépendamment
if __name__ == "__main__":
    test_tickers = ["LDOS", "BAH", "KTOS", "DFEN", "AAPL"] # Ajout de vos tickers spécifiques
    data = fetch_live_data(test_tickers)
    print("\nDonnées récupérées (test market_data_fetcher):")
    for ticker, values in data.items():
        print(f"  {ticker}: Spot Price={values['spot_price']:.2f}, Dividend Yield={values['dividend_yield']:.4f}")

# Pour tester la fonction (peut être ajouté temporairement à la fin du fichier)
if __name__ == '__main__':
    # Test de la fonction pour le taux sans risque
    yield_10y = fetch_us_10y_treasury_yield()
    if yield_10y is not None:
        # La ligne de print ici aussi doit utiliser la valeur directement, pas un objet Series
        print(f"Rendement du Trésor US à 10 ans actuel: {yield_10y:.4f}")
    else:
        print("Impossible de récupérer le rendement du Trésor US à 10 ans.")
