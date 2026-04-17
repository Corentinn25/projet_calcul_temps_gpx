import math

def estimer_temps_itra(distance, dplus, dmoins, cote_itra):
    """
    Modèle de fatigue ULTRA-EXPONENTIELLE.
    La perte de vitesse s'accélère brutalement avec la distance.
    """
    # 1. Calcul de la Distance-Effort (Base ITRA)
    km_e = distance + (dplus / 100) + (dmoins / 200)
    
    # 2. Facteur de Fatigue "Brutal"
    # vitesse_base_1000 reste ton étalon de 29.5 pour le court
    vitesse_base_1000 = 29.5  
    
    # Coeff à 0.012 : la fatigue devient prédominante très vite.
    # Pour 20km-e : facteur ~1.20 (Légère baisse)
    # Pour 50km-e : facteur ~1.71 (Baisse sensible)
    # Pour 100km-e : facteur ~3.12 (Vitesse divisée par 3 !)
    if km_e > 5:
        # On utilise une croissance exponentielle plus forte
        facteur_fatigue = math.exp(0.0395 * (km_e - 5))
    else:
        facteur_fatigue = 1.0
        
    # Vitesse ajustée : (Base * Niveau) / Fatigue_Exponentielle
    vitesse_coureur = (vitesse_base_1000 * (cote_itra / 1000)) / facteur_fatigue
    
    # 3. Calcul du temps en minutes
    temps_minutes = (km_e / vitesse_coureur) * 60
    
    return temps_minutes