# main_portfolio.py
import pandas as pd 
from market_data_fetcher import fetch_live_data 
from portfolio_analyzer import analyze_portfolio
from portfolio_reporter import display_portfolio_report

# --- Définition des positions ---
# purchase_premium est le prix d'achat de l'option et purchase_price est le prix d'achat de l'ETF
positions = [
    {"ticker": "LDOS", "type": "call", "qty": 50, "strike": 180, "expiry": "2025-12-19", "purchase_premium": "3"},
    {"ticker": "BAH", "type": "call", "qty": 16, "strike": 120, "expiry": "2025-12-19", "purchase_premium": "5.15"},
    {"ticker": "KTOS", "type": "call", "qty": 12, "strike": 55, "expiry": "2026-01-16", "purchase_premium": "3.20"},
    {"ticker": "DFEN", "type": "etf", "qty": 1800, "purchase_price": "46.28"}
]

# --- Paramètres globaux pour Black-Scholes ---
risk_free_rate = 0.0441  # (T-10Y US Treasury Yield)

# 1. Obtenir la liste unique des tickers à récupérer
tickers_to_fetch = list(set([p["ticker"] for p in positions]))

# 2. Récupérer les données live (prix spot et dividendes) en utilisant le module market_data_fetcher
live_market_data = fetch_live_data(tickers_to_fetch) 

# Vérifier si les données ont été récupérées avec succès
if not live_market_data:
    print("Erreur: Impossible de récupérer les données de marché. Arrêt de l'analyse.")
    exit()

# 3. Préparer les dictionnaires pour analyze_portfolio
# live_prices_only contiendra {ticker: spot_price}
# dividend_yields_by_ticker contiendra {ticker: dividend_yield}
live_prices_only = {ticker: data["spot_price"] for ticker, data in live_market_data.items()}
dividend_yields_by_ticker = {ticker: data["dividend_yield"] for ticker, data in live_market_data.items()}

# 4. Analyser le portefeuille en utilisant le module portfolio_analyzer
# Passer les prix spot seuls ET les dividendes par ticker
df_portfolio, portfolio_summary = analyze_portfolio(
    positions,
    live_prices_only,           # <-- Dictionnaire des prix spot
    risk_free_rate,
    dividend_yields_by_ticker   # <-- Dictionnaire des dividendes par ticker
)

# Optionnel : trier le DataFrame avant de l'afficher
df_portfolio_sorted = df_portfolio.sort_values(by="Valeur Marché (€)", ascending=False)

# 5. Afficher le rapport du portefeuille en utilisant le module portfolio_reporter
display_portfolio_report(df_portfolio_sorted, portfolio_summary)