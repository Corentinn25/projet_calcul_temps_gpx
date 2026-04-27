import math

def estimer_temps_utmb_2_0(distance_km, d_plus, d_moins, cote_utmb):
    """
    Estimation du temps basée sur la logique UTMB Index 2.0
    - Utilise une Distance Equivalente (Deq) non-linéaire
    - Ajuste la vitesse de référence selon l'Index
    """
    if distance_km <= 0 or cote_utmb <= 0:
        return 0
    
    # 1. CALCUL DE LA DISTANCE ÉQUIVALENTE (Deq)
    # Au lieu du km-effort fixe, on pondère l'effort réel.
    # L'UTMB 2.0 valorise plus le D+ technique.
    # On utilise un ratio de pente moyen (en %)
    pente_moyenne_montante = (d_plus / (distance_km * 500)) * 100 # Approx sur moitié distance
    
    # Nouveau calcul de la distance effort (Pondération 2.0)
    # Le D+ compte pour environ 1km effort tous les 100m, 
    # mais on ajoute un bonus de pénibilité pour les fortes pentes.
    coeff_deniv = 10.0 if pente_moyenne_montante > 15 else 8.5
    km_effort = distance_km + (d_plus / (coeff_deniv * 10)) + (d_moins / 250)

    # 2. VITESSE DE RÉFÉRENCE (Vref)
    # Un score de 1000 correspond environ à 21.5 km-effort/h sur du long.
    # La relation n'est pas strictement linéaire : on utilise une puissance 
    # pour refléter la difficulté à maintenir la vitesse sur la durée.
    vitesse_base = 21.5 * (cote_utmb / 1000) ** 0.95

    # 3. FACTEUR DE FATIGUE (Modèle Endurance)
    # L'UTMB 2.0 prend en compte que l'endurance est une composante de l'index.
    # On applique un ralentissement logarithmique basé sur la distance effort.
    if km_effort > 20:
        # Perte d'efficacité d'environ 3% à 7% par doublement de distance
        facteur_endurance = 1 + (math.log(km_effort / 20, 2) * 0.05)
    else:
        facteur_endurance = 1.0

    # 4. CALCUL DU TEMPS FINAL
    # Temps (h) = Km_Effort / Vitesse_Base * Fatigue
    temps_heures = (km_effort / vitesse_base) * facteur_endurance
    
    return temps_heures * 60 # Retour en minutes

# Exemple d'utilisation :
# temps = estimer_temps_utmb_2_0(distance_km=170, d_plus=10000, d_moins=10000, cote_utmb=800)