
# irondome

**Outil Python d’analyse de portefeuille exposé aux thématiques défense & géopolitique.**

Ce script analyse un portefeuille construit autour d’ETF et d’options call sélectionnés pour tirer parti de la tendance haussière liée à la doctrine de défense américaine (ex : Iron Dome, Trump, dépenses militaires).

---

## Fonctionnalités

- Récupération de données de marché (prix spot, dividendes)
- Calcul de volatilité implicite
- Pricing des options (Black-Scholes)
- Évaluation du portefeuille (valeur, P&L, exposition)
- Génération d’un rapport synthétique

---

## Structure des fichiers

- `main_portfolio.py` : utiliser pour le report final
- `portfolio_analyzer.py` : calculs et consolidation des positions
- `portfolio_reporter.py` : reporting du portefeuille
- `market_data_fetcher.py` : récupération des données via Yahoo Finance
- `implied_volatility_calculator.py` : estimation de la vol implicite grâce à la "Bisection Method - Dichotomy" 
- `option_pricing.py` : valorisation des calls (Black-Scholes)

---

## Installation

**Python ≥ 3.7 requis**

```bash
pip install pandas numpy scipy yfinance
````

--- 

## Exécution

```bash
python main_portfolio.py
```

Affichage :

* IV et Dividend des sous jacents
* Valorisation par position
* P&L total et par actif
* Répartition ETF vs dérivés
* Durée de vie moyenne des calls

---

## Limitations

* Utilisation de Black-Scholes sur des options américaines
* Données dépendantes de Yahoo Finance

---

## Objectif du projet

Fournir une base robuste et automatisée pour suivre des portefeuilles

--- 

## Amélioration 

* Pouvoir changer dynamiquement la composition du portefeuille
* Automatisation d'un envoi de rapport par email (ex : toutes les ouvertures/clôtures)

