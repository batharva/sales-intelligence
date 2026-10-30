from config import P
CSS = f"""<style>
html,body,[class*="css"]{{font-family:Inter,system-ui,-apple-system,sans-serif}}
.stApp{{background:{P['bg']};color:{P['text']}}}
section[data-testid=stSidebar]{{background:{P['surface']};border-right:1px solid {P['border']}}}
.block-container{{padding-top:1.5rem;max-width:1400px}}
h1,h2,h3{{font-weight:600;letter-spacing:-.01em}}
.kpi{{background:{P['surface']};border:1px solid {P['border']};padding:12px 14px;margin-bottom:8px}}
.kpi:hover{{border-color:{P['accent']}}}
.kpi .l{{font-size:.66rem;letter-spacing:.1em;text-transform:uppercase;color:{P['muted']}}}
.kpi .v{{font-size:1.7rem;font-weight:700;line-height:1.3}}
.kpi .d{{font-size:.75rem;font-family:ui-monospace,Menlo,monospace}}
.eyebrow{{font-family:ui-monospace,Menlo,monospace;font-size:.75rem;color:{P['accent']};letter-spacing:.08em}}
.muted{{color:{P['muted']};font-size:.8rem;font-family:ui-monospace,Menlo,monospace}}
code,pre{{font-family:ui-monospace,Menlo,monospace!important}}
hr{{border-color:{P['border']}}}
</style>"""

def kpi(label, value, delta, tip):
    if delta is None: d, col = "N/A vs prior period", P["muted"]
    else: d, col = f"{'▲' if delta >= 0 else '▼'} {abs(delta):.1f}% vs prior period", P["pos"] if delta >= 0 else P["neg"]
    return (f"<div class='kpi' title='{tip}'><div class='l'>{label}</div><div class='v'>{value}</div>"
            f"<div class='d' style='color:{col}'>{d}</div></div>")
