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
    high_sigma = 5.0  # Représente une volatilité très élevée
    low_sigma = 0.001 # Représente une volatilité très faible

    # Vérification initiale pour s'assurer que le prix du marché est entre les bornes
    # du modèle avec low_sigma et high_sigma
    try:
        price_at_low = black_scholes_call(S, K, T, r, low_sigma, q)
        price_at_high = black_scholes_call(S, K, T, r, high_sigma, q)

        if market_price < price_at_low or market_price > price_at_high:
            # Le prix du marché est en dehors des bornes atteignables par le modèle
            # avec les volatilités low_sigma et high_sigma.
            # print(f"Warning: Market price {market_price:.2f} is outside Black-Scholes bounds for S={S}, K={K}, T={T}, r={r}, q={q}.")
            # print(f"Price at low_sigma ({low_sigma:.4f}): {price_at_low:.2f}, Price at high_sigma ({high_sigma:.4f}): {price_at_high:.2f}")
            return np.nan # Ne peut pas trouver une IV valide dans les bornes
    except Exception as e:
        # print(f"Error during initial Black-Scholes check in IV solver: {e}")
        return np.nan


    for _ in range(max_iterations):
        mid_sigma = (low_sigma + high_sigma) / 2
        if mid_sigma == 0: # Éviter la division par zéro si mid_sigma devient 0
            break
        
        try:
            # Assurez-vous que black_scholes_call est correctement importé ou défini
            model_price = black_scholes_call(S, K, T, r, mid_sigma, q)
        except Exception as e:
            # print(f"Error calculating model price in IV solver: {e}")
            return np.nan # Gérer les erreurs de calcul du modèle

        diff = model_price - market_price

        if abs(diff) < tol:
            return mid_sigma
        elif diff < 0: # Le prix du modèle est trop bas, augmenter sigma
            low_sigma = mid_sigma
        else: # Le prix du modèle est trop haut, diminuer sigma
            high_sigma = mid_sigma
    
    return np.nan # Non convergent après max_iterations


# --- Main function to fetch option data and calculate IV ---
# SIGNATURE DE LA FONCTION MODIFIÉE ICI
def get_implied_volatility_for_option(ticker, strike, expiry, spot_price, risk_free_rate, dividend_yield, option_type="call", market_price=None):
    """
    Fonction principale pour obtenir la volatilité implicite d'une option.

    Paramètres:
    ticker (str): Symbole du ticker de l'actif sous-jacent.
    strike (float): Prix d'exercice de l'option.
    expiry (str): Date d'expiration de l'option au format 'YYYY-MM-DD'. # NOM DE PARAMÈTRE MODIFIÉ
    spot_price (float): Prix spot actuel de l'actif sous-jacent.
    risk_free_rate (float): Taux d'intérêt sans risque annuel.
    dividend_yield (float): Rendement des dividendes annuel de l'actif sous-jacent.
    option_type (str): 'call' ou 'put'. (Ajouté)
    market_price (float): Le prix de marché de l'option (prix mid). (Ajouté)

    Retourne:
    float: La volatilité implicite calculée, ou np.nan si impossible.
    """
    if option_type.lower() != "call":
        # Pour le moment, notre solveur d'IV est pour les calls via Black-Scholes Call
        # Il faudrait un modèle Black-Scholes Put et un solveur d'IV pour les puts.
        print(f"Warning: Implied volatility calculation is currently supported only for Call options. {option_type} was given for {ticker} {strike} {expiry}.")
        return np.nan

    # Utilisation du market_price passé en paramètre, PAS DE NOUVEL APPEL YFINANCE ICI
    if market_price is None or pd.isna(market_price) or market_price <= 0:
        print(f"Warning: Market price for {ticker} {strike} {expiry} is invalid or missing ({market_price}). Cannot calculate IV.")
        return np.nan

    try:
        # Convertir la date d'expiration en objet datetime et calculer T
        today = datetime.now()
        expiry_dt = datetime.strptime(expiry, "%Y-%m-%d")
        days_to_expiry = (expiry_dt - today).days

        if days_to_expiry <= 0:
            return np.nan # Option expirée ou expirant aujourd'hui

        T = days_to_expiry / 365.0

        # Utilisez le solveur de dichotomie
        implied_vol = find_implied_volatility_bisection(
            market_price=market_price,
            S=spot_price,
            K=strike,
            T=T,
            r=risk_free_rate,
            q=dividend_yield
        )
        return implied_vol
    except Exception as e:
        print(f"Erreur générale lors de la récupération/calcul de l'IV pour {ticker} {strike} {expiry}: {e}")
        return np.nan




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
        ticker_info = yf_ticker.info
        if 'currentPrice' in ticker_info and pd.notna(ticker_info['currentPrice']):
            test_S = float(ticker_info['currentPrice'])
            print(f"Current spot price for {test_ticker} fetched from .info: {test_S:.2f}")
        else:
            print(f"currentPrice not found in .info or is invalid for {test_ticker}. Falling back to .download().")
            
            # --- Fallback vers .download() si .info a échoué ---
            yf_data = yf.download(test_ticker, period="5d", progress=False, actions=False) 
            
            if not yf_data.empty:
                if 'Adj Close' in yf_data.columns:
                    temp_S = yf_data['Adj Close'].iloc[-1]
                elif 'Close' in yf_data.columns:
                    temp_S = yf_data['Close'].iloc[-1]
                else:
                    print(f"Could not find 'Adj Close' or 'Close' column in downloaded data for {test_ticker}.")
                    temp_S = np.nan
                if pd.notna(temp_S):
                    test_S = float(temp_S)
                    print(f"Current spot price for {test_ticker} fetched from .download(): {test_S:.2f}")
                else:
                    print(f"Failed to retrieve a valid numeric spot price for {test_ticker} from .download().")
                    test_S = None
            else:
                print(f"No data downloaded for {test_ticker} for period '5d'.")
                test_S = None

    except Exception as e:
        print(f"Error fetching spot price for {test_ticker}: {repr(e)}. Skipping IV test.")
        test_S = None

    if test_S is not None: # Assurez-vous que test_S est un nombre valide avant de continuer
        test_r = 0.0441
        test_q = 0.00

        # --- CALCUL DU TEMPS JUSQU'À ÉCHÉANCE POUR LE TEST ---
        today_for_test = datetime.now()
        expiry_dt_for_test = datetime.strptime(test_expiry, "%Y-%m-%d")
        days_to_expiry_for_test = (expiry_dt_for_test - today_for_test).days
        T_for_test = days_to_expiry_for_test / 365.0
        
        # --- NOUVEAU : Simuler un market_price réaliste en utilisant Black-Scholes ---
        # On utilise une volatilité estimée pour générer un prix cohérent
        estimated_volatility_for_test = 0.50 # Volatilité de 50% pour le test, une valeur plausible pour NVDA
        
        # S'assurer que T_for_test est > 0 pour black_scholes_call
        if T_for_test <= 0:
            print("Erreur: Le temps jusqu'à l'échéance est nul ou négatif pour le test.")
            test_market_price = np.nan # Rendre le prix invalide
        else:
            test_market_price = black_scholes_call(
                S=test_S, 
                K=test_strike, 
                T=T_for_test, 
                r=test_r, 
                sigma=estimated_volatility_for_test, 
                q=test_q
            )
            print(f"Simulated Black-Scholes price for {test_ticker} Call {test_strike} {test_expiry} with sigma={estimated_volatility_for_test:.2f}: {test_market_price:.2f}")


        # Vérifiez que test_market_price est valide avant de l'utiliser pour l'IV
        if pd.isna(test_market_price) or test_market_price <= 0:
            print(f"Simulated market price for test is invalid ({test_market_price}). Cannot calculate IV.")
            calculated_iv = np.nan # Assurer que l'IV sera NaN si le prix est invalide
        else:
            calculated_iv = get_implied_volatility_for_option(
                ticker=test_ticker,
                strike=test_strike,
                expiry=test_expiry,
                spot_price=test_S,
                risk_free_rate=test_r,
                dividend_yield=test_q,
                option_type="call", 
                market_price=test_market_price 
            )

        if pd.notna(calculated_iv):
            print(f"Volatilité implicite calculée pour {test_ticker} Call {test_strike} {test_expiry}: {calculated_iv:.4f}")
            # Vous pouvez même vérifier si la IV retrouvée est proche de estimated_volatility_for_test
            print(f"La volatilité retrouvée ({calculated_iv:.4f}) devrait être proche de la volatilité d'entrée ({estimated_volatility_for_test:.4f}).")
        else:
            print(f"Échec du calcul de la volatilité implicite pour {test_ticker} Call {test_strike} {test_expiry}. Une valeur par défaut a été utilisée.")
    else:
        print("Skipping IV calculation test due to invalid spot price.")
