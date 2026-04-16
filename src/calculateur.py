import math

def estimer_temps_itra(distance, dplus, cote_itra):
    """
    Modèle TRAIL STANDARD - Base 28.5.
    Calibrage équilibré pour la majorité des terrains de trail.
    """
    if distance <= 0 or cote_itra <= 0:
        return 0
    
    # 1. Calcul du Kilomètre-Effort (100m D+ = 1km plat)
    km_effort = distance + (dplus / 100)
    
    # 2. Courbe de vitesse avec base 28.5
    # Décroissance de 1.70 pour simuler la gestion de l'effort sur la durée
    base_vitesse_ref = 28.5 - (1.70 * math.log(km_effort + 1))
    
    # 3. Vitesse finale en km-effort/h
    v_km_e_h = (cote_itra / 1000) * base_vitesse_ref
    
    # 4. Temps en minutes
    return (km_effort / v_km_e_h) * 60