# Python Portfolio Analyzer

**Outil Python d’analyse de portefeuille exposé aux thématiques défense & géopolitique.**

Ce script analyse un portefeuille construit autour d’ETF et d’options call sélectionnés pour tirer parti de la tendance haussière liée à la doctrine de défense américaine (ex : Iron Dome, Trump, dépenses militaires). Il est désormais **automatisé et déployé sur une machine virtuelle** pour des rapports quotidiens.

---

## Fonctionnalités

- Récupération de données de marché (prix spot des sous-jacents, rendements obligataires, **prix live Bid/Ask des options**)
- **Calcul de Volatilité Historique annualisée (pour les sous-jacents des options)**
- Calcul de volatilité implicite (`Bisection Method - Dichotomy`)
- Pricing des options (**Modèle d'arbre binomial pour les calls américains**, et Black-Scholes si spécifié pour Européennes)
- Évaluation du portefeuille (valeur, P&L, exposition, durée moyenne des positions d'options)
- Génération d’un rapport synthétique **HTML** détaillé, incluant une analyse de sur/sous-évaluation des options **et la comparaison Volatilité Implicite vs. Volatilité Historique**.
- **Envoi automatisé et sécurisé des rapports par e-mail**

---

## Structure des fichiers

- `main_portfolio.py` : Point d'entrée principal pour l'exécution du rapport, orchestre la récupération des données, l'analyse et la génération du rapport.
- `portfolio_analyzer.py` : Effectue les calculs détaillés des valeurs de marché, du P&L et des métriques d'exposition pour chaque position.
- `portfolio_reporter.py` : Génère le rapport HTML synthétique et détaillé du portefeuille, y compris les interprétations des valorisations d'options.
- `market_data_fetcher.py` : Gère la récupération des données de marché (prix spot des sous-jacents, rendements obligataires, **chaîne d'options live de Yahoo Finance, et données historiques pour la volatilité**).
- `implied_volatility_calculator.py` : Estime la volatilité implicite des options en utilisant la méthode de la dichotomie, **en se basant sur le prix de marché fourni**.
- `option_pricing.py` : Contient les implémentations des modèles de valorisation d'options : Black-Scholes (pour options européennes) et **Arbre Binomial (pour options américaines)**.
- `email_reporter.py` : Gère l'envoi des rapports générés par e-mail de manière sécurisée.
- `requirements.txt` : Liste toutes les dépendances Python nécessaires au projet.

---

## Installation

**Python ≥ 3.7 requis**

Pour installer et exécuter le projet, il est fortement recommandé d'utiliser un environnement virtuel :

```bash
# 1. Créez un environnement virtuel (si ce n'est pas déjà fait)
python3 -m venv myenv

# 2. Activez l'environnement virtuel
source myenv/bin/activate

# 3. Installez les dépendances du projet
pip install -r requirements.txt
```

---

## Déploiement et Automatisation sur VM

Le système est conçu pour un déploiement robuste et une exécution automatisée sur une machine virtuelle (VM), telle qu'une instance Google Cloud.

### 1. Préparation de la VM

* **Copiez les fichiers du projet :** Transférez tous les fichiers du projet (`.py`, `requirements.txt`, etc.) de votre machine locale vers un répertoire dédié sur la VM (ex: `/home/votrenomutilisateur/iron/`)

* **Installez les dépendances sur la VM :** Une fois les fichiers copiés sur la VM, connectez-vous en SSH, naviguez dans le répertoire du projet, activez l'environnement virtuel et installez les dépendances :
    ```bash
    cd /home/xxxx/iron/
    python3 -m venv myenv
    source myenv/bin/activate
    pip install -r requirements.txt
    ```

### 2. Configuration de l'automatisation avec Cron

Les rapports sont automatiquement générés et envoyés par e-mail deux fois par jour via une tâche Cron.

* **Ouvrez votre `crontab` pour édition sur la VM :**
    ```bash
    crontab -e
    ```
* **Ajoutez les lignes suivantes à votre `crontab` :**
    * **Important :** Adaptez les chemins (`/home/xxxx/...`) et les variables d'environnement (`SENDER_EMAIL`, `SENDER_PASSWORD`, `RECEIVER_EMAIL`) avec vos informations. Le `SENDER_PASSWORD` doit être un mot de passe d'application si vous utilisez Gmail avec l'authentification à deux facteurs.
    * Les heures sont définies en **UTC** sur la VM, ce qui correspond à l'heure de Paris (CEST) ajustée. Par exemple, 15h30 CEST = 13h30 UTC, et 22h00 CEST = 20h00 UTC.

    ```cron
    # ------------- Tâches Cron pour Iron Dome --------------
    # Rapports quotidiens à 15h30 et 22h00 (heure de Paris / CEST)
    # Ceci correspond à 13h30 et 20h00 UTC sur la VM

    30 13 * * * SENDER_EMAIL="votre_email@gmail.com" SENDER_PASSWORD="votre_mot_de_passe_app" RECEIVER_EMAIL="votre_email_dest@example.com" /home/xxxx/myenv/bin/python /home/xxxx/iron/main_portfolio.py >> /home/xxxx/cron_output.log 2>&1
    0 20 * * * SENDER_EMAIL="votre_email@gmail.com" SENDER_PASSWORD="votre_mot_de_passe_app" RECEIVER_EMAIL="votre_email_dest@example.com" /home/xxxx/myenv/bin/python /home/xxxx/iron/main_portfolio.py >> /home/xxxx/cron_output.log 2>&1
    ```

* **Suivi et débogage :** La sortie des exécutions Cron est redirigée vers `/home/xxxx/cron_output.log`. Vous pouvez le consulter pour vérifier le bon déroulement ou diagnostiquer des erreurs :
    ```bash
    cat /home/xxxx/cron_output.log
    # ou pour un suivi en temps réel :
    tail -f /home/xxxx/cron_output.log
    ```

---

## Exécution (Manuelle)

Pour exécuter le script manuellement depuis l'environnement virtuel activé sur la VM ou votre machine locale :

```bash
python main_portfolio.py
```

**Affichage (en console ou dans le log si automatisé) :**

* Volatilité implicite (IV), **Volatilité historique des sous-jacents**, et Rendements de dividende des sous-jacents
* Valorisation par position
* P&L total et par actif
* Répartition ETF vs dérivés
* Durée de vie moyenne des calls

---

## Limitations

* **Actuellement, la valorisation des options et le calcul de la volatilité implicite sont principalement implémentés pour les options d'achat (calls).**
* Dépendance des données à l'API de Yahoo Finance.

---

## Objectif du projet

Fournir une base robuste et automatisée pour suivre des portefeuilles avec une analyse détaillée des options et des ETF.

---

## Améliorations Possibles

* Ajouter la possibilité de valoriser et d'analyser les options de vente (puts).
* Ajouter la possibilité de changer dynamiquement la composition du portefeuille via un fichier de configuration externe (ex : JSON, CSV).
* Intégrer d'autres modèles d'évaluation d'options (ex: Monte Carlo pour les options américaines).
* Gérer les erreurs d'API de manière plus robuste (ex: retries, backoff).
* Améliorer l'interface utilisateur ou ajouter des visualisations.
