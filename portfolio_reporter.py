# portfolio_reporter.py
import pandas as pd
from datetime import datetime

def get_portfolio_report_html(df_portfolio, portfolio_summary):
    """
    Génère un rapport de portefeuille formaté en HTML avec des styles inline
    pour une compatibilité maximale avec les clients de messagerie (y compris Gmail).

    Paramètres:
    df_portfolio (pd.DataFrame): DataFrame détaillé du portefeuille.
    portfolio_summary (dict): Dictionnaire récapitulatif du portefeuille.

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
    html_parts.append("<div style=\"max-width: 800px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);\">")

    # --- En-tête Général ---
    html_parts.append("<h1 style=\"color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 0; font-size: 2em;\">Rapport d'Analyse de Portefeuille Iron Dome</h1>")
    html_parts.append(f"<p style=\"font-size: 0.9em; color: #666; margin-bottom: 20px;\"><strong>Date du rapport :</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")

    # --- Portefeuille Détaillé ---
    html_parts.append("<h2 style=\"color: #34495e; border-bottom: 1px solid #dcdcdc; padding-bottom: 5px; margin-top: 25px; font-size: 1.5em;\">Portefeuille Détaillé 📈</h2>") # Emoji ajouté ici directement

    df_portfolio_html = df_portfolio.copy()

    # Formatage des colonnes numériques (Valeur Marché)
    for col in ["Valeur Marché (€)"]:
        if col in df_portfolio_html.columns:
            df_portfolio_html[col] = pd.to_numeric(df_portfolio_html[col], errors='coerce')
            df_portfolio_html[col] = df_portfolio_html[col].map('{:,.2f}'.format)
    df_portfolio_html = df_portfolio_html.fillna('-')

    # Styles inline pour P&L
    profit_style = "color: #28a745; font-weight: bold;"   # Vert pour les gains
    loss_style = "color: #dc3545; font-weight: bold;"     # Rouge pour les pertes
    zero_style = "color: #6c757d; font-weight: bold;"     # Gris pour zéro

    # Styles inline pour le tableau
    table_style = "width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.9em;"
    th_style = "border: 1px solid #e9ecef; padding: 10px; text-align: left; background-color: #e2e6ea; color: #495057; font-weight: bold;"
    td_style = "border: 1px solid #e9ecef; padding: 10px; text-align: left;"
    tr_even_bg = "background-color: #fefefe;" # Fond clair pour les lignes paires

    # Début du tableau HTML
    html_parts.append(f"<table style=\"{table_style}\">")
    html_parts.append("<thead><tr>")
    for col in df_portfolio_html.columns:
        html_parts.append(f"<th style=\"{th_style}\">{col}</th>")
    html_parts.append("</tr></thead>")
    html_parts.append("<tbody>")

    # Génération des lignes du tableau avec styles inline
    for i, row in df_portfolio_html.iterrows():
        row_style = f"style=\"{tr_even_bg}\"" if i % 2 == 1 else "" # Appliquer le style pour les lignes paires
        html_parts.append(f"<tr {row_style}>")
        for col_name, cell_value in row.items():
            final_cell_value = str(cell_value)
            cell_specific_style = td_style

            # Appliquer les styles conditionnels pour la colonne P&L (€)
            if col_name == "P&L (€)":
                try:
                    num_val = float(str(cell_value).replace(',', '').replace('€', '').strip())
                    if num_val > 0:
                        cell_specific_style += profit_style # Ajoute le style vert
                        final_cell_value = f"{num_val:,.2f}€"
                    elif num_val < 0:
                        cell_specific_style += loss_style # Ajoute le style rouge
                        final_cell_value = f"{num_val:,.2f}€"
                    else:
                        cell_specific_style += zero_style # Ajoute le style gris
                        final_cell_value = f"{num_val:,.2f}€"
                except ValueError:
                    pass # Si ce n'est pas un nombre, laisser tel quel

            html_parts.append(f"<td style=\"{cell_specific_style}\">{final_cell_value}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody>")
    html_parts.append("</table>")

    # --- Résumé du Portefeuille ---
    html_parts.append("<h2 style=\"color: #34495e; border-bottom: 1px solid #dcdcdc; padding-bottom: 5px; margin-top: 25px; font-size: 1.5em;\">Résumé du Portefeuille 💰</h2>") # Emoji ici aussi
    html_parts.append("<div style=\"background-color: #e9f5ff; padding: 15px; border-radius: 5px; margin-top: 20px;\">") # styles inline pour summary-section

    summary_value_style = "font-weight: bold; color: #0056b3;" # Styles inline pour summary-value

    for key, value in portfolio_summary.items():
        # Utiliser un style inline directement pour le <p>
        p_item_style = "margin-bottom: 8px;"
        if isinstance(value, (int, float)):
            if "Valeur totale portefeuille" in key or "P&L total portefeuille" in key:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.2f}€</span></p>")
            elif "Exposition" in key:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.2f}%</span></p>")
            elif "Durée moyenne" in key:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.0f}j</span></p>")
            else:
                html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value:,.2f}</span></p>")
        else:
            html_parts.append(f"<p style=\"{p_item_style}\"><strong>{key}:</strong> <span style=\"{summary_value_style}\">{value}</span></p>")
    html_parts.append("</div>")

    # --- Ajout de la signature ---
    footer_style = "margin-top: 30px; font-size: 0.85em; color: #777; text-align: center; border-top: 1px solid #eee; padding-top: 15px;"
    signature_style = "font-style: italic;"
    html_parts.append(f"<p style=\"{footer_style}\">Rapport généré automatiquement par Iron Dome.<br><span style=\"{signature_style}\">Par Nolhan Mas</span>.</p>")

    html_parts.append("</div>") # Fermeture du conteneur principal
    html_parts.append("</body>")
    html_parts.append("</html>")

    return "\n".join(html_parts)
