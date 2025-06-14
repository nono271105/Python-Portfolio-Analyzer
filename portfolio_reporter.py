# portfolio_reporter.py
import pandas as pd

def display_portfolio_report(df_portfolio, portfolio_summary):
    """
    Affiche le tableau détaillé et le résumé du portefeuille.

    Paramètres:
    df_portfolio (pd.DataFrame): DataFrame détaillé du portefeuille.
    portfolio_summary (dict): Dictionnaire récapitulatif du portefeuille.
    """
    print("\n" + "="*40)
    print("--- DÉTAIL ET RÉSUMÉ DU PORTEFEUILLE ---")
    print("="*40)

    print("\n--- Portefeuille détaillé ---")
    
    print(df_portfolio.to_string(index=False)) 

    print("\n--- Résumé du portefeuille ---")
    for key, value in portfolio_summary.items():
        if isinstance(value, (int, float)):
            if "Valeur totale portefeuille" in key or "P&L total portefeuille" in key:
                print(f"{key}: {value:,.2f}€") 
            elif "Exposition" in key:
                print(f"{key}: {value:,.2f}%") 
            elif "Durée moyenne" in key:
                print(f"{key}: {value:,.0f}j") 
            else:
                print(f"{key}: {value:,.2f}")
        else:
            print(f"{key}: {value}")