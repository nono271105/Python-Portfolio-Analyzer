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
    options_valuation_details (list): Liste des dictionnaires avec les détails de valorisation des options. 

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
    container_style = "max-width: 800px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); overflow: hidden;"
    header_style = "background-color: #7399c6; color: white; padding: 20px; text-align: center; border-top-left-radius: 8px; border-top-right-radius: 8px;"
    section_style = "padding: 20px; border-bottom: 1px solid #eee;"
    table_style = "width: 100%; border-collapse: collapse; margin-top: 15px;"
    th_td_style = "padding: 10px; border: 1px solid #ddd; text-align: left;"
    th_style = "background-color: #f2f2f2; font-weight: bold;"
    summary_item_style = "padding: 5px 0; border-bottom: 1px dashed #eee; display: flex; justify-content: space-between;"
    summary_label_style = "font-weight: bold; color: #555;"
    summary_value_style = "color: #333;"
    
    # Styles pour la section d'analyse des options
    options_analysis_title_style = "color: #2c3e50; font-size: 1.5em; margin-bottom: 15px; text-align: center;"
    option_block_style = "background-color: #fefefe; border: 1px solid #e0e0e0; border-radius: 5px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);"
    option_header_style = "color: #34495e; font-size: 1.2em; margin-top: 0; margin-bottom: 10px;"
    option_item_style = "margin-bottom: 8px; font-size: 0.95em;"

    # --- En-tête du rapport ---
    html_parts.append(f"<div style=\"{container_style}\">")
    html_parts.append(f"<div style=\"{header_style}\">")
    html_parts.append("<h1>Rapport de Portefeuille Iron Dome</h1>")
    html_parts.append(f"<p>Date du rapport : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    html_parts.append("</div>")

    # --- Résumé du Portefeuille ---
    html_parts.append(f"<div style=\"{section_style}\">")
    html_parts.append("<h2 style=\"color: #2c3e50; text-align: center;\">Résumé du Portefeuille</h2>")
    html_parts.append("<div style=\"padding: 0 20px;\">") # Ajout d'un padding pour le contenu
    
    # Valeur totale portefeuille
    total_value_formatted = f"{portfolio_summary['Valeur totale portefeuille ']:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")
    html_parts.append(f"<div style=\"{summary_item_style}\"><span style=\"{summary_label_style}\">Valeur totale portefeuille :</span> <span style=\"{summary_value_style}\">{total_value_formatted}</span></div>")

    # P&L total portefeuille
    pnl_total_value = portfolio_summary['P&L total portefeuille ']
    pnl_total_color = "color: #e74c3c;" if pnl_total_value < 0 else "color: #27ae60;"
    pnl_total_formatted = f"{pnl_total_value:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")
    html_parts.append(f"<div style=\"{summary_item_style}\"><span style=\"{summary_label_style}\">P&L total portefeuille :</span> <span style=\"{summary_value_style} {pnl_total_color}\">{pnl_total_formatted}</span></div>")

    # Exposition options
    exposure_options_val = portfolio_summary.get('Exposition options ', '0.00%')
    html_parts.append(f"<div style=\"{summary_item_style}\"><span style=\"{summary_label_style}\">Exposition options :</span> <span style=\"{summary_value_style}\">{exposure_options_val}</span></div>")

    # Exposition ETF
    exposure_etf_val = portfolio_summary.get('Exposition ETF ', '0.00%')
    html_parts.append(f"<div style=\"{summary_item_style}\"><span style=\"{summary_label_style}\">Exposition ETF :</span> <span style=\"{summary_value_style}\">{exposure_etf_val}</span></div>")
    
    # Durée moyenne (jours)
    avg_duration = portfolio_summary.get('Durée moyenne (jours)', 0)
    html_parts.append(f"<div style=\"{summary_item_style}\"><span style=\"{summary_label_style}\">Durée moyenne (jours):</span> <span style=\"{summary_value_style}\">{int(avg_duration)}j</span></div>")

    html_parts.append("</div>") # Fin du padding
    html_parts.append("</div>") # Fin de la section

    # --- Détail des Positions ---
    html_parts.append(f"<div style=\"{section_style}\">")
    html_parts.append("<h2 style=\"color: #2c3e50; text-align: center;\">Détail des Positions</h2>")
    html_parts.append(f"<table style=\"{table_style}\">")
    html_parts.append("<thead><tr>")
    for col in df_portfolio.columns:
        html_parts.append(f"<th style=\"{th_td_style} {th_style}\">{col}</th>")
    html_parts.append("</tr></thead>")
    html_parts.append("<tbody>")

    for index, row in df_portfolio.iterrows():
        html_parts.append("<tr>")
        for col in df_portfolio.columns:
            cell_value = row[col]
            cell_style = th_td_style
            if col == "P&L (€)":
                if pd.notna(cell_value):
                    cell_color = "#e74c3c" if cell_value < 0 else "#27ae60"
                    cell_value = f"{cell_value:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")
                    cell_style += f" color: {cell_color};"
                else:
                    cell_value = "-"
            elif col in ["Valeur Marché (€)", "Prix Achat (€/contrat)"]:
                if pd.notna(cell_value):
                    cell_value = f"{cell_value:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    cell_value = "-"
            elif col == "Prix Spot Actuel":
                 # Ne pas formater en € pour la colonne "Prix Spot Actuel" si elle contient plusieurs valeurs
                if "P=" in str(cell_value): # C'est une option avec S=... P=...
                    parts = str(cell_value).split(" P=")
                    s_part = parts[0]
                    p_part = parts[1]
                    # Reformater uniquement le prix P de l'option
                    try:
                        p_value_float = float(p_part.replace('€', ''))
                        p_part_formatted = f"{p_value_float:.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")
                        cell_value = f"{s_part} P={p_part_formatted}"
                    except ValueError:
                        pass # Garder la valeur telle quelle si conversion échoue
                else: # C'est un ETF ou une action avec juste S=...
                    pass # Garder le format actuel
            elif isinstance(cell_value, float):
                if pd.notna(cell_value):
                    cell_value = f"{cell_value:.2f}"
                else:
                    cell_value = "-"
            html_parts.append(f"<td style=\"{cell_style}\">{cell_value}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody>")
    html_parts.append("</table>")
    html_parts.append("</div>") # Fin de la section

    # --- Analyse d'Évaluation des Options ---
    html_parts.append(f"<div style=\"{section_style}\">")
    html_parts.append(f"<h2 style=\"{options_analysis_title_style}\">Analyse d'Évaluation des Options</h2>")
    if not options_valuation_details:
        html_parts.append("<p style=\"text-align: center; color: #7f8c8d;\">Aucune position d'option à analyser.</p>")
    else:
        for opt in options_valuation_details:
            ticker_strike_expiry = f"{opt['ticker']} {opt['strike']:.1f} {opt['expiry']} ({opt['type'].upper()})"
            
            market_price = opt.get('market_price')
            theoretical_price = opt.get('theoretical_price')
            implied_volatility = opt.get('implied_volatility')
            historical_volatility = opt.get('historical_volatility') # Récupérer la volatilité historique
            over_under_value = opt.get('over_under_value')
            over_under_percent = opt.get('over_under_percent')

            html_parts.append(f"<div style=\"{option_block_style}\">")
            html_parts.append(f"<h3 style=\"{option_header_style}\">{ticker_strike_expiry}</h3>")
            
            if pd.notna(market_price):
                html_parts.append(f"<p style=\"{option_item_style}\">Prix du marché (Live) : <strong style=\"color: #2980b9;\">{market_price:.2f}€</strong></p>")
            else:
                html_parts.append(f"<p style=\"{option_item_style}\">Prix du marché (Live) : <span style=\"color: #e74c3c;\">Non disponible</span></p>")

            if pd.notna(theoretical_price):
                html_parts.append(f"<p style=\"{option_item_style}\">Prix théorique (Modèle Binomial) : <strong style=\"color: #8e44ad;\">{theoretical_price:.2f}€</strong></p>")
            else:
                html_parts.append(f"<p style=\"{option_item_style}\">Prix théorique (Modèle Binomial) : <span style=\"color: #e74c3c;\">Non calculé</span></p>")
            
            if pd.notna(implied_volatility):
                html_parts.append(f"<p style=\"{option_item_style}\">Volatilité Implicite : <strong style=\"color: #f39c12;\">{implied_volatility:.2%}</strong></p>")
            else:
                html_parts.append(f"<p style=\"{option_item_style}\">Volatilité Implicite : <span style=\"color: #7f8c8d;\">Non calculée</span></p>")

            # Affichage de la volatilité historique
            if pd.notna(historical_volatility):
                html_parts.append(f"<p style=\"{option_item_style}\">Volatilité Historique (passé) : <strong style=\"color: #16a085;\">{historical_volatility:.2%}</strong></p>")
            else:
                html_parts.append(f"<p style=\"{option_item_style}\">Volatilité Historique : <span style=\"color: #7f8c8d;\">Non disponible</span></p>")

            interpretation = ""
            interpretation_style = ""

            if pd.notna(over_under_value) and pd.notna(over_under_percent):
                diff_formatted = f"{over_under_value:.2f}€"
                percent_formatted = f"({over_under_percent:.2f}%)"
                html_parts.append(f"<p style=\"{option_item_style}\">Différence (Live - Théorique) : <strong style=\"color: #c0392b;\">{diff_formatted}</strong> <span style=\"color: #c0392b;\">{percent_formatted}</span></p>")

                # Interprétation ajustée pour inclure HV vs IV
                if abs(over_under_percent) > 5: # Seuil pour considérer une sur/sous-évaluation significative
                    if over_under_percent > 0: # Live > Théorique
                        interpretation = "Votre modèle sous-évalue l'option par rapport au marché."
                        interpretation_style = "color: #e74c3c; font-weight: bold;"
                        interpretation += " Cela peut indiquer une surévaluation potentielle par le marché."
                    else: # Live < Théorique
                        interpretation = "Votre modèle surévalue l'option par rapport au marché."
                        interpretation_style = "color: #27ae60; font-weight: bold;"
                        interpretation += " Cela peut indiquer une sous-évaluation potentielle par le marché, et donc une opportunité d'achat."
                else: # Proche du prix théorique
                    interpretation = "Le prix de marché est proche du prix théorique de votre modèle."
                    interpretation_style = "color: #7f8c8d;" # Gris
                
                # Ajout de l'interprétation IV vs HV
                if pd.notna(implied_volatility) and pd.notna(historical_volatility):
                    if implied_volatility > historical_volatility * 1.10: # Si IV est significativement plus haute que HV (+10%)
                        interpretation += f"<br>La volatilité implicite ({implied_volatility:.2%}) est significativement plus élevée que la volatilité historique ({historical_volatility:.2%}). Le marché anticipe plus de mouvements futurs que ce que le passé a montré."
                    elif implied_volatility < historical_volatility * 0.90: # Si IV est significativement plus basse que HV (-10%)
                        interpretation += f"<br>La volatilité implicite ({implied_volatility:.2%}) est significativement plus basse que la volatilité historique ({historical_volatility:.2%}). Le marché anticipe moins de mouvements futurs que ce que le passé a montré."
                    else:
                        interpretation += f"<br>La volatilité implicite ({implied_volatility:.2%}) est en ligne avec la volatilité historique ({historical_volatility:.2%})."
                
            else:
                interpretation = "Impossible de calculer la sur/sous-évaluation pour cette option."
                interpretation_style = "color: #7f8c8d;"

            html_parts.append(f"<p style=\"{option_item_style} {interpretation_style}\">{interpretation}</p>")
            html_parts.append("</div>")

    # --- Ajout de la signature ---
    footer_style = "margin-top: 30px; font-size: 0.85em; color: #777; text-align: center; border-top: 1px solid #eee; padding-top: 15px;"
    signature_style = "font-style: italic;"
    html_parts.append(f"<div style=\"{footer_style}\">")
    html_parts.append(f"<p>Généré par <span style=\"{signature_style}\">Iron Dome V3</span></p>")
    html_parts.append(f"<p style=\"font-weight: bold; margin-top: 5px;\">Fait par Nolhan Mas</p>")
    html_parts.append("</div>")

    html_parts.append("</body>")
    html_parts.append("</html>")

    return "".join(html_parts)
