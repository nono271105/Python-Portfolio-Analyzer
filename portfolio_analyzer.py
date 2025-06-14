# portfolio_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime
from option_pricing import black_scholes_call
from implied_volatility_calculator import get_implied_volatility_for_option

# Modifier la signature de la fonction
def analyze_portfolio(positions, live_prices, risk_free_rate, dividend_yields_by_ticker):
    """
    Analyse les positions du portefeuille, calcule les valeurs de marché et le P&L.

    Paramètres:
    positions (list): Liste des dictionnaires de positions.
    live_prices (dict): Dictionnaire des prix spot actuels.
    risk_free_rate (float): Taux d'intérêt sans risque annuel.
    dividend_yields_by_ticker (dict): Dictionnaire des rendements de dividende annuel par ticker.

    Retourne:
    pd.DataFrame: DataFrame détaillé du portefeuille.
    dict: Résumé global du portefeuille.
    """
    data = []
    today = datetime.today()

    for pos in positions:
        ticker = pos["ticker"]
        current_spot_price = live_prices.get(ticker)
        
        # Récupérer le rendement de dividende spécifique pour ce ticker
        ticker_dividend_yield = dividend_yields_by_ticker.get(ticker, 0.00)

        if current_spot_price is None:
            print(f"Warning: Live price not found in fetched data for {ticker}. Skipping this position.")
            continue

        purchase_value = None
        if pos["type"] == "etf":
            if pos["purchase_price"] != "XX":
                purchase_value = float(pos["purchase_price"])
        else: # type == "call"
            if pos["purchase_premium"] != "XX":
                purchase_value = float(pos["purchase_premium"])

        pnl_val = None

        if pos["type"] == "etf":
            live_price_etf = current_spot_price
            mkt_val = pos["qty"] * live_price_etf
            if purchase_value is not None:
                pnl_val = (live_price_etf - purchase_value) * pos["qty"]
            
            data.append([
                ticker, "ETF", pos["qty"], purchase_value, 
                f"{live_price_etf:.2f}", # Pour ETF, afficher simplement le prix spot formaté
                "-", "-", "-", mkt_val, pnl_val
            ])
        else: # type == "call"
            implied_volatility = None 

            if "volatility_manual" in pos and pd.notna(pos["volatility_manual"]):
                implied_volatility = float(pos["volatility_manual"])
                print(f"IV Calc Info: Using manual volatility ({implied_volatility:.4f}) for {ticker} {pos['strike']} {pos['expiry']}.")
            else:
                implied_volatility = get_implied_volatility_for_option(
                    ticker, 
                    pos["strike"], 
                    pos["expiry"], 
                    current_spot_price, 
                    risk_free_rate, 
                    ticker_dividend_yield 
                )
            
            if pd.isna(implied_volatility) or implied_volatility <= 0:
                print(f"IV Calc Warning: No valid implied volatility found for {ticker} {pos['strike']} {pos['expiry']}. Using default volatility (0.30).")
                implied_volatility = 0.30 
            
            days_to_expiry = (datetime.strptime(pos["expiry"], "%Y-%m-%d") - today).days
            T = days_to_expiry / 365.0 if days_to_expiry > 0 else 0

            try:
                live_option_premium = black_scholes_call(
                    S=current_spot_price,
                    K=pos["strike"],
                    T=T,
                    r=risk_free_rate,
                    sigma=implied_volatility,
                    q=ticker_dividend_yield 
                )
            except Exception as e:
                print(f"Erreur de calcul Black-Scholes pour {ticker}: {e}. Setting premium to 0.")
                live_option_premium = 0

            mkt_val = pos["qty"] * live_option_premium * 100
            if purchase_value is not None:
                pnl_val = (live_option_premium - purchase_value) * pos["qty"] * 100

            data.append([
                ticker, pos["type"], pos["qty"], purchase_value, 
                f"S={current_spot_price:.2f} P={live_option_premium:.2f}€", 
                pos["strike"], pos["expiry"], days_to_expiry, mkt_val, pnl_val
            ])

    # Définition des colonnes du DataFrame dans le nouvel ordre et avec les nouveaux noms
    df = pd.DataFrame(data, columns=[
        "Ticker", "Type", "Quantité", "Prix Achat", "Prix Spot Actuel", "Strike", "Échéance", "Jours Restants", "Valeur Marché (€)", "P&L (€)"
    ])

    # Résumé du portefeuille
    total_value = df["Valeur Marché (€)"].sum()
    total_pnl = df["P&L (€)"].dropna().sum() if not df["P&L (€)"].dropna().empty else None

    summary = {
        "Valeur totale portefeuille ": total_value,
        "P&L total portefeuille ": total_pnl,
        "Exposition options ": df[df['Type'] == 'call']["Valeur Marché (€)"].sum() / total_value * 100 if total_value > 0 else 0,
        "Exposition ETF ": df[df['Type'] == 'ETF']["Valeur Marché (€)"].sum() / total_value * 100 if total_value > 0 else 0,
        "Durée moyenne (jours)": np.average(df[df['Type'] == 'call']["Jours Restants"],
                                             weights=df[df['Type'] == 'call']["Valeur Marché (€)"]) if not df[df['Type'] == 'call'].empty else 0
    }
    
    return df, summary