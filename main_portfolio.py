# main_portfolio.py
import io
import sys
import pandas as pd
from datetime import datetime
import os


from market_data_fetcher import fetch_live_data, fetch_us_10y_treasury_yield 
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
    {"ticker": "LDOS", "type": "call", "qty": 50, "strike": 180, "expiry": "2025-12-19", "purchase_premium": "3"},
    {"ticker": "BAH", "type": "call", "qty": 16, "strike": 120, "expiry": "2025-12-19", "purchase_premium": "5.15"},
    {"ticker": "KTOS", "type": "call", "qty": 12, "strike": 55, "expiry": "2026-01-16", "purchase_premium": "3.20"},
    {"ticker": "DFEN", "type": "etf", "qty": 1800, "purchase_price": "46.28"}
]


# --- Configuration Email ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "nolhanmas@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "etyv pzzl irtt duin")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "nolhanmas@gmail.com")

# --- Fonction principale pour exécuter l'analyse et envoyer l'email ---
def run_and_email_report():
    print("Démarrage de l'analyse de portefeuille Iron Dome...")

    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECEIVER_EMAIL:
        print("\n--- ATTENTION : CONFIGURATION EMAIL INCOMPLÈTE ---")
        print("Veuillez renseigner SENDER_EMAIL, SENDER_PASSWORD et RECEIVER_EMAIL.")
        print("Pour Gmail, utilisez un 'mot de passe d'application' si vous avez l'authentification à deux facteurs.")
        return

    # --- Récupérer le taux sans risque en direct ---
    live_risk_free_rate = fetch_us_10y_treasury_yield()
    if live_risk_free_rate is None:
        error_msg = "Erreur: Impossible de récupérer le taux du Trésor US à 10 ans. Utilisation d'une valeur par défaut."
        print(error_msg)
        live_risk_free_rate = 0.0441 # Valeur par défaut si la récupération échoue
    else:
        print(f"Taux sans risque (US 10Y Treasury) récupéré en direct: {live_risk_free_rate:.4f}")

    # 1. Obtenir la liste unique des tickers à récupérer
    tickers_to_fetch = list(set([p["ticker"] for p in positions]))

    # 2. Récupérer les données live (prix spot et dividendes)
    live_market_data = fetch_live_data(tickers_to_fetch)

    # Vérifier si les données ont été récupérées avec succès
    if not live_market_data:
        error_msg = "Erreur: Impossible de récupérer les données de marché. Arrêt de l'analyse."
        print(error_msg)
        send_email("Iron Dome - Erreur d'analyse de portefeuille", error_msg, RECEIVER_EMAIL, SENDER_EMAIL, SENDER_PASSWORD, is_html=False)
        return

    # 3. Préparer les dictionnaires pour analyze_portfolio
    live_prices_only = {ticker: data["spot_price"] for ticker, data in live_market_data.items()}
    dividend_yields_by_ticker = {ticker: data["dividend_yield"] for ticker, data in live_market_data.items()}

    # 4. Analyser le portefeuille 
    df_portfolio, portfolio_summary = analyze_portfolio(
        positions,
        live_prices_only,
        live_risk_free_rate, 
        dividend_yields_by_ticker
    )
    df_portfolio_sorted = df_portfolio.sort_values(by="Valeur Marché (€)", ascending=False)

    # 5. Générer le rapport en HTML
    html_report_output = get_portfolio_report_html(df_portfolio_sorted, portfolio_summary)

    # 6. Envoyer l'email avec le rapport HTML
    subject = f"Iron Dome - Rapport de Portefeuille US - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    email_sent_successfully = send_email(subject, html_report_output, RECEIVER_EMAIL, SENDER_EMAIL, SENDER_PASSWORD, is_html=True) # is_html=True est crucial

    if email_sent_successfully:
        print("Analyse de portefeuille Iron Dome terminée.")
        print(f"Rapport envoyé avec succès à {RECEIVER_EMAIL}.")
    else:
        print("\n--- ATTENTION : ÉCHEC DE L'ENVOI D'EMAIL ---")
        print("Le rapport n'a pas pu être envoyé par e-mail. Veuillez vérifier la configuration et les logs d'erreurs.")
        print("Voici le rapport qui aurait dû être envoyé (en HTML pour le debug, si votre console le supporte) :\n")
        print(html_report_output)

if __name__ == "__main__":
    run_and_email_report()
