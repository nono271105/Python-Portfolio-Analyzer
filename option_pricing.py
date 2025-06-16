# option_pricing.py
import numpy as np
from scipy.stats import norm


def black_scholes_call(S, K, T, r, sigma, q=0):
    """
    Calcule le prix d'une option call européenne en utilisant le modèle Black-Scholes.

    Paramètres:
    S : Prix spot de l'actif sous-jacent
    K : Prix d'exercice (Strike) de l'option
    T : Temps jusqu'à l'échéance en années (Jours restants / 365)
    r : Taux d'intérêt sans risque annuel (ex: 0.05 pour 5% ou 0.045 pour 4.5%)
    sigma : Volatilité implicite annuelle (ex: 0.20 pour 20%)
    q : Rendement des dividendes annuel (par défaut 0, en décimal 0.01 pour 1%)
    """
    if T <= 0: # Gérer les options expirées
        return max(0, S - K)

    # Éviter les divisions par zéro si sigma est proche de zéro
    if sigma < 1e-6: # Gérer le cas de volatilité très faible
        return max(0, S * np.exp(-q * T) - K * np.exp(-r * T)) # Approximation pour sigma très petit

    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price



def binomial_tree_american_call(S, K, T, r, sigma, q, N):
    """
    Calcule le prix d'une option call américaine en utilisant le modèle d'arbre binomial.

    Paramètres:
    S (float): Prix spot de l'actif sous-jacent.
    K (float): Prix d'exercice de l'option.
    T (float): Temps jusqu'à l'échéance en années.
    r (float): Taux d'intérêt sans risque annuel.
    sigma (float): Volatilité annuelle.
    q (float): Rendement des dividendes annuel.
    N (int): Nombre de pas dans l'arbre binomial. Plus N est grand, plus le modèle est précis, mais plus lent.
    """
    if T <= 0:
        return max(0, S - K)

    dt = T / N  # Longueur d'un pas de temps
    u = np.exp(sigma * np.sqrt(dt)) # Facteur de hausse
    d = 1 / u # Facteur de baisse
    p = (np.exp((r - q) * dt) - d) / (u - d) # Probabilité neutre au risque de hausse

    # Vérification des probabilités (doivent être entre 0 et 1)
    if not (0 <= p <= 1):
        print(f"Warning: Probability p={p:.4f} is out of [0,1] range. Check input parameters or increase N.")
        return np.nan 

    # Initialisation des prix de l'actif sous-jacent à l'échéance
    ST = np.zeros(N + 1)
    for j in range(N + 1):
        ST[j] = S * (u**(N - j)) * (d**j)

    # Initialisation des valeurs de l'option à l'échéance
    # Pour un call, c'est max(0, ST - K)
    option_values = np.maximum(0, ST - K)

    # Remontée dans l'arbre
    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            # Valeur de l'option par non-arbitrage
            continuation_value = np.exp(-r * dt) * (p * option_values[j] + (1 - p) * option_values[j + 1])
            
            # Valeur d'exercice anticipé (Intrinsic Value)
            # Prix de l'actif sous-jacent au nœud actuel
            current_S = S * (u**(i - j)) * (d**j)
            exercise_value = np.maximum(0, current_S - K)
            
            # Pour une option américaine, la valeur est le maximum de la continuation_value
            # et de l'exercise_value
            option_values[j] = np.maximum(continuation_value, exercise_value)

    return option_values[0] # Le prix de l'option au temps 0



# Un bloc 'if __name__ == "__main__":' est utile pour tester le module indépendamment
if __name__ == "__main__":
    print("Test de la fonction Black-Scholes :")
    S_test_bs = 150
    K_test_bs = 150
    T_test_bs = 1.0
    r_test_bs = 0.05
    sigma_test_bs = 0.20
    q_test_bs = 0.02
    price_bs = black_scholes_call(S_test_bs, K_test_bs, T_test_bs, r_test_bs, sigma_test_bs, q_test_bs)
    print(f"Prix Black-Scholes (Call Européen) : {price_bs:.4f}")

    print("\nTest de la fonction d'Arbre Binomial (Call Américain) :")
    S_test_bt = 150
    K_test_bt = 150
    T_test_bt = 1.0
    r_test_bt = 0.05
    sigma_test_bt = 0.20
    q_test_bt = 0.02
    N_steps = 100 # Nombre de pas pour le modèle binomial (plus c'est élevé, plus c'est précis)

    price_bt = binomial_tree_american_call(S_test_bt, K_test_bt, T_test_bt, r_test_bt, sigma_test_bt, q_test_bt, N_steps)
    if not np.isnan(price_bt):
        print(f"Prix Arbre Binomial (Call Américain) : {price_bt:.4f} (avec {N_steps} pas)")
    else:
        print("Échec du calcul du prix par arbre binomial.")
    
    # Test avec des paramètres où l'exercice anticipé pourrait être pertinent (dividendes)
    print("\nTest Arbre Binomial avec dividende important (pour voir l'exercice anticipé) :")
    S_test_div = 100
    K_test_div = 90
    T_test_div = 0.5
    r_test_div = 0.02
    sigma_test_div = 0.30
    q_test_div = 0.10 # Dividende important
    N_steps_div = 50
    price_bt_div = binomial_tree_american_call(S_test_div, K_test_div, T_test_div, r_test_div, sigma_test_div, q_test_div, N_steps_div)
    if not np.isnan(price_bt_div):
        print(f"Prix Arbre Binomial (Call Américain, dividende élevé) : {price_bt_div:.4f}")
    else:
        print("Échec du calcul du prix par arbre binomial (dividende élevé).")
