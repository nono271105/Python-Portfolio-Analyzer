# portfolio_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime
# from option_pricing import black_scholes_call # Nous n'avons plus besoin de black_scholes_call directement ici
from option_pricing import binomial_tree_american_call
from implied_volatility_calculator import get_implied_volatility_for_option
from market_data_fetcher import calculate_historical_volatility # NOUVEL IMPORT : pour la volatilité historique

# Modifier la signature de la fonction pour inclure live_option_data
def analyze_portfolio(positions, live_prices, risk_free_rate, dividend_yields_by_ticker, live_option_data):
    """
    Analyse les positions du portefeuille, calcule les valeurs de marché et le P&L.

    Paramètres:
    positions (list): Liste des dictionnaires de positions.
    live_prices (dict): Dictionnaire des prix spot actuels.
    risk_free_rate (float): Taux d'intérêt sans risque annuel.
    dividend_yields_by_ticker (dict): Dictionnaire des rendements de dividende annuel par ticker.
    live_option_data (dict): Dictionnaire des données live des options (prix mid, bid, ask). 

    Retourne:
    pd.DataFrame: DataFrame détaillé du portefeuille.
    dict: Résumé global du portefeuille.
    list: Détails de la valorisation des options pour le rapport séparé. 
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
        
        # Logique pour les actions (ajoutée pour compléter, elle manquait)
        if pos["type"] == "stock":
            if pos["purchase_price"] != "XX":
                purchase_value = float(pos["purchase_price"]) * pos["qty"]
            mkt_val = current_spot_price * pos["qty"]
            pnl_val = mkt_val - purchase_value if purchase_value is not None else np.nan
            data.append([
                ticker, pos["type"], pos["qty"], purchase_value, 
                f"S={current_spot_price:.2f}", 
                "-", "-", "-", mkt_val, pnl_val
            ])
        
        elif pos["type"] == "etf":
            if pos["purchase_price"] != "XX":
                purchase_value = float(pos["purchase_price"]) * pos["qty"] # Multiplier par la quantité
            
            # Pour les ETF, le prix spot actuel est la valeur de marché par unité
            mkt_val = current_spot_price * pos["qty"]
            pnl_val = (current_spot_price * pos["qty"]) - purchase_value if purchase_value is not None else np.nan # P&L total
            
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
            historical_volatility = np.nan # Initialisation de la volatilité historique

            if option_live_info: 
                live_option_premium = option_live_info.get("mid")
                if live_option_premium is None: 
                    live_option_premium = option_live_info.get("bid", option_live_info.get("ask"))
                
                # --- Calcul de la Volatilité Historique (HV) ---
                historical_volatility = calculate_historical_volatility(ticker) # Récupération de la HV
                if pd.isna(historical_volatility) or historical_volatility == 0:
                    print(f"Avertissement: Volatilité historique non disponible ou nulle pour {ticker}. Utilisation d'une valeur par défaut de 0.20.")
                    historical_volatility = 0.20 # Valeur par défaut si HV non disponible ou nulle
                
                # --- Calcul de la Volatilité Implicite (IV) ---
                # On ne calcule l'IV que pour les calls car le modèle binomial américain est un call
                if pos["type"] == "call" and pd.notna(live_option_premium) and T > 0 and current_spot_price > 0 and strike > 0 and live_option_premium > 0:
                    try:
                        implied_volatility = get_implied_volatility_for_option(
                            ticker=ticker,
                            strike=strike,
                            expiry=pos["expiry"], 
                            spot_price=current_spot_price,
                            risk_free_rate=risk_free_rate,
                            dividend_yield=ticker_dividend_yield,
                            option_type="call", # Toujours "call" pour l'IV
                            market_price=live_option_premium
                        )
                    except Exception as e:
                        print(f"Erreur lors du calcul de l'IV pour {ticker} {strike} {pos['expiry']}: {e}")
                        implied_volatility = np.nan
                
                # --- Calcul du prix théorique avec le modèle binomial (utilisant la Volatilité Historique) ---
                theoretical_premium = np.nan # Initialisation
                # Nous utilisons la HV ici pour le prix théorique comme convenu
                if pos["type"] == "call" and pd.notna(historical_volatility) and T > 0 and current_spot_price > 0 and strike > 0:
                    try:
                        theoretical_premium = binomial_tree_american_call(
                            S=current_spot_price,
                            K=strike,
                            T=T,
                            r=risk_free_rate,
                            sigma=historical_volatility, # <<< UTILISATION DE LA VOLATILITÉ HISTORIQUE
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
                        over_under_percent = np.nan 

            # Ajouter les détails de valorisation des options
            options_valuation_details.append({
                "ticker": ticker,
                "strike": strike,
                "expiry": pos["expiry"],
                "type": pos["type"],
                "market_price": live_option_premium,
                "theoretical_price": theoretical_premium,
                "implied_volatility": implied_volatility,
                "historical_volatility": historical_volatility, # AJOUT DE LA VOLATILITÉ HISTORIQUE
                "over_under_value": over_under_value,
                "over_under_percent": over_under_percent,
                "risk_free_rate": risk_free_rate, # Ajout pour être complet
                "dividend_yield": ticker_dividend_yield, # Ajout pour être complet
                "time_to_expiry": T # Ajout pour être complet
            })

            # Calcul de la valeur de marché et P&L pour le DataFrame principal
            mkt_val = live_option_premium * pos["qty"] * 100 # Multiplier par 100 car une option contrôle 100 actions
            
            # Purchase value est le prix d'achat d'une option multiplié par 100 (pour 1 contrat)
            purchase_premium_raw = float(pos["purchase_premium"]) if pos["purchase_premium"] != "XX" else np.nan
            purchase_value_contract = purchase_premium_raw * 100 if pd.notna(purchase_premium_raw) else np.nan # Valeur par contrat
            
            pnl_val = (live_option_premium * 100 - purchase_value_contract) * pos["qty"] if pd.notna(purchase_value_contract) else np.nan
            
            # Le "Prix Spot Actuel" affichera toujours le Spot du sous-jacent et le Prix Live de l'option
            data.append([
                ticker, pos["type"], pos["qty"], purchase_value_contract, # Ici on met le prix d'achat du contrat
                f"S={current_spot_price:.2f} P={live_option_premium:.2f}€", 
                strike, expiry.strftime("%Y-%m-%d"), days_to_expiry, mkt_val, pnl_val
            ])

    # Définition des colonnes du DataFrame dans le nouvel ordre et avec les noms
    df = pd.DataFrame(data, columns=[
        "Ticker", "Type", "Quantité", "Prix Achat (€/contrat)", "Prix Spot Actuel", "Strike", "Échéance", "Jours Restants", "Valeur Marché (€)", "P&L (€)"
    ])

    # Résumé du portefeuille
    total_value = df["Valeur Marché (€)"].sum() if not df["Valeur Marché (€)"].empty else 0
    total_pnl = df["P&L (€)"].dropna().sum() if not df["P&L (€)"].dropna().empty else 0

    summary = {
        "Valeur totale portefeuille ": total_value,
        "P&L total portefeuille ": total_pnl,
        "Exposition options ": df[df['Type'].isin(['call', 'put'])]["Valeur Marché (€)"].sum() / total_value * 100 if total_value > 0 else 0,
        "Exposition ETF ": df[df['Type'] == 'etf']["Valeur Marché (€)"].sum() / total_value * 100 if total_value > 0 else 0,
        "Durée moyenne (jours)": df[df['Type'].isin(['call', 'put'])]['Jours Restants'].replace('-', np.nan).dropna().mean() if not df[df['Type'].isin(['call', 'put'])].empty and 'Jours Restants' in df.columns else 0
    }

    # Assurez-vous que les pourcentages sont bien formatés dans le résumé final
    summary["Exposition options "] = f"{summary['Exposition options ']:.2f}%"
    summary["Exposition ETF "] = f"{summary['Exposition ETF ']:.2f}%"

    return df, summary, options_valuation_details
