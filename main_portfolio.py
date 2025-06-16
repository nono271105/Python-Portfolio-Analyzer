# main_portfolio.py
import io
import sys
import pandas as pd
from datetime import datetime
import os


from market_data_fetcher import fetch_live_data, fetch_us_10y_treasury_yield, fetch_live_option_data # Ajout de fetch_live_option_data
from portfolio_analyzer import analyze_portfolio
from portfolio_reporter import get_portfolio_report_html 
from email_reporter import send_email

# --- Fonctions pour capturer/restaurer l'output ---
def capture_output(func, *args, **kwargs):
    """
    Capture la sortie console d'une fonction et la retourne sous forme de chaîne.
    """
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    try:
        func(*args, **kwargs)
        return redirected_output.getvalue()
    finally:
        sys.stdout = old_stdout

# --- Définition des positions ---
positions = [
    {"ticker": "LDOS", "type": "call", "qty": 50, "strike": 180.0, "expiry": "2025-12-19", "purchase_premium": "4.4"},
    {"ticker": "BAH", "type": "call", "qty": 16, "strike": 120.0, "expiry": "2025-12-19", "purchase_premium": "5.4"},
    {"ticker": "KTOS", "type": "call", "qty": 12, "strike": 55.0, "expiry": "2026-01-16", "purchase_premium": "3.60"},
    {"ticker": "DFEN", "type": "etf", "qty": 1800, "purchase_price": "45.00"},
]

# --- Configuration email (à configurer dans les variables d'environnement) ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

if not SENDER_EMAIL or not SENDER_PASSWORD or not RECEIVER_EMAIL:
    print("Erreur: Les variables d'environnement SENDER_EMAIL, SENDER_PASSWORD et RECEIVER_EMAIL doivent être configurées.")
    print("Veuillez les définir avant d'exécuter le script.")
    sys.exit(1) # Quitte le script si les variables ne sont pas configurées

# --- Logique principale ---
if __name__ == "__main__":
    print(f"Démarrage de l'analyse de portefeuille Iron Dome à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Récupérer le taux d'intérêt sans risque
    live_risk_free_rate = fetch_us_10y_treasury_yield()
    if live_risk_free_rate is None:
        print("Erreur critique: Impossible de récupérer le taux sans risque. Arrêt du script.")
        sys.exit(1) # Quitte si le taux sans risque ne peut pas être récupéré

    # 2. Préparer la liste des tickers uniques pour les sous-jacents et les options
    unique_underlying_tickers = set()
    option_positions_details = [] # Pour stocker les infos des options pour fetch_live_option_data

    for pos in positions:
        ticker = pos["ticker"]
        unique_underlying_tickers.add(ticker)
        if pos["type"] in ["call", "put"]:
            # Créer une copie ou extraire les infos nécessaires pour fetch_live_option_data
            option_positions_details.append({
                "ticker": pos["ticker"],
                "strike": float(pos["strike"]), # Assurer que le strike est un float
                "expiry": pos["expiry"],
                "type": pos["type"]
            })
    
    # Convertir le set en liste pour les fonctions de fetching
    list_of_all_tickers = list(unique_underlying_tickers)

    # 3. Récupérer les prix spot live et rendements de dividende pour tous les sous-jacents
    live_market_data = fetch_live_data(list_of_all_tickers)
    
    # Extraire les prix spot et rendements de dividende pour un accès facile
    live_prices_only = {ticker: data["spot_price"] for ticker, data in live_market_data.items()}
    dividend_yields_by_ticker = {ticker: data["dividend_yield"] for ticker, data in live_market_data.items()}

    # 4. Récupérer les prix live pour les options
    # On passe les détails des options et les prix spot des sous-jacents
    live_option_data = fetch_live_option_data(option_positions_details, live_prices_only)

    # 5. Analyser le portefeuille
    df_portfolio, portfolio_summary, options_valuation_details = analyze_portfolio( 
        positions,
        live_prices_only,
        live_risk_free_rate, 
        dividend_yields_by_ticker,
        live_option_data 
    )
    df_portfolio_sorted = df_portfolio.sort_values(by="Valeur Marché (€)", ascending=False)

    # 6. Générer le rapport en HTML 
    html_report_output = get_portfolio_report_html(df_portfolio_sorted, portfolio_summary, options_valuation_details) # Nouveau paramètre

    # 7. Envoyer l'email avec le rapport HTML
    subject = f"Iron Dome - Rapport de Portefeuille US - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    email_sent_successfully = send_email(subject, html_report_output, RECEIVER_EMAIL, SENDER_EMAIL, SENDER_PASSWORD, is_html=True) # is_html=True est crucial

    if email_sent_successfully:
        print("Analyse de portefeuille Iron Dome terminée.")
        print(f"Rapport envoyé avec succès à {RECEIVER_EMAIL}.")
    else:
        print("\n--- ATTENTION : ÉCHEC DE L'ENVOI D'EMAIL ---")
        print("Le rapport n'a pas pu être envoyé par e-mail. Veuillez vérifier la configuration et les logs d'erreurs.")
