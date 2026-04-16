import pandas as pd

def compute_segments(df, threshold=100, tolerance=40):
    if df.empty: return pd.DataFrame()

    segments = []
    start_idx = 0
    peak_ele = df.iloc[0]['ele']
    peak_idx = 0
    valley_ele = df.iloc[0]['ele']
    valley_idx = 0
    mode = None

    for i in range(1, len(df)):
        curr_ele = df.iloc[i]['ele']
        
        # Détection proactive
        if i > 50:
            dist_prev = (df.iloc[i]['dist_cum'] - df.iloc[start_idx]['dist_cum'])
            if dist_prev > 0.5:
                pente_locale = (curr_ele - df.iloc[start_idx]['ele']) / (dist_prev * 1000) * 100
                if mode is None and abs(pente_locale) > 4:
                    mode = 'up' if pente_locale > 0 else 'down'

        if mode != 'up':
            if curr_ele > valley_ele + threshold:
                if mode == 'down':
                    segments.append((start_idx, valley_idx, 'Descente'))
                    start_idx = valley_idx
                mode = 'up'
                peak_ele = curr_ele
                peak_idx = i
        else:
            if curr_ele < peak_ele - tolerance:
                segments.append((start_idx, peak_idx, 'Montée'))
                start_idx = peak_idx
                mode = 'down'
                valley_ele = curr_ele
                valley_idx = i
            elif curr_ele > peak_ele:
                peak_ele = curr_ele
                peak_idx = i

        if mode == 'down':
            if curr_ele < valley_ele:
                valley_ele = curr_ele
                valley_idx = i
            elif curr_ele > valley_ele + tolerance:
                segments.append((start_idx, valley_idx, 'Descente'))
                start_idx = valley_idx
                mode = 'up'
                peak_ele = curr_ele
                peak_idx = i

    segments.append((start_idx, len(df)-1, mode if mode else 'Plat'))

    summary = []
    for start, end, _ in segments:
        sub = df.iloc[start:end+1]
        dist = sub['dist_rel'].sum() / 1000
        if dist < 0.1: continue
        
        dplus_sec = int(sub['ele_diff'].clip(lower=0).sum())
        dmoins_sec = int(abs(sub['ele_diff'].clip(upper=0).sum()))
        d_net = sub['ele'].iloc[-1] - sub['ele'].iloc[0]
        pente = (d_net / (dist * 1000) * 100) if dist > 0 else 0
        
        # --- LOGIQUE DE NOMMAGE SYMÉTRIQUE ---
        if pente > 3:
            if dplus_sec < 100: label = "⛰️ Petite côte"
            elif 100 <= dplus_sec < 300: label = "🏔️ Moyenne côte"
            elif 300 <= dplus_sec < 1000: label = "🌋 Grande côte"
            else: label = "🌌 SUPER CÔTE"
            
        elif pente < -3:
            if dmoins_sec < 100: label = "🏃 Petite descente"
            elif 100 <= dmoins_sec < 300: label = "📉 Moyenne descente"
            elif 300 <= dmoins_sec < 1000: label = "🎿 Grande descente"
            else: label = "💀 SUPER DESCENTE"
            
        elif abs(pente) <= 3 and (sub['ele_diff'].abs().sum() > threshold/2):
            label = "🏃 Vallonné"
        else:
            label = "🛣️ Plat"
            
        summary.append({
            "Section": label,
            "Distance (km)": round(dist, 2),
            "Cumul (km)": round(sub['dist_cum'].iloc[-1], 2),
            "D+ (m)": dplus_sec,
            "D- (m)": dmoins_sec,
            "Pente moy (%)": round(pente, 1)
        })

    return pd.DataFrame(summary)