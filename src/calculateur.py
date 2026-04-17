import math

def estimer_temps_itra(distance, dplus, dmoins, cote_itra):
    """
    Calcule le temps de passage en s'inspirant de la logique ITRA :
    - Utilise le D+ et le D-
    - Applique une dérive d'endurance logarithmique
    """
    # 1. Calcul de la Distance-Effort (Logique ITRA complète)
    # L'ITRA considère que 100m D+ = 1km et 200m D- = 1km
    km_e = distance + (dplus / 100) + (dmoins / 200)
    
    # 2. Facteur de Fatigue (Pénalité d'Endurance)
    # On définit une base de vitesse "vitesse record" (Vref) pour une cote 1000.
    # On ajuste cette vitesse selon la longueur de la course (km_e).
    # Plus c'est long, plus la vitesse de référence diminue.
    
    # Constantes d'ajustement empiriques pour coller aux tables ITRA
    vitesse_base_1000 = 29.5  # km-e/h (proche du record marathon mis à plat)
    
    # Dérive : on perd en efficacité au fur et à mesure que les km-e s'accumulent
    # On utilise une puissance pour simuler l'épuisement des réserves
    if km_e > 10:
        # Facteur qui réduit la vitesse de référence quand la distance augmente
        # Puissance 0.07 : dérive modérée (trail court)
        # Puissance 0.11 : dérive forte (ultra trail)
        facteur_fatigue = math.pow(km_e / 10, 0.09)
    else:
        facteur_fatigue = 1.0
        
    # Vitesse cible ajustée à la cote du coureur
    # Une cote 600 court à 60% de la vitesse de référence
    vitesse_coureur = (vitesse_base_1000 / facteur_fatigue) * (cote_itra / 1000)
    
    # 3. Calcul du temps en minutes
    temps_minutes = (km_e / vitesse_coureur) * 60
    
    return temps_minutes