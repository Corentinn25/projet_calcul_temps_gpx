import math

def estimer_temps_utmb(distance, dplus, dmoins, cote_utmb):
    """
    Modèle avec seuil de fatigue retardé.
    L'impact reste faible jusqu'à 40-50 km-e, puis explose pour l'ultra.
    """
    # 1. Calcul de la Distance-Effort (Base ITRA)
    km_e = distance + (dplus / 100) + (dmoins / 200)
    
    vitesse_base_1000 = 31.5
    
    # 2. Facteur de Fatigue Adaptatif
    # Cela crée une courbe qui reste "plate" plus longtemps mais monte plus raide ensuite.
    if km_e > 15:
        # pour libérer de la vitesse sur le 46km tout en gardant le mur sur le 80km.
        facteur_fatigue = math.exp(0.029 * math.pow(km_e - 15, 1.545))
    else:
        facteur_fatigue = 1.0
        
    vitesse_coureur = (vitesse_base_1000 * (cote_utmb / 1000)) / facteur_fatigue
    
    # 3. Calcul du temps en minutes
    temps_minutes = (km_e / vitesse_coureur) * 60
    
    return temps_minutes