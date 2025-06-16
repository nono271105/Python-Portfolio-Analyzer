# portfolio_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime
# from option_pricing import black_scholes_call # Nous n'avons plus besoin de black_scholes_call directement ici
from option_pricing import binomial_tree_american_call
from implied_volatility_calculator import get_implied_volatility_for_option

# Modifier la signature de la fonction pour inclure live_option_data
def analyze_portfolio(positions, live_prices, risk_free_rate, dividend_yields_by_ticker, live_option_data):
    """
    Analyse les positions du portefeuille, calcule les valeurs de marché et le P&L.

    Paramètres:
    positions (list): Liste des dictionnaires de positions.
    live_prices (dict): Dictionnaire des prix spot actuels.
    risk_free_rate (float): Taux d'intérêt sans risque annuel.
    dividend_yields_by_ticker (dict): Dictionnaire des rendements de dividende annuel par ticker.
    live_option_data (dict): Dictionnaire des données live des options (prix mid, bid, ask). # NOUVEAU

    Retourne:
    pd.DataFrame: DataFrame détaillé du portefeuille.
    dict: Résumé global du portefeuille.
    list: Détails de la valorisation des options pour le rapport séparé. # NOUVEAU
    """
    data = []
    today = datetime.today()
    options_valuation_details = [] 

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
            
            # Pour les ETF, le prix spot actuel est la valeur de marché par unité
            mkt_val = current_spot_price * pos["qty"]
            pnl_val = (current_spot_price - purchase_value) * pos["qty"] if purchase_value is not None else np.nan
            
            data.append([
                ticker, pos["type"], pos["qty"], purchase_value, 
                f"S={current_spot_price:.2f}", # Seulement le prix spot pour les ETF
                "-", "-", "-", mkt_val, pnl_val
            ])

        elif pos["type"] in ["call", "put"]:
            strike = float(pos["strike"])
            expiry = datetime.strptime(pos["expiry"], "%Y-%m-%d")
            days_to_expiry = (expiry - today).days
            T = days_to_expiry / 365.0

            # Clé pour récupérer les données live de l'option
            option_key = f"{ticker}-{strike}-{pos['expiry']}-{pos['type']}"
            option_live_info = live_option_data.get(option_key)

            live_option_premium = np.nan
            implied_volatility = np.nan
            theoretical_premium = np.nan
            over_under_value = np.nan
            over_under_percent = np.nan

            if option_live_info: # MODIFICATION ICI : Supprimé `and option_live_info["status"] == "Trouvé"`
                live_option_premium = option_live_info.get("mid")
                if live_option_premium is None: # Fallback au bid si mid n'est pas dispo, ou ask si bid n'est pas dispo
                    live_option_premium = option_live_info.get("bid", option_live_info.get("ask"))
                
                # --- Calcul de la Volatilité Implicite (IV) ---
                # On ne calcule l'IV que pour les calls car le modèle binomial américain est un call
                # Si le modèle binomial était flexible (call/put), on pourrait aussi faire l'IV pour les puts
                if pos["type"] == "call" and pd.notna(live_option_premium) and T > 0 and current_spot_price > 0 and strike > 0 and live_option_premium > 0:
                    try:
                        implied_volatility = get_implied_volatility_for_option(
                            ticker=ticker,
                            strike=strike,
                            expiry=pos["expiry"], # Passer la date string pour la fonction
                            spot_price=current_spot_price,
                            risk_free_rate=risk_free_rate,
                            dividend_yield=ticker_dividend_yield,
                            option_type="call", # Toujours "call" pour l'IV
                            market_price=live_option_premium
                        )
                    except Exception as e:
                        print(f"Erreur lors du calcul de l'IV pour {ticker} {strike} {pos['expiry']}: {e}")
                        implied_volatility = np.nan

                # --- Calcul du prix théorique avec le modèle binomial ---
                theoretical_premium = np.nan # Initialisation
                if pos["type"] == "call" and pd.notna(implied_volatility) and T > 0 and current_spot_price > 0 and strike > 0:
                    try:
                        # Utilisation de la nouvelle fonction binomial_tree_american_call
                        # N=500 est un nombre de pas raisonnable pour la précision vs performance
                        theoretical_premium = binomial_tree_american_call(
                            S=current_spot_price,
                            K=strike,
                            T=T,
                            r=risk_free_rate,
                            sigma=implied_volatility,
                            q=ticker_dividend_yield,
                            N=500 # Nombre de pas pour l'arbre binomial
                        )
                    except Exception as e:
                        print(f"Erreur lors du calcul du prix théorique binomial pour {ticker} {strike} {pos['expiry']}: {e}")
                        theoretical_premium = np.nan
                
                # --- Calcul de la sur/sous-évaluation ---
                if pd.notna(live_option_premium) and pd.notna(theoretical_premium):
                    over_under_value = live_option_premium - theoretical_premium
                    if theoretical_premium != 0:
                        over_under_percent = (over_under_value / theoretical_premium) * 100
                    else:
                        over_under_percent = np.nan # Éviter la division par zéro

            # Ajouter les détails de valorisation des options
            options_valuation_details.append({
                "ticker": ticker,
                "strike": strike,
                "expiry": pos["expiry"],
                "type": pos["type"],
                "market_price": live_option_premium,
                "theoretical_price": theoretical_premium,
                "implied_volatility": implied_volatility,
                "over_under_value": over_under_value,
                "over_under_percent": over_under_percent
            })

            # Calcul de la valeur de marché et P&L pour le DataFrame principal
            mkt_val = live_option_premium * pos["qty"] * 100 # Multiplier par 100 car une option contrôle 100 actions
            
            # Purchase value est le prix d'achat d'une option multiplié par 100 (pour 1 contrat)
            purchase_value = float(pos["purchase_premium"]) if pos["purchase_premium"] != "XX" else np.nan
            purchase_value_contract = purchase_value * 100 if pd.notna(purchase_value) else np.nan # Valeur par contrat
            
            pnl_val = (live_option_premium * 100 - purchase_value_contract) * pos["qty"] if pd.notna(purchase_value_contract) else np.nan
            
            # Le "Prix Spot Actuel" affichera toujours le Spot du sous-jacent et le Prix Live de l'option
            data.append([
                ticker, pos["type"], pos["qty"], purchase_value, 
                f"S={current_spot_price:.2f} P={live_option_premium:.2f}€", 
                strike, expiry, days_to_expiry, mkt_val, pnl_val
            ])

    # Définition des colonnes du DataFrame dans le nouvel ordre et avec les nouveaux noms
    df = pd.DataFrame(data, columns=[
        "Ticker", "Type", "Quantité", "Prix Achat", "Prix Spot Actuel", "Strike", "Échéance", "Jours Restants", "Valeur Marché (€)", "P&L (€)"
    ])

    # Résumé du portefeuille
    total_value = df["Valeur Marché (€)"].sum() if not df["Valeur Marché (€)"].empty else 0
    total_pnl = df["P&L (€)"].dropna().sum() if not df["P&L (€)"].dropna().empty else 0

    summary = {
        "Valeur totale portefeuille ": total_value,
        "P&L total portefeuille ": total_pnl,
        "Exposition options ": df[df['Type'].isin(['call', 'put'])]["Valeur Marché (€)"].sum() / total_value * 100 if total_value > 0 else 0,
        "Exposition ETF ": df[df['Type'] == 'etf']["Valeur Marché (€)"].sum() / total_value * 100 if total_value > 0 else 0,
        "Durée moyenne (jours)": df[df['Type'].isin(['call', 'put'])]['Jours Restants'].replace('-', np.nan).dropna().mean() if not df[df['Type'].isin(['call', 'put'])]['Jours Restants'].replace('-', np.nan).dropna().empty else 0
    }

    return df, summary, options_valuation_details

