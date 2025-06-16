# portfolio_reporter.py
import pandas as pd
from datetime import datetime
import numpy as np # Assurez-vous d'importer numpy car nous utilisons np.nan

def get_portfolio_report_html(df_portfolio, portfolio_summary, options_valuation_details):
    """
    Génère un rapport de portefeuille formaté en HTML avec des styles inline
    pour une compatibilité maximale avec les clients de messagerie (y compris Gmail).

    Paramètres:
    df_portfolio (pd.DataFrame): DataFrame détaillé du portefeuille.
    portfolio_summary (dict): Dictionnaire récapitulatif du portefeuille.
    options_valuation_details (list): Liste des dictionnaires avec les détails de valorisation des options. # NOUVEAU

    Retourne:
    str: Le rapport formaté en HTML.
    """
    html_parts = []

    # Structure HTML de base avec encodage
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang='fr'>")
    html_parts.append("<head>")
    html_parts.append("<meta charset='utf-8'>") # Assurer l'encodage pour les accents
    html_parts.append("<title>Rapport de Portefeuille Iron Dome</title>")
    html_parts.append("</head>")
    # Styles inline pour le corps du document
    html_parts.append("<body style=\"font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; background-color: #f8f9fa; margin: 0; padding: 20px;\">")

    # Conteneur principal avec styles inline
    container_style = "max-width: 800px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);"
    html_parts.append(f"<div style=\"{container_style}\">")

    # --- En-tête du rapport ---
    header_style = "color: #2c3e50; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #e0e0e0; padding-bottom: 15px;"
    h1_style = "font-size: 2em; margin: 0; padding: 0;"
    p_date_style = "font-size: 0.9em; color: #7f8c8d; margin-top: 5px;"
    html_parts.append(f"<div style=\"{header_style}\">")
    html_parts.append(f"<h1 style=\"{h1_style}\">Rapport de Portefeuille Iron Dome</h1>")
    html_parts.append(f"<p style=\"{p_date_style}\">Date du rapport : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    html_parts.append("</div>")

    # --- Résumé du portefeuille ---
    html_parts.append("<h2 style=\"color: #2c3e50; font-size: 1.5em; margin-bottom: 15px;\">Résumé du Portefeuille</h2>")
    summary_container_style = "background-color: #f0f3f6; border-left: 5px solid #3498db; padding: 15px 20px; margin-bottom: 25px; border-radius: 5px;"
    p_item_style = "margin: 5px 0; font-size: 0.95em;"
    summary_value_style = "font-weight: bold; color: #2c3e50;"
    
    html_parts.append(f"<div style=\"{summary_container_style}\">")
    for key, value in portfolio_summary.items():
        if isinstance(value, (int, float)):
            if "total portefeuille" in key or "P&L total portefeuille" in key:
                color = "green" if value >= 0 else "red"
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}; color: {color};\">{value:,.2f}€</span></p>")
            elif "Exposition" in key:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.2f}%</span></p>")
            elif "Durée moyenne" in key:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.0f}j</span></p>")
            else:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.2f}</span></p>")
        else:
            html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value}</span></p>")
    html_parts.append("</div>")

    # --- Tableau détaillé du portefeuille ---
    html_parts.append("<h2 style=\"color: #2c3e50; font-size: 1.5em; margin-bottom: 15px;\">Détail des Positions</h2>")
    table_style = "width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 0.9em;"
    th_td_style = "padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd;"
    th_style = f"{th_td_style} background-color: #f2f2f2; font-weight: bold; color: #333;"
    td_style = f"{th_td_style} color: #555;"
    
    html_parts.append(f"<table style=\"{table_style}\">")
    
    # En-têtes du tableau
    html_parts.append("<thead><tr>")
    for col in df_portfolio.columns:
        html_parts.append(f"<th style=\"{th_style}\">{col}</th>")
    html_parts.append("</tr></thead>")
    
    # Corps du tableau
    html_parts.append("<tbody>")
    for index, row in df_portfolio.iterrows():
        html_parts.append("<tr>")
        for col in df_portfolio.columns:
            value = row[col]
            display_value = ""
            cell_style = td_style

            if isinstance(value, (int, float)):
                if col == "Valeur Marché (€)" or col == "P&L (€)":
                    display_value = f"{value:,.2f}€"
                    if col == "P&L (€)": # Couleur pour P&L
                        if value > 0:
                            cell_style += " color: green;"
                        elif value < 0:
                            cell_style += " color: red;"
                elif col == "Prix Achat":
                    display_value = f"{value:,.2f}€" if pd.notna(value) else "-"
                elif col == "Jours Restants":
                    display_value = f"{int(value)}" if pd.notna(value) else "-"
                elif col == "Quantité":
                    display_value = f"{int(value)}"
                else:
                    display_value = f"{value:,.2f}" # Formatage par défaut pour d'autres floats
            elif pd.isna(value):
                display_value = "-"
            else:
                display_value = str(value)
            
            html_parts.append(f"<td style=\"{cell_style}\">{display_value}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody>")
    html_parts.append("</table>")


    # --- NOUVELLE SECTION : Analyse de l'évaluation des Options ---
    if options_valuation_details: # Seulement si nous avons des données d'options à analyser
        html_parts.append("<h2 style=\"color: #2c3e50; font-size: 1.5em; margin-top: 30px; margin-bottom: 15px;\">Analyse d'Évaluation des Options</h2>")
        
        # Styles pour les blocs d'options individuels
        option_block_style = "background-color: #e8f4f8; border: 1px solid #b3e0f2; padding: 15px; margin-bottom: 15px; border-radius: 5px;"
        option_header_style = "font-weight: bold; color: #2c3e50; margin-bottom: 10px;"
        option_item_style = "margin: 3px 0; font-size: 0.9em;"
        interpretation_style_base = "font-weight: bold;"

        for detail in options_valuation_details:
            ticker = detail.get("ticker", "N/A")
            strike = detail.get("strike", "N/A")
            expiry = detail.get("expiry", "N/A")
            option_type = detail.get("type", "N/A")
            market_price = detail.get("market_price")
            theoretical_price = detail.get("theoretical_price")
            implied_volatility = detail.get("implied_volatility")
            over_under_value = detail.get("over_under_value")
            over_under_percent = detail.get("over_under_percent")

            if pd.isna(market_price) or pd.isna(theoretical_price):
                 html_parts.append(f"<div style=\"{option_block_style}\">")
                 html_parts.append(f"<p style=\"{option_header_style}\">{ticker} {strike} {expiry} ({option_type.upper()})</p>")
                 html_parts.append(f"<p style=\"{option_item_style}\">Impossible d'évaluer cette option (données manquantes ou invalides).</p>")
                 html_parts.append("</div>")
                 continue

            html_parts.append(f"<div style=\"{option_block_style}\">")
            html_parts.append(f"<p style=\"{option_header_style}\">{ticker} {strike} {expiry} ({option_type.upper()})</p>")
            html_parts.append(f"<p style=\"{option_item_style}\">Prix du marché (Live) : <span style=\"font-weight: bold;\">{market_price:,.2f}€</span></p>")
            html_parts.append(f"<p style=\"{option_item_style}\">Prix théorique (Modèle Binomial) : <span style=\"font-weight: bold;\">{theoretical_price:,.2f}€</span></p>")
            html_parts.append(f"<p style=\"{option_item_style}\">Volatilité Implicite : <span style=\"font-weight: bold;\">{implied_volatility:.2%}</span></p>")
            
            interpretation = ""
            interpretation_style = interpretation_style_base
            if pd.notna(over_under_value):
                html_parts.append(f"<p style=\"{option_item_style}\">Différence (Live - Théorique) : <span style=\"font-weight: bold;\">{over_under_value:,.2f}€</span> ({over_under_percent:,.2f}%)</p>")
                
                if over_under_value > 0.1: # Légèrement sur-évaluée
                    interpretation = "Votre modèle sous-évalue l'option par rapport au marché."
                    interpretation_style += " color: #c0392b;" # Rouge vif
                    if over_under_percent > 5: # Si la différence est > 5%
                         interpretation += " Cela peut indiquer une surévaluation potentielle par le marché."
                         interpretation_style += " font-size: 1.05em;" # Un peu plus grand
                elif over_under_value < -0.1: # Légèrement sous-évaluée
                    interpretation = "Votre modèle surévalue l'option par rapport au marché."
                    interpretation_style += " color: #27ae60;" # Vert vif
                    if over_under_percent < -5: # Si la différence est < -5%
                         interpretation += " Cela peut indiquer une sous-évaluation potentielle par le marché, et donc une opportunité d'achat."
                         interpretation_style += " font-size: 1.05em;"
                else: # Proche du prix théorique
                    interpretation = "Le prix de marché est proche du prix théorique de votre modèle."
                    interpretation_style += " color: #7f8c8d;" # Gris
            else:
                interpretation = "Impossible de calculer la sur/sous-évaluation pour cette option."
                interpretation_style += " color: #7f8c8d;"

            html_parts.append(f"<p style=\"{option_item_style} {interpretation_style}\">{interpretation}</p>")
            html_parts.append("</div>")

    # --- Ajout de la signature ---
    footer_style = "margin-top: 30px; font-size: 0.85em; color: #777; text-align: center; border-top: 1px solid #eee; padding-top: 15px;"
    signature_style = "font-style: italic;"
    html_parts.append(f"<div style=\"{footer_style}\">")
    html_parts.append(f"<p>Généré par <span style=\"{signature_style}\">Iron Dome V3</span></p>")
    html_parts.append(f"<p style=\"font-weight: bold; margin-top: 5px;\">Fait par Nolhan Mas</p>")
    html_parts.append("</div>")

    html_parts.append("</div>") # Fermeture du conteneur principal
    html_parts.append("</body>")
    html_parts.append("</html>")
    
    return "".join(html_parts)

