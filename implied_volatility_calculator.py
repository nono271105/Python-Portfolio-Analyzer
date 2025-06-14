# implied_volatility_calculator.py
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from scipy.stats import norm
from option_pricing import black_scholes_call 

# --- Implied Volatility Solver (Bisection Method - Dichotomie) ---
def find_implied_volatility_bisection(market_price, S, K, T, r, q=0, tol=1e-6, max_iterations=200):
    """
    Calcule la volatilité implicite d'une option call européenne en utilisant
    la méthode de la dichotomie (bisection method).

    Paramètres:
    market_price (float): Le prix observé de l'option sur le marché.
    S (float): Prix spot de l'actif sous-jacent.
    K (float): Prix d'exercice de l'option.
    T (float): Temps jusqu'à l'échéance en années.
    r (float): Taux d'intérêt sans risque annuel.
    q (float): Rendement des dividendes annuel.
    tol (float): Tolérance pour la convergence (différence High - Low).
    max_iterations (int): Nombre maximal d'itérations pour éviter les boucles infinies.

    Retourne:
    float: La volatilité implicite calculée, ou np.nan si non convergent ou invalide.
    """
    if T <= 0 or S <= 0 or K <= 0:
        return np.nan # IV non définie pour options expirées ou paramètres invalides

    # Définition des bornes comme dans votre code VBA
    high_sigma = 5.0  # Représente 500%
    low_sigma = 0.001 # Une volatilité de 0 est souvent problématique, donc une petite valeur > 0

    # Vérification initiale si la solution est dans l'intervalle
    price_at_low = black_scholes_call(S, K, T, r, low_sigma, q)
    price_at_high = black_scholes_call(S, K, T, r, high_sigma, q)

    # S'assurer que le prix de marché est entre les bornes
    # Attention: Utilisez une condition OR, car market_price pourrait être entre price_at_high et price_at_low
    # si low_sigma et high_sigma étaient initialement inversés ou si market_price est très faible/élevé
    # Une meilleure approche est de s'assurer que price_at_low < market_price < price_at_high après ajustement des bornes si nécessaire.
    # Pour la dichotomie, il faut que f(low_sigma) et f(high_sigma) aient des signes opposés par rapport à la cible.
    # Ici, nous cherchons price(sigma) = market_price. Donc nous voulons price_at_low < market_price et market_price < price_at_high
    
    # Cas où le prix de marché est plus bas que ce qu'une volatilité minimale donnerait
    # (cela peut arriver pour des options très OTM dont le prix de marché est très bas)
    if market_price < price_at_low:
        # La IV serait inférieure à low_sigma, ou le prix est trop bas pour être solvable.
        return np.nan
    
    # Cas où le prix de marché est plus haut que ce qu'une volatilité maximale donnerait
    # (cela peut arriver pour des options très ITM dont le prix de marché est très haut,
    # ou pour des prix de marché aberrants)
    if market_price > price_at_high:
        # La IV serait supérieure à high_sigma.
        return np.nan

    for i in range(max_iterations):
        mid_sigma = (high_sigma + low_sigma) / 2
        
        # Condition de convergence
        if (high_sigma - low_sigma) < tol:
            return mid_sigma
        
        # Calcul du prix Black-Scholes avec la volatilité moyenne
        bs_price_mid = black_scholes_call(S, K, T, r, mid_sigma, q)
        
        # Ajustement des bornes
        if bs_price_mid > market_price:
            high_sigma = mid_sigma
        else:
            low_sigma = mid_sigma
            
    return (high_sigma + low_sigma) / 2 # Retourne la meilleure approximation après max_iterations


# --- Main function to fetch option data and calculate IV ---
def get_implied_volatility_for_option(ticker, strike, expiry_date_str, current_spot_price, risk_free_rate, dividend_yield):
    """
    Récupère les données d'option de yfinance et calcule la volatilité implicite.

    Paramètres:
    ticker (str): Symbole du sous-jacent (ex: "LDOS").
    strike (float): Prix d'exercice de l'option.
    expiry_date_str (str): Date d'échéance au format "YYYY-MM-DD".
    current_spot_price (float): Prix actuel du sous-jacent.
    risk_free_rate (float): Taux d'intérêt sans risque.
    dividend_yield (float): Rendement des dividendes.

    Retourne:
    float: La volatilité implicite calculée, ou la volatilité par défaut si échec.
    """
    default_volatility = 0.55 # Volatilité par défaut si le calcul échoue ou échoue à trouver un prix de marché valide.

    # 1. Vérifier la validité des inputs
    if current_spot_price <= 0 or strike <= 0:
        print(f"IV Calc Warning: Invalid spot ({current_spot_price:.2f}) or strike ({strike:.2f}) for {ticker}. Using default volatility.")
        return default_volatility

    # 2. Convertir la date d'échéance
    today = datetime.today()
    try:
        expiry_dt = datetime.strptime(expiry_date_str, "%Y-%m-%d")
    except ValueError:
        print(f"IV Calc Warning: Invalid expiry date format for {ticker}: {expiry_date_str}. Using default volatility.")
        return default_volatility

    time_to_expiry_days = (expiry_dt - today).days
    if time_to_expiry_days <= 0:
        print(f"IV Calc Warning: Option for {ticker} is expired or expiring today ({expiry_date_str}). Using default volatility.")
        return default_volatility
    T = time_to_expiry_days / 365.0

    # 3. Récupérer les données de la chaîne d'options
    try:
        yf_ticker = yf.Ticker(ticker)
        # yfinance.option_chain() requiert la date au format 'YYYY-MM-DD'
        option_chain = yf_ticker.option_chain(expiry_date_str)
        calls = option_chain.calls
    except Exception as e:
        print(f"IV Calc Error: Could not fetch option chain for {ticker} (Expiry: {expiry_date_str}). Error: {e}. Using default volatility.")
        return default_volatility

    # 4. Trouver l'option spécifique par Strike
    target_option = calls[calls['strike'] == strike]

    if target_option.empty:
        print(f"IV Calc Warning: Call option with strike {strike} and expiry {expiry_date_str} not found for {ticker}. Using default volatility.")
        return default_volatility
    
    # Préférer la moyenne Bid/Ask, sinon Last Price
    market_price_bid = target_option['bid'].iloc[0]
    market_price_ask = target_option['ask'].iloc[0]
    market_price_last = target_option['lastPrice'].iloc[0]

    market_price = np.nan # Initialiser à NaN

    # Utiliser np.isnan au lieu de pd.notna pour plus de robustesse avec les scalaires numpy
    if not np.isnan(market_price_bid) and not np.isnan(market_price_ask) and market_price_bid > 0 and market_price_ask > 0:
        market_price = (market_price_bid + market_price_ask) / 2
        print(f"IV Calc Info: Using Bid/Ask price ({market_price:.2f}) for {ticker} {strike} {expiry_date_str}.")
    elif not np.isnan(market_price_last) and market_price_last > 0:
        market_price = market_price_last
        print(f"IV Calc Info: Using Last Price ({market_price:.2f}) for {ticker} {strike} {expiry_date_str}.")
    else:
        print(f"IV Calc Warning: No valid market price (bid/ask/lastPrice > 0) found for {ticker} {strike} {expiry_date_str}. Using default volatility.")
        return default_volatility
    
    # 5. Calculer la volatilité implicite avec la méthode de dichotomie
    if np.isnan(market_price) or market_price <= 0: # <-- CORRECTION ICI : Utilisation de np.isnan
        print(f"IV Calc Warning: Invalid market price ({market_price}) for {ticker} {strike} {expiry_date_str}. Using default volatility.")
        return default_volatility

    iv = find_implied_volatility_bisection(market_price, current_spot_price, strike, T, risk_free_rate, dividend_yield)
    
    if np.isnan(iv): # <-- CORRECTION ICI : Utilisation de np.isnan
        print(f"IV Calc Warning: Failed to converge or invalid parameters for IV for {ticker} {strike} {expiry_date_str}. Using default volatility.")
        return default_volatility
    
    print(f"IV Calc Success: Implied Volatility for {ticker} {strike} {expiry_date_str}: {iv:.4f}")
    return iv


# Pour tester ce module indépendamment
if __name__ == "__main__":
    print("--- Test du calculateur de Volatilité Implicite (Méthode Dichotomie) ---")
    
    test_ticker = "NVDA" # Un exemple plus courant pour les options
    test_strike = 130.00
    test_expiry = "2025-07-18" # Une date d'échéance où NVDA a des options actives

    print(f"Fetching spot price for {test_ticker}...")
    test_S = None # Initialiser à None

    try:
        yf_ticker = yf.Ticker(test_ticker)
        
        # --- Tenter de récupérer le prix actuel via .info d'abord ---
        # C'est souvent plus fiable pour un prix unique et actuel, surtout hors heures de marché.
        ticker_info = yf_ticker.info
        if 'currentPrice' in ticker_info and pd.notna(ticker_info['currentPrice']):
            test_S = float(ticker_info['currentPrice'])
            print(f"Current spot price for {test_ticker} fetched from .info: {test_S:.2f}")
        else:
            print(f"currentPrice not found in .info or is invalid for {test_ticker}. Falling back to .download().")
            
            # --- Fallback vers .download() si .info a échoué ---
            # Utiliser period="5d" pour augmenter les chances d'obtenir des données historiques valides
            yf_data = yf.download(test_ticker, period="5d", progress=False, actions=False) 
            
            if not yf_data.empty:
                # Prioriser 'Adj Close', sinon 'Close'
                if 'Adj Close' in yf_data.columns:
                    temp_S = yf_data['Adj Close'].iloc[-1]
                elif 'Close' in yf_data.columns:
                    temp_S = yf_data['Close'].iloc[-1]
                else:
                    print(f"Could not find 'Adj Close' or 'Close' column in downloaded data for {test_ticker}.")
                    temp_S = np.nan # Assigner NaN si aucune colonne trouvée

                if pd.notna(temp_S): # Vérifier si la valeur temporaire n'est pas NaN
                    test_S = float(temp_S) # Convertir explicitement en float
                    print(f"Current spot price for {test_ticker} fetched from .download(): {test_S:.2f}")
                else:
                    print(f"Failed to retrieve a valid numeric spot price for {test_ticker} from .download().")
                    test_S = None # S'assurer que test_S est None si non valide
            else:
                print(f"No data downloaded for {test_ticker} for period '5d'.")
                test_S = None

    except Exception as e:
        # Afficher l'exception de manière plus robuste pour éviter l'erreur "ambiguous truth value"
        # repr(e) donne la représentation 'officielle' de l'objet, qui est toujours une chaîne.
        print(f"Error fetching spot price for {test_ticker}: {repr(e)}. Skipping IV test.")
        test_S = None # Indiquer l'échec

    if test_S is not None: # Assurez-vous que test_S est un nombre valide avant de continuer
        test_r = 0.0441
        test_q = 0.00

        calculated_iv = get_implied_volatility_for_option(
            test_ticker, test_strike, test_expiry, test_S, test_r, test_q
        )
        if pd.notna(calculated_iv):
            print(f"Volatilité implicite calculée pour {test_ticker} Call {test_strike} {test_expiry}: {calculated_iv:.4f}")
        else:
            print(f"Échec du calcul de la volatilité implicite pour {test_ticker} Call {test_strike} {test_expiry}. Une valeur par défaut a été utilisée.")
    else:
        print("Skipping IV calculation test due to invalid spot price.")