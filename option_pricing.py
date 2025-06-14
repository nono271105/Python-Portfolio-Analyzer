# options_pricing.py
import numpy as np
from scipy.stats import norm

def black_scholes_call(S, K, T, r, sigma, q=0):
    """
    Calcule le prix d'une option call européenne en utilisant le modèle Black-Scholes.

    Paramètres:
    S : Prix spot de l'actif sous-jacent
    K : Prix d'exercice (Strike) de l'option
    T : Temps jusqu'à l'échéance en années (Jours restants / 365)
    r : Taux d'intérêt sans risque annuel (ex: 0.05 pour 5%)
    sigma : Volatilité implicite annuelle (ex: 0.20 pour 20%)
    q : Rendement des dividendes annuel (par défaut 0)
    """
    if T <= 0: # Gérer les options expirées
        return max(0, S - K)

    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call_price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

# Un bloc 'if __name__ == "__main__":' est utile pour tester le module indépendamment
if __name__ == "__main__":
    print("Test de la fonction Black-Scholes :")
    S_test = 150
    K_test = 160
    T_test = 0.5
    r_test = 0.04
    sigma_test = 0.30
    price_test = black_scholes_call(S_test, K_test, T_test, r_test, sigma_test)
    print(f"Prix d'un call (S={S_test}, K={K_test}, T={T_test}, r={r_test}, sigma={sigma_test}): {price_test:.2f}")