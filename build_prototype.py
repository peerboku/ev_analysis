"""One-off generator for the Klimadashboard-style widget prototype.

Reads the final CSV and writes a self-contained outputs/dashboard.html that
mimics the Klimadashboard widget chrome: colored category header (Grafik),
plain title + logo header (Tabelle/Info), and a bottom toggle bar with icons.
Prototype for the Klimadashboard call — not part of the main pipeline.
"""
from pathlib import Path
import pandas as pd

CSV = Path("data/final/ev_registrations_monthly_clean.csv")
PNG = "dashboard_emissionsfreie_pkw_neuzulassungen.png"  # headed chart (yellow bar); sits next to the html in outputs/
OUT = Path("outputs/dashboard.html")

df = pd.read_csv(CSV).sort_values("month").reset_index(drop=True)

MONTHS_DE = {
    "01": "Jänner", "02": "Februar", "03": "März", "04": "April",
    "05": "Mai", "06": "Juni", "07": "Juli", "08": "August",
    "09": "September", "10": "Oktober", "11": "November", "12": "Dezember",
}


def de_num(x):
    return f"{int(round(x)):,}".replace(",", ".")


def de_pct(x):
    return f"{x * 100:.1f}".replace(".", ",") + " %"


def month_label(m):
    y, mm = m.split("-")
    return f"{MONTHS_DE[mm]} {y}"


latest = df.iloc[-1]
latest_label = month_label(latest["month"])
latest_pct = de_pct(latest["emission_free_share"])
stand = month_label(latest["month"])

rows = []
for _, r in df[::-1].iterrows():
    rows.append(
        "<tr>"
        f"<td>{month_label(r['month'])}</td>"
        f"<td class='num'>{de_num(r['total_new_registrations'])}</td>"
        f"<td class='num'>{de_num(r['electric_new_registrations'])}</td>"
        f"<td class='num'>{de_num(r['hybrid_new_registrations'])}</td>"
        f"<td class='num'>{de_num(r['emission_free_registrations'])}</td>"
        f"<td class='num'>{de_pct(r['ev_share'])}</td>"
        f"<td class='num'>{de_pct(r['hybrid_share'])}</td>"
        f"<td class='num'>{de_pct(r['emission_free_share'])}</td>"
        "</tr>"
    )
table_rows = "\n".join(rows)

# Klimadashboard logo, recreated as inline SVG (green rounded square + chevron "K")
LOGO = (
    '<svg class="logo" viewBox="0 0 100 100" width="26" height="26" aria-hidden="true">'
    '<defs><linearGradient id="kg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#57C98C"/><stop offset="1" stop-color="#2BA77A"/>'
    '</linearGradient></defs>'
    '<rect x="4" y="4" width="92" height="92" rx="20" fill="url(#kg)"/>'
    '<rect x="22" y="32" width="20" height="38" rx="6" fill="#EAF7EF" opacity="0.95"/>'
    '<polyline points="60,32 40,51 60,70" fill="none" stroke="#EAF7EF" stroke-width="14" '
    'stroke-linecap="round" stroke-linejoin="round" opacity="0.6"/>'
    '<polyline points="80,32 60,51 80,70" fill="none" stroke="#EAF7EF" stroke-width="14" '
    'stroke-linecap="round" stroke-linejoin="round" opacity="0.4"/>'
    '</svg>'
)
BRAND = f'<span class="brand">Klimadashboard.at{LOGO}</span>'

# Inline SVG icons (stroke = currentColor)
ICON_CHART = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="20" x2="6" y2="13"/><line x1="12" y1="20" x2="12" y2="6"/><line x1="18" y1="20" x2="18" y2="10"/></svg>'
ICON_TABLE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="16" rx="1.5"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="9" y1="4" x2="9" y2="20"/></svg>'
ICON_INFO = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><polyline points="14 3 14 8 19 8"/><line x1="8.5" y1="13" x2="15.5" y2="13"/><line x1="8.5" y1="17" x2="13.5" y2="17"/></svg>'
ICON_LINK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>'
ICON_CODE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 8 5 12 9 16"/><polyline points="15 8 19 12 15 16"/></svg>'

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Emissionsfreie PKW-Neuzulassungen — Österreich</title>
<style>
  :root {{
    --bg: #111113;
    --panel: #27272A;
    --grid: #71717B;
    --text: #F4F4F5;
    --muted: #9F9FA9;
    --mobility: #F5AF4A;
    --kd-green: #3FBE8C;
    --line: #2a2a2e;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 40px 16px;
    background: #0c0c0d;
    color: var(--text);
    font-family: "Barlow", system-ui, -apple-system, "Segoe UI", sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .widget {{
    max-width: 860px; margin: 0 auto;
    background: var(--bg);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 1px 0 #1c1c1f inset;
  }}

  /* Plain title header (all tabs) */
  .plain-header {{
    padding: 22px 26px 8px;
    display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
  }}
  .plain-header h2 {{ margin: 0; font-size: 21px; font-weight: 700; line-height: 1.25; }}
  .plain-header .subtitle {{ margin: 6px 0 0; color: var(--muted); font-size: 15px; line-height: 1.5; max-width: 56ch; }}
  .brand {{ display: flex; align-items: center; gap: 8px; color: var(--kd-green); font-weight: 600; font-size: 15px; white-space: nowrap; }}
  .brand .logo {{ flex: none; }}

  .body {{ padding: 20px 26px 8px; }}
  .body.tight {{ padding-top: 8px; }}

  img.chart {{ width: 100%; height: auto; display: block; border-radius: 8px; }}

  .source {{ color: var(--muted); font-size: 12.5px; line-height: 1.5; padding: 6px 26px 0; }}

  /* Table */
  .table-wrap {{ max-height: 440px; overflow: auto; border-radius: 10px; border: 1px solid var(--line); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  thead th {{
    position: sticky; top: 0; background: var(--panel); color: var(--muted);
    text-align: left; font-weight: 600; padding: 10px 14px; white-space: nowrap;
  }}
  tbody td {{ padding: 8px 14px; border-top: 1px solid #1f1f22; }}
  tbody tr:hover {{ background: #1a1a1d; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}

  /* Info text */
  .info p {{ color: #d4d4d8; font-size: 15.5px; line-height: 1.65; margin: 0 0 16px; }}
  .info b {{ color: var(--text); }}
  .info .methodik {{ margin-top: 26px; padding-top: 20px; border-top: 1px solid var(--line); }}
  .info .methodik h3 {{ color: var(--text); font-size: 17px; font-weight: 700; margin: 0 0 12px; }}
  .info .methodik p {{ font-size: 14.5px; color: var(--muted); }}
  .src-table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 10px; }}
  .src-table th {{ text-align: left; color: var(--muted); font-weight: 600; padding: 8px 12px; border-bottom: 1px solid var(--line); }}
  .src-table td {{ padding: 8px 12px; border-bottom: 1px solid #1f1f22; color: #d4d4d8; vertical-align: top; }}
  .src-table td:first-child {{ font-weight: 600; color: var(--text); white-space: nowrap; }}

  .panel {{ display: none; }}
  .panel.active {{ display: block; }}

  /* Bottom toggle bar */
  .toolbar {{
    display: flex; align-items: stretch; justify-content: space-between;
    border-top: 1px solid var(--line); margin-top: 14px;
  }}
  .toolbar-left {{ display: flex; }}
  .toolbar-right {{ display: flex; align-items: center; padding-right: 18px; gap: 16px; color: var(--muted); }}
  .toolbar-right a {{ color: var(--muted); display: inline-flex; cursor: pointer; }}
  .toolbar-right a:hover {{ color: var(--text); }}
  .tab {{
    display: inline-flex; align-items: center; gap: 8px;
    border: 0; background: transparent; color: var(--muted);
    font: inherit; font-size: 15px; padding: 16px 20px; cursor: pointer;
    border-top: 2px solid transparent; margin-top: -1px;
    transition: color .15s;
  }}
  .tab:hover {{ color: var(--text); }}
  .tab[aria-selected="true"] {{ color: var(--text); border-top-color: var(--mobility); font-weight: 600; }}
</style>
</head>
<body>
  <div class="widget">

    <!-- Grafik -->
    <section id="grafik" class="panel active">
      <div class="plain-header">
        <div>
          <h2>Elektromobilität Ziele und Neuzulassungen</h2>
          <p class="subtitle">Emissionsfreie PKW-Zulassungen muss mehr Priorität bekommen für 2030-AT-Ziel und 2035-EU-Ziel</p>
        </div>
        {BRAND}
      </div>
      <div class="body"><img class="chart" src="{PNG}" alt="Diagramm: Emissionsfreie PKW-Neuzulassungen"></div>
      <p class="source">Quelle: Statistik Austria — KFZ-Neuzulassungen nach Bundesland und Kraftstoffart/Energiequelle (Stand: {stand}).<br>Zielpfade: Mobilitätsmasterplan 2030 (AT), EU-Flottengrenzwerte 2035.</p>
    </section>

    <!-- Tabelle -->
    <section id="tabelle" class="panel">
      <div class="plain-header">
        <h2>Neuzulassungen nach Monat</h2>
        {BRAND}
      </div>
      <div class="body tight">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Monat</th>
                <th style="text-align:right">Neuzulassungen gesamt</th>
                <th style="text-align:right">Elektro</th>
                <th style="text-align:right">Hybrid</th>
                <th style="text-align:right">Emissionsfrei</th>
                <th style="text-align:right">Anteil Elektro</th>
                <th style="text-align:right">Anteil Hybrid</th>
                <th style="text-align:right">Anteil emissionsfrei</th>
              </tr>
            </thead>
            <tbody>
{table_rows}
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Info -->
    <section id="info" class="panel info">
      <div class="plain-header">
        <h2>Elektromobilität: Ziele und Neuzulassungen</h2>
        {BRAND}
      </div>
      <div class="body tight">
        <p>Mit dem Mobilitätsmasterplan 2030 hat Österreich den Rahmen gesetzt, den Verkehr
           schrittweise auf klimafreundliche Antriebe umzustellen. Ein zentraler Baustein ist die
           Umstellung der PKW-Neuzulassungen auf emissionsfreie Fahrzeuge — also rein
           batterieelektrische Autos und Wasserstoff-Brennstoffzellenfahrzeuge. Auf EU-Ebene kommt
           hinzu, dass ab 2035 keine neuen PKW mit reinem Verbrennungsmotor mehr zugelassen werden
           dürfen.</p>

        <p>Die durchgezogene orange Linie zeigt den monatlich beobachteten Anteil emissionsfreier PKW
           an allen Neuzulassungen in Österreich seit Jänner 2019. Der Punkt am Ende markiert den
           zuletzt verfügbaren Monat — im <b>{latest_label}</b> waren <b>{latest_pct}</b> der
           Neuzulassungen emissionsfrei. Die beiden gestrichelten Linien sind gedachte, lineare
           Zielpfade: Sie starten beim Durchschnittswert des Jahres 2020 und steigen auf 100 %. Das
           AT-Ziel ist auf Ende 2030 ausgerichtet, das EU-Ziel auf Ende 2035.</p>

        <p>Der Anteil emissionsfreier Neuzulassungen ist seit 2019 deutlich gestiegen, liegt aber noch
           klar unter dem Pfad, der für das AT-Ziel 2030 nötig wäre. Damit die Ziele erreichbar
           bleiben, müsste sich der Hochlauf in den nächsten Jahren spürbar beschleunigen — etwa durch
           Kaufanreize, den Ausbau der Ladeinfrastruktur und ein größeres Angebot leistbarer Modelle.</p>

        <div class="methodik">
          <h3>Datenhinweise und Methodik</h3>
          <p>Datengrundlage sind die monatlichen KFZ-Neuzulassungen der Statistik Austria, gefiltert
             auf Personenkraftwagen (Klasse M1) für Gesamtösterreich. Als emissionsfrei gelten rein
             elektrische Fahrzeuge und Wasserstoff-Brennstoffzellenfahrzeuge; Hybride (Benzin/Elektro,
             Diesel/Elektro) zählen nicht dazu. Der Anteil emissionsfrei ergibt sich aus den
             emissionsfreien Zulassungen geteilt durch alle Neuzulassungen des jeweiligen Monats. Jeder
             Monatswert durchläuft vor der Darstellung automatische Plausibilitätsprüfungen. Die
             Zielpfade sind lineare Referenzlinien zur Einordnung und keine Prognose.</p>
          <table class="src-table">
            <thead>
              <tr><th>Datensatz</th><th>Datenquelle</th><th>Aktualisierung</th></tr>
            </thead>
            <tbody>
              <tr><td>PKW-Neuzulassungen nach Kraftstoffart</td><td>Statistik Austria</td><td>Monatlich</td></tr>
              <tr><td>AT-Ziel 2030</td><td>Österreichischer Mobilitätsmasterplan 2030</td><td>—</td></tr>
              <tr><td>EU-Ziel 2035</td><td>EU-Flottengrenzwerte (VO (EU) 2019/631)</td><td>—</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Bottom toggle bar -->
    <div class="toolbar">
      <div class="toolbar-left" role="tablist">
        <button class="tab" role="tab" aria-selected="true"  data-target="grafik">{ICON_CHART}Grafik</button>
        <button class="tab" role="tab" aria-selected="false" data-target="tabelle">{ICON_TABLE}Tabelle</button>
        <button class="tab" role="tab" aria-selected="false" data-target="info">{ICON_INFO}Info</button>
      </div>
      <div class="toolbar-right">
        <a title="Link kopieren">{ICON_LINK}</a>
        <a title="Einbetten">{ICON_CODE}</a>
      </div>
    </div>

  </div>

<script>
  const tabs = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('.panel');
  tabs.forEach(tab => tab.addEventListener('click', () => {{
    tabs.forEach(t => t.setAttribute('aria-selected', t === tab));
    panels.forEach(p => p.classList.toggle('active', p.id === tab.dataset.target));
  }}));
</script>
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT}  ({len(df)} rows, latest {latest['month']} = {latest_pct})")
