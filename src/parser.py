import gpxpy
import pandas as pd
import numpy as np
from geopy.distance import geodesic

def parse_gpx(file):
    gpx = gpxpy.parse(file)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({'lat': point.latitude, 'lon': point.longitude, 'ele': point.elevation})
    
    df = pd.DataFrame(points)
    
    # Distances
    distances = [0]
    for i in range(1, len(df)):
        p1 = (df.iloc[i-1]['lat'], df.iloc[i-1]['lon'])
        p2 = (df.iloc[i]['lat'], df.iloc[i]['lon'])
        distances.append(geodesic(p1, p2).meters)
    
    df['dist_rel'] = distances
    df['dist_cum'] = df['dist_rel'].cumsum() / 1000 # en km
    
    # Dénivelé et D+ cumulé
    df['ele_diff'] = df['ele'].diff().fillna(0)
    df['dplus_cum'] = df['ele_diff'].clip(lower=0).cumsum() # Ne garde que les valeurs positives et cumule
    
    # Calcul de la pente (%) : (Vertical / Horizontal) * 100
    # On utilise un rolling moyen pour éviter les pentes absurdes à 150% dues au bruit GPS
    df['pente'] = (df['ele_diff'] / df['dist_rel'].replace(0, np.nan)) * 100
    df['pente'] = df['pente'].fillna(0).rolling(window=5, center=True).mean() 
    
    return df