"""
MIRISDA — Mifzal & Riska Intelligent Sea-Dashboard
====================================================
Dashboard analisis sebaran marine debris di perairan Jawa Barat 2013-2018.
Dilengkapi visualisasi oseanografi: Wind Rose, Wave Rose, dan korelasi
faktor lingkungan terhadap akumulasi sampah laut.

REFERENSI DATASET:
    Purba, Noir; Faizal, Ibnu; Martasuganda, Marine (2021),
    "Marine Debris Dataset in Coastal Areas in Indonesia",
    Mendeley Data, V2, doi: 10.17632/r3y43cdd3x.2

INSTALL:
    pip install streamlit plotly folium streamlit-folium pandas numpy scipy openpyxl xarray

RUN:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from scipy import stats
import warnings
import math

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MIRISDA — Marine Debris Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# DARK OCEAN THEME CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
:root {
    --deep:#020b18; --mid:#051c35; --cyan:#00d4ff; --teal:#00b4a0;
    --green:#27ae60; --amber:#e67e22; --red:#c0392b;
    --text:#e8f4fd; --muted:#7fb3d3;
    --border:rgba(0,212,255,0.18); --card:rgba(5,28,53,0.88);
}
.stApp {
    background: linear-gradient(135deg,#020b18 0%,#051c35 55%,#0a2248 100%);
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text);
}
[data-testid="stSidebar"] {
    background: rgba(1,7,18,0.97) !important;
    border-right: 1px solid var(--border);
}
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stMetricValue"] { color: var(--cyan) !important; font-size: 1.7rem !important; font-weight: 600; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.7rem !important; letter-spacing: .1em; text-transform: uppercase; }
h1 { color: var(--text) !important; font-weight: 700; }
h2, h3, h4 { color: var(--cyan) !important; font-weight: 600; }
.js-plotly-plot .plotly { background: transparent !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; }
.stSelectbox > div > div { background: rgba(5,28,53,0.9) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
.stTabs [data-baseweb="tab-list"] { background: rgba(5,28,53,0.6); border-radius: 10px; border: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { color: var(--muted) !important; }
.stTabs [aria-selected="true"] { color: var(--cyan) !important; }
.insight-box {
    background: linear-gradient(135deg,rgba(0,180,160,.12),rgba(0,212,255,.08));
    border: 1px solid rgba(0,180,160,.4); border-radius: 12px;
    padding: .9rem 1.1rem; margin: .4rem 0; font-size: .85rem; line-height: 1.6;
    color: var(--text);
}
.insight-title { color: #00b4a0; font-weight: 600; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .3rem; }
.ocean-info-box {
    background: linear-gradient(135deg,rgba(0,100,180,.12),rgba(0,212,255,.06));
    border: 1px solid rgba(0,180,255,.3); border-radius: 10px;
    padding: .75rem 1rem; font-size: .78rem; line-height: 1.6; color: var(--muted);
}
.ref-box {
    background: rgba(5,28,53,0.7);
    border: 1px solid var(--border); border-radius: 10px;
    padding: .8rem 1rem; font-size: .75rem; line-height: 1.7; color: var(--muted);
}
.ref-box a { color: var(--cyan); text-decoration: none; }
.ref-box a:hover { text-decoration: underline; }
hr { border-color: var(--border) !important; }
.upload-note { font-size: .72rem; color: var(--muted); line-height: 1.5; padding: .5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER BANNER ITB
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(90deg, #1a3a8f 0%, #2a5bd7 50%, #1a3a8f 100%);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid rgba(0,212,255,0.3);
    margin-bottom: 1rem;
">
    <div style="display:flex; align-items:center; gap:14px;">
        <img src="https://upload.wikimedia.org/wikipedia/id/thumb/f/f6/Logo_Institut_Teknologi_Bandung.svg/200px-Logo_Institut_Teknologi_Bandung.svg.png"
             width="52" style="filter: brightness(1.1);">
        <div style="color:white; font-family:'Space Grotesk',sans-serif; line-height:1.4;">
            <div style="font-size:.72rem; font-weight:400; opacity:.9">PROGRAM STUDI OSEANOGRAFI</div>
            <div style="font-size:.72rem; font-weight:400; opacity:.9">FAKULTAS ILMU DAN TEKNOLOGI KEBUMIAN</div>
            <div style="font-size:.72rem; font-weight:600;">INSTITUT TEKNOLOGI BANDUNG</div>
        </div>
    </div>
    <div style="
        color:white; font-family:'Space Grotesk',sans-serif;
        text-align:right; font-weight:700; font-size:.78rem; line-height:1.5;
        background:rgba(255,255,255,0.15); padding:8px 16px; border-radius:8px;
    ">
        METODE ANALISIS DATA<br>OSEANOGRAFI (OS3201)
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
PALETTE = ["#00d4ff","#00b4a0","#4ecdc4","#27ae60","#e67e22","#c0392b","#8e44ad","#2980b9","#16a085","#d35400"]

CAT_LABELS = {
    "cat_A": "Most Likely Items",
    "cat_B": "Fishing Gear",
    "cat_C": "Packaging Materials",
    "cat_D": "Personal Hygiene",
    "cat_E": "Other Trash",
    "cat_F": "Tiny Trash (<2.5cm)",
}
CAT_COLORS = {
    "cat_A": "#00d4ff", "cat_B": "#00b4a0", "cat_C": "#27ae60",
    "cat_D": "#e67e22", "cat_E": "#c0392b", "cat_F": "#8e44ad",
}

ITEM_NAMES = {
    "A1":"Cigarette Butts","A2":"Food Wrapper","A3":"Takeout Container (Plastic)",
    "A4":"Takeout Container (Foam)","A5":"Bottle Caps (Plastic)","A6":"Bottle Caps (Metal)",
    "A7":"Lids (Plastic)","A8":"Straws/Stirrers","A9":"Fork/Knife/Spoon",
    "A10":"Beverage Bottles (Plastic)","A11":"Beverage Bottles (Glass)",
    "A12":"Beverage Cans","A13":"Grocery Bags (Plastic)","A14":"Other Plastic Bags",
    "A15":"Paper Bags","A16":"Cups & Plates (Paper)","A17":"Cups & Plates (Plastic)",
    "A18":"Cups & Plates (Foam)",
    "B1":"Fishing Buoys/Pots","B2":"Fishing Net","B3":"Rope","B4":"Fishing Line",
    "C1":"6-Pack Holders","C2":"Other Plastic Packaging","C3":"Other Plastic Bottles",
    "C4":"Strapping Bands","C5":"Tobacco Packaging",
    "D1":"Condoms","D2":"Diapers","D3":"Syringes","D4":"Tampons",
    "E1":"Appliances","E2":"Balloons","E3":"Cigar Tips","E4":"Cigarette Lighters",
    "E5":"Construction Materials","E6":"Fireworks","E7":"Tires",
    "F1":"Foam Pieces","F2":"Glass Pieces","F3":"Plastic Pieces",
}

MONTH_MAP = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
             "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
MONTHS_EN = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

OCEAN_COLS = ["wind_speed","wind_direction","wave_height","wave_direction","rainfall_mm"]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(5,28,53,0.55)",
    font=dict(family="Space Grotesk, sans-serif", color="#e8f4fd", size=11),
)


# ─────────────────────────────────────────────
# DATA LOADING — UoP DATASET
# ─────────────────────────────────────────────
@st.cache_data
def load_builtin_data() -> pd.DataFrame:
    df_raw = pd.read_excel(
        "Marine Debris-Data-UoP.xlsx",
        sheet_name="Dataset",
        header=None,
    )
    return _parse_uop_raw(df_raw)


def _parse_uop_raw(df_raw: pd.DataFrame) -> pd.DataFrame:
    data_rows = df_raw.iloc[3:].copy().reset_index(drop=True)

    def fwd_fill(col_idx):
        vals = list(data_rows[col_idx])
        last = None
        result = []
        for v in vals:
            sv = str(v).strip()
            if pd.notna(v) and sv and sv.lower() not in ["nan", "places", "lon", "lat"]:
                last = sv
            result.append(last)
        return result

    for col in [2, 3, 4, 5]:
        data_rows[col] = fwd_fill(col)

    col_map = {
        "expedition": 2, "month": 3, "year": 4, "place": 5, "lon": 6, "lat": 7,
        "A1":8,"A2":9,"A3":10,"A4":11,"A5":12,"A6":13,"A7":14,"A8":15,
        "A9":16,"A10":17,"A11":18,"A12":19,"A13":20,"A14":21,"A15":22,
        "A16":23,"A17":24,"A18":25,
        "B1":26,"B2":27,"B3":28,"B4":29,
        "C1":30,"C2":31,"C3":32,"C4":33,"C5":34,
        "D1":35,"D2":36,"D3":37,"D4":38,
        "E1":39,"E2":40,"E3":41,"E4":42,"E5":43,"E6":44,"E7":45,
        "F1":46,"F2":47,"F3":48,
        "weight":49,"distance":50,"total_items":51,
    }

    df = pd.DataFrame({name: data_rows[idx] for name, idx in col_map.items()})

    item_cols = list(ITEM_NAMES.keys())
    for c in item_cols + ["weight", "distance", "total_items", "lat", "lon", "year"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in item_cols:
        df[c] = df[c].fillna(0)

    df = df.dropna(subset=["lat", "lon"])
    df["year"] = df["year"].astype(int)
    df["expedition"] = df["expedition"].astype(str).str.strip()
    df["place"] = df["place"].astype(str).str.strip()
    df["month"] = df["month"].astype(str).str.strip()
    df["month_num"] = df["month"].map(MONTH_MAP)

    df["cat_A"] = df[[f"A{i}" for i in range(1, 19)]].sum(axis=1)
    df["cat_B"] = df[[f"B{i}" for i in range(1, 5)]].sum(axis=1)
    df["cat_C"] = df[[f"C{i}" for i in range(1, 6)]].sum(axis=1)
    df["cat_D"] = df[[f"D{i}" for i in range(1, 5)]].sum(axis=1)
    df["cat_E"] = df[[f"E{i}" for i in range(1, 8)]].sum(axis=1)
    df["cat_F"] = df[[f"F{i}" for i in range(1, 4)]].sum(axis=1)

    df["density"] = (df["total_items"] / df["distance"].replace(0, np.nan)).round(3)
    return df.reset_index(drop=True)


def parse_uploaded_file(uploaded_file) -> pd.DataFrame:
    fname = uploaded_file.name.lower()
    if fname.endswith(".csv"):
        df_raw = pd.read_csv(uploaded_file, header=None)
    else:
        try:
            df_raw = pd.read_excel(uploaded_file, sheet_name="Dataset", header=None)
        except Exception:
            df_raw = pd.read_excel(uploaded_file, sheet_name=0, header=None)
    return _parse_uop_raw(df_raw)


# ─────────────────────────────────────────────
# OCEANOGRAPHY — LOAD ERA5 NetCDF
# ─────────────────────────────────────────────
def load_era5(nc_file) -> object:
    try:
        import xarray as xr
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp:
            tmp.write(nc_file.read())
            tmp_path = tmp.name
        ds = xr.open_dataset(tmp_path)
        return ds
    except ImportError:
        st.warning("Library `xarray` belum terinstall. Jalankan: `pip install xarray`")
        return None
    except Exception as e:
        st.error(f"Gagal membaca file ERA5: {e}")
        return None


def merge_ocean_data(df: pd.DataFrame, ds) -> pd.DataFrame:
    # Hapus kolom ocean lama dulu biar tidak duplikat
    df = df.drop(columns=[c for c in OCEAN_COLS if c in df.columns], errors="ignore")

    results = []
    for _, row in df.iterrows():
        try:
            point = ds.sel(latitude=row["lat"], longitude=row["lon"], method="nearest")
            if "valid_time" in point.dims:
                month_data = point.where(
                    point["valid_time.month"] == row["month_num"], drop=True
                ).mean("valid_time")
            elif "time" in point.dims:
                month_data = point.where(
                    point["time.month"] == row["month_num"], drop=True
                ).mean("time")
            else:
                month_data = point

            def safe_float(da):
                try:
                    return float(np.array(da.values).squeeze())
                except Exception:
                    return np.nan

            u   = safe_float(month_data["u10"]) if "u10" in month_data else np.nan
            v   = safe_float(month_data["v10"]) if "v10" in month_data else np.nan
            swh = safe_float(month_data["swh"]) if "swh" in month_data else np.nan
            mwd = safe_float(month_data["mwd"]) if "mwd" in month_data else np.nan
            tp  = safe_float(month_data["tp"])  if "tp"  in month_data else np.nan
            if not np.isnan(tp):
                tp = tp * 1000

            wind_speed = round(math.sqrt(u**2 + v**2), 2) if not (np.isnan(u) or np.isnan(v)) else np.nan
            wind_dir   = round((math.degrees(math.atan2(u, v)) + 360) % 360, 1) if not (np.isnan(u) or np.isnan(v)) else np.nan

            results.append({
                "wind_speed":     wind_speed,
                "wind_direction": wind_dir,
                "wave_height":    round(swh, 2) if not np.isnan(swh) else np.nan,
                "wave_direction": round(mwd, 1) if not np.isnan(mwd) else np.nan,
                "rainfall_mm":    round(tp, 1)  if not np.isnan(tp)  else np.nan,
            })
        except Exception:
            results.append({k: np.nan for k in OCEAN_COLS})

    ocean_df = pd.DataFrame(results, index=df.index)
    return pd.concat([df, ocean_df], axis=1)


def generate_demo_ocean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Hapus kolom ocean lama dulu biar tidak duplikat
    df = df.drop(columns=[c for c in OCEAN_COLS if c in df.columns], errors="ignore")

    rng = np.random.default_rng(42)
    records = []
    for _, row in df.iterrows():
        m = row.get("month_num", 6) or 6
        if m in [11, 12, 1, 2, 3]:
            base_dir, spd_mu, wave_mu, rain_mu = 270, 6.5, 1.4, 180
        elif m in [5, 6, 7, 8, 9]:
            base_dir, spd_mu, wave_mu, rain_mu = 130, 4.8, 0.9, 35
        else:
            base_dir, spd_mu, wave_mu, rain_mu = 200, 3.5, 0.7, 90

        wind_dir = (base_dir + rng.normal(0, 25)) % 360
        wind_spd = max(0.5, rng.normal(spd_mu, 1.2))
        wave_h   = max(0.1, rng.normal(wave_mu, 0.3))
        wave_dir = (wind_dir + rng.normal(15, 20)) % 360
        rain     = max(0, rng.normal(rain_mu, rain_mu * 0.4))

        records.append({
            "wind_speed":     round(wind_spd, 2),
            "wind_direction": round(wind_dir, 1),
            "wave_height":    round(wave_h, 2),
            "wave_direction": round(wave_dir, 1),
            "rainfall_mm":    round(rain, 1),
        })

    ocean_df = pd.DataFrame(records, index=df.index)
    return pd.concat([df, ocean_df], axis=1)


# ─────────────────────────────────────────────
# WIND / WAVE ROSE
# ─────────────────────────────────────────────
def build_wind_rose(df: pd.DataFrame, var_dir: str, var_speed: str, title: str) -> go.Figure:
    valid = df.dropna(subset=[var_dir, var_speed]).copy()
    if len(valid) < 3:
        fig = go.Figure()
        fig.add_annotation(text="Data tidak cukup", x=0.5, y=0.5, showarrow=False,
                           font=dict(color="#7fb3d3"))
        fig.update_layout(**CHART_LAYOUT, height=340, title=title)
        return fig

    DIR_LABELS = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
                  "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    n_sectors = 16
    sector_size = 360 / n_sectors

    speed_bins  = [0, 2, 4, 6, 8, 100]
    speed_names = ["0-2 m/s","2-4 m/s","4-6 m/s","6-8 m/s",">8 m/s"]
    speed_colors = ["#00b4a0","#00d4ff","#f39c12","#e67e22","#c0392b"]

    # Pastikan kolom adalah Series 1D
    dir_series   = valid[var_dir].astype(float)
    speed_series = valid[var_speed].astype(float)

    valid["sector"]  = ((dir_series + sector_size / 2) % 360 / sector_size).astype(int) % n_sectors
    valid["spd_cat"] = pd.cut(speed_series, bins=speed_bins, labels=speed_names, right=False)

    traces = []
    for name, color in zip(speed_names, speed_colors):
        sub = valid[valid["spd_cat"] == name]
        counts = sub.groupby("sector").size().reindex(range(n_sectors), fill_value=0)
        pct = (counts / len(valid) * 100).round(1)
        traces.append(go.Barpolar(
            r=pct.values,
            theta=[s * sector_size for s in range(n_sectors)],
            name=name,
            marker_color=color,
            marker_line_color="rgba(0,0,0,0.3)",
            marker_line_width=0.5,
            opacity=0.85,
            width=sector_size * 0.9,
            hovertemplate=f"<b>{name}</b><br>Arah: %{{theta}}°<br>Frekuensi: %{{r:.1f}}%<extra></extra>",
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,28,53,0.55)",
        font=dict(family="Space Grotesk, sans-serif", color="#e8f4fd", size=10),
        title=dict(text=title, font=dict(color="#00d4ff", size=13), x=0.5),
        polar=dict(
            bgcolor="rgba(5,28,53,0.7)",
            radialaxis=dict(
                ticksuffix="%",
                tickfont=dict(color="#7fb3d3", size=9),
                gridcolor="rgba(0,212,255,0.15)",
                linecolor="rgba(0,212,255,0.2)",
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=[i * sector_size for i in range(n_sectors)],
                ticktext=DIR_LABELS,
                tickfont=dict(color="#e8f4fd", size=9),
                gridcolor="rgba(0,212,255,0.15)",
                linecolor="rgba(0,212,255,0.2)",
                direction="clockwise",
                rotation=90,
            ),
        ),
        legend=dict(
            bgcolor="rgba(5,28,53,0.8)",
            bordercolor="rgba(0,212,255,0.2)",
            borderwidth=1,
            font=dict(size=9, color="#e8f4fd"),
            orientation="v",
            x=1.05,
        ),
        height=340,
        margin=dict(l=20, r=100, t=50, b=20),
    )
    return fig


# ─────────────────────────────────────────────
# MAP
# ─────────────────────────────────────────────
def density_color(density: float, max_d: float) -> str:
    t = min(1.0, density / max(max_d, 0.001))
    if t >= 0.66:
        return "#c0392b"
    if t >= 0.33:
        return "#e67e22"
    return "#27ae60"


def build_map(df: pd.DataFrame, show_points: bool, show_circles: bool, show_labels: bool) -> folium.Map:
    fmap = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=6,
        tiles="CartoDB DarkMatter",
        prefer_canvas=True,
    )

    loc_agg = (
        df.groupby("place")
        .agg(lat=("lat","mean"), lon=("lon","mean"),
             avg_density=("density","mean"),
             total_items=("total_items","sum"),
             total_weight=("weight","sum"),
             n_surveys=("place","count"))
        .reset_index()
    )
    max_d = loc_agg["avg_density"].max()

    for _, row in loc_agg.iterrows():
        col = density_color(row["avg_density"], max_d)
        status = ("🔴 High Risk"   if row["avg_density"] >= max_d * 0.66 else
                  "🟡 Medium Risk" if row["avg_density"] >= max_d * 0.33 else "🟢 Low Risk")

        if show_circles:
            radius = 6 + int((row["avg_density"] / max_d) * 22)
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=radius, color=col, weight=2,
                fill=True, fill_color=col, fill_opacity=0.22,
            ).add_to(fmap)

        if show_points:
            icon_html = (f'<div style="width:14px;height:14px;background:{col};'
                         f'border:2px solid rgba(255,255,255,.55);border-radius:50%;'
                         f'box-shadow:0 0 8px {col}88"></div>')
            icon = folium.DivIcon(html=icon_html, icon_size=(14,14), icon_anchor=(7,7))
            popup_html = (
                f'<div style="font-family:Space Grotesk,sans-serif;background:#051c35;'
                f'color:#e8f4fd;padding:12px 15px;border-radius:10px;'
                f'min-width:210px;border:1px solid rgba(0,212,255,.3);font-size:13px">'
                f'<b style="color:#00d4ff;font-size:14px">{row["place"]}</b><br><br>'
                f'🌊 Avg Density: <b>{row["avg_density"]:.2f}</b> items/m<br>'
                f'🗑️ Total Items: <b>{int(row["total_items"]):,}</b><br>'
                f'⚖️ Total Weight: <b>{row["total_weight"]:.1f} kg</b><br>'
                f'📍 Surveys: <b>{int(row["n_surveys"])}</b><br><br>{status}</div>'
            )
            folium.Marker(
                location=[row["lat"], row["lon"]],
                icon=icon,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=row["place"],
            ).add_to(fmap)

        if show_labels:
            folium.Tooltip(
                text=(f'<div style="background:rgba(2,11,24,.88);color:#e8f4fd;'
                      f'font-size:10px;padding:2px 7px;border-radius:5px;'
                      f'border:1px solid rgba(0,212,255,.25);'
                      f'font-family:Space Grotesk,sans-serif">{row["place"][:22]}</div>'),
                permanent=True,
            ).add_to(folium.Marker(
                location=[row["lat"], row["lon"]],
                icon=folium.DivIcon(html="", icon_size=(0,0)),
            ).add_to(fmap))

    pts = [[r["lat"], r["lon"]] for _, r in loc_agg.iterrows()]
    if pts:
        fmap.fit_bounds(pts, max_zoom=9)

    legend_html = """
    <div style="position:fixed;bottom:24px;left:24px;z-index:9999;
                background:rgba(2,11,24,.93);border:1px solid rgba(0,212,255,.3);
                border-radius:10px;padding:10px 14px;
                font-family:'Space Grotesk',sans-serif;color:#e8f4fd;font-size:11px">
      <div style="color:#00d4ff;font-weight:600;letter-spacing:.1em;margin-bottom:7px;font-size:10px">DENSITAS DEBRIS</div>
      <div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="width:11px;height:11px;background:#27ae60;border-radius:3px;display:inline-block"></span>Rendah
      </div>
      <div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="width:11px;height:11px;background:#e67e22;border-radius:3px;display:inline-block"></span>Sedang
      </div>
      <div style="display:flex;align-items:center;gap:7px;margin:3px 0">
        <span style="width:11px;height:11px;background:#c0392b;border-radius:3px;display:inline-block"></span>Tinggi
      </div>
    </div>"""
    fmap.get_root().html.add_child(folium.Element(legend_html))
    return fmap


# ─────────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────────
def generate_insights(df: pd.DataFrame) -> list:
    insights = []

    by_month = df.groupby("month_num")["total_items"].mean()
    if not by_month.empty:
        peak_m = int(by_month.idxmax())
        insights.append(
            f'<div class="insight-title">📅 Bulan Puncak Survei</div>'
            f'<b>{MONTHS_EN.get(peak_m,"N/A")}</b> mencatat rata-rata debris tertinggi '
            f'({by_month[peak_m]:.0f} item/survei), menunjukkan pola musiman akumulasi sampah.'
        )

    valid = df.dropna(subset=["density","weight"])
    if len(valid) >= 5:
        r, _ = stats.pearsonr(valid["density"], valid["weight"])
        direction = "positif kuat" if r > 0.5 else "positif sedang" if r > 0.2 else "lemah"
        insights.append(
            f'<div class="insight-title">🔗 Korelasi Densitas–Berat</div>'
            f'Densitas debris berkorelasi <b>{direction}</b> dengan berat (r = {r:.2f}). '
            f'{"Item lebih berat menumpuk di area padat." if r > 0.3 else "Komposisi debris bervariasi antar lokasi."}'
        )

    item_totals = {name: df[code].sum() for code, name in ITEM_NAMES.items()}
    top_item = max(item_totals, key=item_totals.get)
    total_all = df["total_items"].sum()
    top_pct = (item_totals[top_item] / total_all * 100) if total_all > 0 else 0
    insights.append(
        f'<div class="insight-title">🗑️ Jenis Debris Dominan</div>'
        f'<b>{top_item}</b> adalah jenis paling banyak ditemukan, '
        f'mewakili <b>{top_pct:.1f}%</b> dari semua item yang tercatat.'
    )

    loc_avg = df.groupby("place")["density"].mean()
    if not loc_avg.empty:
        worst = loc_avg.idxmax()
        insights.append(
            f'<div class="insight-title">🔴 Lokasi Risiko Tertinggi</div>'
            f'<b>{worst[:30]}</b> memiliki rata-rata densitas tertinggi '
            f'({loc_avg[worst]:.2f} item/m). Prioritas intervensi segera.'
        )

    n_surveys = len(df)
    n_locs = df["place"].nunique()
    total_kg = df["weight"].sum()
    insights.append(
        f'<div class="insight-title">📊 Ringkasan Survei</div>'
        f'<b>{n_surveys}</b> survei di <b>{n_locs}</b> lokasi mengumpulkan '
        f'<b>{int(total_all):,}</b> item debris, total berat <b>{total_kg:.1f} kg</b>.'
    )

    return [f'<div class="insight-box">{ins}</div>' for ins in insights]


def generate_ocean_insights(df: pd.DataFrame) -> list:
    insights = []
    if not all(c in df.columns for c in ["wind_speed","wind_direction","wave_height","rainfall_mm"]):
        return []

    valid = df.dropna(subset=["density","wind_speed"])
    if len(valid) >= 5:
        r_wind, _ = stats.pearsonr(valid["wind_speed"], valid["density"])
        insights.append(
            f'<div class="insight-title">💨 Angin vs Debris</div>'
            f'Kecepatan angin berkorelasi <b>r = {r_wind:.2f}</b> dengan densitas debris. '
            f'{"Lokasi berangin kencang cenderung mengakumulasi lebih banyak debris." if r_wind > 0.2 else "Pengaruh angin terhadap akumulasi debris relatif kecil di dataset ini."}'
        )

    valid2 = df.dropna(subset=["density","wave_height"])
    if len(valid2) >= 5:
        r_wave, _ = stats.pearsonr(valid2["wave_height"], valid2["density"])
        insights.append(
            f'<div class="insight-title">🌊 Gelombang vs Debris</div>'
            f'Tinggi gelombang berkorelasi <b>r = {r_wave:.2f}</b> dengan densitas debris. '
            f'{"Gelombang tinggi mendorong debris ke pantai lebih intensif." if r_wave > 0.2 else "Distribusi debris tidak terlalu dipengaruhi tinggi gelombang secara langsung."}'
        )

    valid3 = df.dropna(subset=["wind_direction"])
    if len(valid3) >= 5:
        barat = len(valid3[(valid3["wind_direction"] >= 225) & (valid3["wind_direction"] <= 315)])
        timur = len(valid3[(valid3["wind_direction"] >= 45)  & (valid3["wind_direction"] <= 135)])
        dom_musim = "Musim Barat (angin dari barat)" if barat >= timur else "Musim Timur (angin dari tenggara)"
        insights.append(
            f'<div class="insight-title">🧭 Musim Dominan</div>'
            f'Dari {len(valid3)} survei, kondisi <b>{dom_musim}</b> lebih dominan. '
            f'Musim barat umumnya membawa lebih banyak debris ke pesisir barat Jawa.'
        )

    return [f'<div class="insight-box">{ins}</div>' for ins in insights]


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
def main():
    # ── SESSION STATE ──────────────────────────────────────────
    if "df" not in st.session_state:
        try:
            st.session_state.df = load_builtin_data()
            st.session_state.dataset_name = "UoP Dataset (Built-in)"
        except FileNotFoundError:
            st.error(
                "⚠️ File `Marine Debris-Data-UoP.xlsx` tidak ditemukan.\n\n"
                "Letakkan file tersebut di folder yang sama dengan script ini, "
                "atau upload melalui sidebar."
            )
            st.session_state.df = pd.DataFrame()
            st.session_state.dataset_name = "No data"

    if "ocean_data_loaded" not in st.session_state:
        st.session_state.ocean_data_loaded = False
    if "use_demo_ocean" not in st.session_state:
        st.session_state.use_demo_ocean = False

    df_full = st.session_state.df

    # ── SIDEBAR ────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:.8rem 0 .5rem'>
          <div style='font-size:2rem'>🌊</div>
          <div style='color:#00d4ff;font-weight:700;font-size:1rem;letter-spacing:.03em;line-height:1.3'>
            Mifzal & Riska Intelligent<br>Sea-Dashboard
          </div>
          <div style='color:#00b4a0;font-weight:600;font-size:.75rem;margin-top:3px'>MIRISDA</div>
          <div style='color:#7fb3d3;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;margin-top:4px'>
            Sebaran Marine Debris<br>Perairan Jawa Barat 2013–2018
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Upload Dataset Debris ──
        st.markdown("### 📂 Upload Dataset Debris")
        uploaded = st.file_uploader(
            "Pilih file .xlsx atau .csv",
            type=["xlsx","xls","csv"],
            label_visibility="collapsed",
            key="upload_debris",
        )
        if uploaded is not None:
            try:
                with st.spinner("Membaca file..."):
                    new_df = parse_uploaded_file(uploaded)
                if len(new_df) < 3:
                    st.error(f"Hanya {len(new_df)} baris valid. Periksa format file.")
                else:
                    st.session_state.df = new_df
                    st.session_state.dataset_name = uploaded.name
                    st.session_state.ocean_data_loaded = False
                    df_full = new_df
                    st.success(f"✅ {len(new_df)} catatan dari {uploaded.name}")
            except Exception as e:
                st.error(f"❌ Gagal membaca: {str(e)[:200]}")

        st.markdown(
            '<div class="upload-note">Format: sama dengan dataset UoP<br>'
            '(sheet Dataset, kolom A1–F3, Weight, Distance, Total Items)</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Upload ERA5 ──
        st.markdown("### 🌬️ Upload Data Oseanografi (ERA5)")
        uploaded_era5 = st.file_uploader(
            "Pilih file .nc (NetCDF ERA5)",
            type=["nc"],
            label_visibility="collapsed",
            key="upload_era5",
        )
        if uploaded_era5 is not None:
            if not st.session_state.ocean_data_loaded:
                with st.spinner("Memuat data ERA5 & mencocokkan koordinat..."):
                    ds = load_era5(uploaded_era5)
                    if ds is not None and not df_full.empty:
                        df_with_ocean = merge_ocean_data(df_full, ds)
                        st.session_state.df = df_with_ocean
                        df_full = df_with_ocean
                        st.session_state.ocean_data_loaded = True
                        st.session_state.use_demo_ocean = False
                        st.success("✅ Data oseanografi ERA5 berhasil dimuat!")
            else:
                st.success("✅ Data ERA5 sudah dimuat.")

        # Demo toggle
        if not st.session_state.ocean_data_loaded:
            use_demo = st.toggle(
                "Gunakan data oseanografi simulasi (demo)",
                value=st.session_state.use_demo_ocean,
            )
            if use_demo != st.session_state.use_demo_ocean:
                st.session_state.use_demo_ocean = use_demo
                if use_demo and not df_full.empty:
                    df_with_demo = generate_demo_ocean_data(df_full)
                    st.session_state.df = df_with_demo
                    df_full = df_with_demo
                elif not use_demo:
                    st.session_state.df = df_full.drop(
                        columns=[c for c in OCEAN_COLS if c in df_full.columns], errors="ignore"
                    )
                    df_full = st.session_state.df

        st.markdown(
            '<div class="upload-note">Download ERA5 dari:<br>'
            '<b>cds.climate.copernicus.eu</b><br>'
            'Variabel: u10, v10, swh, mwd, tp<br>'
            'Area: Indonesia (6°N–11°S, 95°E–141°E)</div>',
            unsafe_allow_html=True,
        )

        if df_full.empty:
            st.error("DataFrame kosong! File Excel tidak terbaca.")
            st.stop()

        st.divider()

        # ── Filters ──
        st.markdown("### 📅 Rentang Tahun")
        yrs = sorted(df_full["year"].dropna().unique().astype(int))
        if len(yrs) >= 2:
            y_range = st.slider("Tahun", min_value=yrs[0], max_value=yrs[-1],
                                value=(yrs[0], yrs[-1]), label_visibility="collapsed")
        else:
            y_range = (yrs[0], yrs[0])

        st.markdown("### 📍 Lokasi")
        places = sorted(df_full["place"].dropna().unique())
        sel_place = st.selectbox("Lokasi", ["Semua Lokasi"] + places,
                                 label_visibility="collapsed")

        st.markdown("### 🔬 Ekspedisi")
        exps = sorted(df_full["expedition"].dropna().unique())
        sel_exp = st.selectbox("Ekspedisi", ["Semua Ekspedisi"] + exps,
                               label_visibility="collapsed")

        st.markdown("### 🗑️ Kategori Debris")
        cat_opts = {v: k for k, v in CAT_LABELS.items()}
        sel_cat_label = st.selectbox(
            "Kategori", ["Semua Kategori"] + list(CAT_LABELS.values()),
            label_visibility="collapsed",
        )

        st.markdown("### 🌐 Overlay Peta")
        show_points  = st.toggle("Titik survei",       value=True)
        show_circles = st.toggle("Lingkaran densitas", value=True)
        show_labels  = st.toggle("Label lokasi",       value=True)

        st.divider()
        st.markdown(
            f'<div style="font-size:.63rem;color:#7fb3d3;text-align:center;line-height:1.7">'
            f'Dataset: {st.session_state.get("dataset_name","UoP")}<br>'
            f'Perairan Indonesia · 2013–2018<br>'
            f'{"🌬️ + Data Oseanografi" if st.session_state.ocean_data_loaded or st.session_state.use_demo_ocean else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── APPLY FILTERS ──────────────────────────────────────────
    df_full = st.session_state.df
    df = df_full.copy()
    df = df[df["year"].between(y_range[0], y_range[1])]
    if sel_place != "Semua Lokasi":
        df = df[df["place"] == sel_place]
    if sel_exp != "Semua Ekspedisi":
        df = df[df["expedition"] == sel_exp]
    if sel_cat_label != "Semua Kategori":
        sel_cat_col = cat_opts[sel_cat_label]
        df = df[df[sel_cat_col] > 0]

    has_ocean = all(c in df.columns for c in ["wind_speed","wind_direction","wave_height"])

    if df.empty:
        st.warning("⚠️ Tidak ada data yang cocok dengan filter ini.")
        return

    # ── HEADER ─────────────────────────────────────────────────
    st.markdown("""
    <div style='padding:.3rem 0 .6rem'>
      <h1 style='font-size:1.55rem;margin:0;background:linear-gradient(90deg,#00d4ff,#00b4a0);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
        🌊 Marine Debris Intelligence Dashboard
      </h1>
      <p style='color:#7fb3d3;font-size:.8rem;margin:.2rem 0 .1rem'>
        Analisis sebaran sampah pesisir — Perairan Pantai Jawa Barat ·
        Dataset University of Portsmouth
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ────────────────────────────────────────────────────
    total_items   = int(df["total_items"].sum())
    avg_density   = df["density"].mean()
    total_weight  = df["weight"].sum()
    n_sites       = df["place"].nunique()
    n_expeditions = df["expedition"].nunique()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🗑️ Total Item Debris",    f"{total_items:,}")
    k2.metric("📏 Avg Densitas (item/m)", f"{avg_density:.2f}")
    k3.metric("⚖️ Total Berat (kg)",      f"{total_weight:.1f}")
    k4.metric("📍 Lokasi Survei",         f"{n_sites}")
    k5.metric("🔭 Ekspedisi",             f"{n_expeditions}")

    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

    # ── TABS ───────────────────────────────────────────────────
    tab_debris, tab_ocean = st.tabs(["📊 Analisis Debris", "🌬️ Oseanografi"])

    # ══════════════════════════════════════════
    # TAB 1 — ANALISIS DEBRIS
    # ══════════════════════════════════════════
    with tab_debris:
        col_map, col_charts = st.columns([2, 1], gap="medium")

        with col_map:
            st.markdown("#### 🗺️ Peta Lokasi Survei — Densitas & Distribusi Debris")
            fmap = build_map(df, show_points, show_circles, show_labels)
            st_folium(fmap, width="100%", height=460, returned_objects=[])

        with col_charts:
            st.markdown("#### 🥧 Debris per Kategori")
            cat_vals = {CAT_LABELS[c]: df[c].sum() for c in CAT_LABELS}
            fig_pie = go.Figure(go.Pie(
                labels=list(cat_vals.keys()),
                values=list(cat_vals.values()),
                hole=0.48,
                marker=dict(colors=list(CAT_COLORS.values()),
                            line=dict(color="#051c35", width=2)),
                textinfo="percent",
                textfont=dict(size=11, color="#ffffff"),
                hovertemplate="<b>%{label}</b><br>%{value:,} items (%{percent})<extra></extra>",
            ))
            fig_pie.update_layout(
                **CHART_LAYOUT, height=250,
                margin=dict(l=10, r=10, t=10, b=80),
                showlegend=True,
                legend=dict(
                    font=dict(size=10, color="#e8f4fd"),
                    x=0.5, xanchor="center",
                    y=-0.25, orientation="h",
                    bgcolor="rgba(0,0,0,0)",
                )
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("#### 📊 Top 10 Jenis Debris")
            item_totals_df = pd.DataFrame([
                {"item": name[:28], "count": int(df[code].sum())}
                for code, name in ITEM_NAMES.items()
            ]).sort_values("count", ascending=False).head(10)

            fig_bar = go.Figure(go.Bar(
                x=item_totals_df["count"],
                y=item_totals_df["item"],
                orientation="h",
                marker=dict(
                    color=item_totals_df["count"],
                    colorscale=[[0,"#00b4a0"],[0.5,"#00d4ff"],[1.0,"#c0392b"]],
                    showscale=False,
                ),
                text=item_totals_df["count"].apply(lambda v: f"{v:,}"),
                textposition="outside",
                textfont=dict(color="#e8f4fd", size=10),
                hovertemplate="<b>%{y}</b>: %{x:,} items<extra></extra>",
            ))
            fig_bar.update_layout(
                **CHART_LAYOUT, height=300,
                margin=dict(l=10, r=70, t=10, b=10),
                xaxis=dict(gridcolor="rgba(0,212,255,0.1)", zerolinecolor="rgba(0,212,255,0.2)"),
                yaxis=dict(tickfont=dict(size=10, color="#e8f4fd"), gridcolor="rgba(0,212,255,0.1)"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        col_ts, col_tbl, col_corr = st.columns([1.35, 1.1, 1.3], gap="medium")

        with col_ts:
            st.markdown("#### 📈 Tren Tahunan Debris & Berat")
            by_year = (df.groupby("year")
                         .agg(total_items=("total_items","sum"),
                              total_weight=("weight","sum"))
                         .reset_index().sort_values("year"))
            fig_ts = make_subplots(specs=[[{"secondary_y": True}]])
            fig_ts.add_trace(go.Bar(
                x=by_year["year"], y=by_year["total_items"],
                name="Total Item", marker_color="rgba(0,180,160,.6)",
                marker_line_color="#00b4a0", marker_line_width=1,
            ), secondary_y=False)
            fig_ts.add_trace(go.Scatter(
                x=by_year["year"], y=by_year["total_weight"].round(1),
                name="Berat (kg)", mode="lines+markers",
                line=dict(color="#e67e22", width=2),
                marker=dict(size=6, color="#e67e22"),
            ), secondary_y=True)
            fig_ts.update_layout(**CHART_LAYOUT, height=270,
                                 legend=dict(orientation="h", y=1.1, x=0, font=dict(size=10)))
            fig_ts.update_yaxes(title_text="Total Item", secondary_y=False,
                                gridcolor="rgba(0,212,255,0.1)", title_font_color="#7fb3d3")
            fig_ts.update_yaxes(title_text="Berat (kg)", secondary_y=True,
                                gridcolor=None, title_font_color="#7fb3d3")
            st.plotly_chart(fig_ts, use_container_width=True)

        with col_tbl:
            st.markdown("#### 🔥 Hotspot per Lokasi")
            hotspot = (df.groupby("place")
                         .agg(avg_density=("density","mean"),
                              total_items=("total_items","sum"),
                              n=("place","count"))
                         .reset_index()
                         .sort_values("avg_density", ascending=False)
                         .head(15))
            p33 = hotspot["avg_density"].quantile(0.33)
            p66 = hotspot["avg_density"].quantile(0.66)
            hotspot["Status"] = hotspot["avg_density"].apply(
                lambda v: "🔴 Tinggi" if v >= p66 else ("🟡 Sedang" if v >= p33 else "🟢 Rendah")
            )
            hotspot["Densitas"] = hotspot["avg_density"].round(2)
            hotspot["Lokasi"] = hotspot["place"].str[:22]
            st.dataframe(
                hotspot[["Lokasi","Densitas","Status"]],
                use_container_width=True, height=270, hide_index=True,
                column_config={"Densitas": st.column_config.ProgressColumn(
                    "Densitas (item/m)", min_value=0,
                    max_value=float(hotspot["Densitas"].max()), format="%.2f")},
            )

        with col_corr:
            st.markdown("#### 🔬 Korelasi Densitas vs Berat")
            valid_corr = df.dropna(subset=["density","weight"])
            valid_corr = valid_corr[valid_corr["density"] > 0]
            if len(valid_corr) >= 5:
                m_reg, b_reg, r_val, _, _ = stats.linregress(
                    valid_corr["density"], valid_corr["weight"])
                x_range = np.linspace(valid_corr["density"].min(),
                                       valid_corr["density"].max(), 100)
                fig_sc = go.Figure()
                fig_sc.add_trace(go.Scatter(
                    x=valid_corr["density"], y=valid_corr["weight"],
                    mode="markers",
                    marker=dict(color=valid_corr["density"],
                                colorscale=[[0,"#27ae60"],[0.5,"#e67e22"],[1,"#c0392b"]],
                                size=7, opacity=0.75),
                    name="Survei",
                    customdata=valid_corr[["place"]].values,
                    hovertemplate="%{customdata[0]}<br>Densitas: %{x:.2f}<br>Berat: %{y:.1f} kg<extra></extra>",
                ))
                fig_sc.add_trace(go.Scatter(
                    x=x_range, y=m_reg * x_range + b_reg, mode="lines",
                    line=dict(color="#00d4ff", width=2, dash="dash"),
                    name=f"Trend (r={r_val:.2f})",
                ))
                fig_sc.update_layout(**CHART_LAYOUT, height=270,
                                     xaxis_title="Densitas (item/m)", yaxis_title="Berat (kg)",
                                     legend=dict(orientation="h", y=1.1, x=0, font=dict(size=10)))
                st.plotly_chart(fig_sc, use_container_width=True)
            else:
                st.info("Data tidak cukup untuk menghitung korelasi.")

        st.divider()

        st.markdown("#### 🧠 Insight Otomatis")
        insights = generate_insights(df)
        cols_ins = st.columns(len(insights))
        for col, ins in zip(cols_ins, insights):
            with col:
                st.markdown(ins, unsafe_allow_html=True)

        st.markdown("#### 📆 Pola Musiman — Item/Survei per Bulan × Lokasi")
        seasonal = df.groupby(["place","month_num"])["total_items"].mean().reset_index()
        seasonal_pivot = seasonal.pivot(index="place", columns="month_num",
                                         values="total_items").fillna(0)
        seasonal_pivot.columns = [MONTHS_EN.get(int(c), str(c)) for c in seasonal_pivot.columns]
        fig_heat = go.Figure(go.Heatmap(
            z=seasonal_pivot.values,
            x=list(seasonal_pivot.columns),
            y=[loc[:25] for loc in seasonal_pivot.index],
            colorscale=[[0,"#003300"],[0.35,"#006600"],[0.65,"#ffcc00"],[1.0,"#cc0000"]],
            hovertemplate="<b>%{y}</b><br>Bulan: %{x}<br>Avg items/survei: %{z:.0f}<extra></extra>",
            colorbar=dict(title=dict(text="items/survei", font=dict(color="#e8f4fd")),
                          tickfont=dict(color="#e8f4fd")),
        ))
        fig_heat.update_layout(
            **CHART_LAYOUT,
            height=max(300, len(seasonal_pivot) * 22 + 60),
            xaxis=dict(title="Bulan"),
            yaxis=dict(title="Lokasi", autorange="reversed"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ══════════════════════════════════════════
    # TAB 2 — OSEANOGRAFI
    # ══════════════════════════════════════════
    with tab_ocean:
        if not has_ocean:
            st.markdown("""
            <div class="ocean-info-box">
              <b style="color:#00d4ff">🌬️ Data oseanografi belum dimuat</b><br><br>
              Ada dua cara untuk mengaktifkan tab ini:<br><br>
              <b>1. Upload file ERA5 (.nc)</b> — download dari
              <a href="https://cds.climate.copernicus.eu" target="_blank"
                 style="color:#00d4ff">cds.climate.copernicus.eu</a><br>
              &nbsp;&nbsp;&nbsp;Variabel: <code>u10</code>, <code>v10</code>,
              <code>swh</code>, <code>mwd</code>, <code>tp</code><br><br>
              <b>2. Aktifkan mode demo</b> — toggle "Gunakan data oseanografi simulasi"
              di sidebar.
            </div>
            """, unsafe_allow_html=True)
        else:
            is_demo = st.session_state.use_demo_ocean and not st.session_state.ocean_data_loaded
            if is_demo:
                st.info("🔬 Menampilkan data oseanografi **simulasi** (demo). Upload file ERA5 untuk data aktual.")

            col_wr, col_wv = st.columns(2, gap="medium")
            with col_wr:
                st.markdown("#### 💨 Wind Rose — Arah & Kecepatan Angin")
                fig_wind = build_wind_rose(df, "wind_direction", "wind_speed", "Distribusi Angin (m/s)")
                st.plotly_chart(fig_wind, use_container_width=True)

            with col_wv:
                st.markdown("#### 🌊 Wave Rose — Arah & Tinggi Gelombang")
                fig_wave = build_wind_rose(df, "wave_direction", "wave_height", "Distribusi Gelombang (m)")
                st.plotly_chart(fig_wave, use_container_width=True)

            st.divider()

            st.markdown("#### 🔬 Korelasi Debris × Faktor Oseanografi")
            col_w1, col_w2, col_w3 = st.columns(3, gap="medium")
            ocean_factors = [
                ("wind_speed",  "Kecepatan Angin (m/s)", "#00d4ff"),
                ("wave_height", "Tinggi Gelombang (m)",  "#00b4a0"),
                ("rainfall_mm", "Curah Hujan (mm)",      "#4ecdc4"),
            ]
            for col_widget, (factor, label, color) in zip([col_w1, col_w2, col_w3], ocean_factors):
                with col_widget:
                    v = df.dropna(subset=["density", factor])
                    v = v[v["density"] > 0]
                    if len(v) >= 5:
                        m_r, b_r, r_v, _, _ = stats.linregress(v[factor], v["density"])
                        x_r = np.linspace(v[factor].min(), v[factor].max(), 80)
                        fig_c = go.Figure()
                        fig_c.add_trace(go.Scatter(
                            x=v[factor], y=v["density"], mode="markers",
                            marker=dict(color=color, size=6, opacity=0.65),
                            name="Survei",
                            hovertemplate=f"{label}: %{{x:.2f}}<br>Densitas: %{{y:.2f}}<extra></extra>",
                        ))
                        fig_c.add_trace(go.Scatter(
                            x=x_r, y=m_r * x_r + b_r, mode="lines",
                            line=dict(color="#ffffff", width=1.5, dash="dot"),
                            name=f"r={r_v:.2f}",
                        ))
                        fig_c.update_layout(
                            **CHART_LAYOUT, height=240,
                            xaxis_title=label, yaxis_title="Densitas (item/m)",
                            margin=dict(l=40,r=10,t=30,b=40),
                            legend=dict(orientation="h", y=1.1, x=0, font=dict(size=9)),
                            title=dict(text=f"Debris × {label.split('(')[0].strip()}",
                                       font=dict(color="#00d4ff", size=11), x=0.5),
                        )
                        st.plotly_chart(fig_c, use_container_width=True)
                    else:
                        st.info(f"Data {label} tidak cukup.")

            st.divider()

            st.markdown("#### 📈 Tren Bulanan — Debris vs Kondisi Oseanografi")
            by_mon = (df.groupby("month_num")
                        .agg(avg_items=("total_items","mean"),
                             avg_wind=("wind_speed","mean"),
                             avg_wave=("wave_height","mean"),
                             avg_rain=("rainfall_mm","mean"))
                        .reset_index().sort_values("month_num"))
            by_mon["month_name"] = by_mon["month_num"].map(MONTHS_EN)

            fig_mon = make_subplots(specs=[[{"secondary_y": True}]])
            fig_mon.add_trace(go.Bar(
                x=by_mon["month_name"], y=by_mon["avg_items"].round(1),
                name="Avg Item/Survei", marker_color="rgba(0,180,160,.6)",
                marker_line_color="#00b4a0", marker_line_width=1,
            ), secondary_y=False)
            fig_mon.add_trace(go.Scatter(
                x=by_mon["month_name"], y=by_mon["avg_wind"].round(2),
                name="Angin (m/s)", mode="lines+markers",
                line=dict(color="#00d4ff", width=2), marker=dict(size=5),
            ), secondary_y=True)
            fig_mon.add_trace(go.Scatter(
                x=by_mon["month_name"], y=by_mon["avg_wave"].round(2),
                name="Gelombang (m)", mode="lines+markers",
                line=dict(color="#e67e22", width=2, dash="dot"), marker=dict(size=5),
            ), secondary_y=True)
            fig_mon.update_layout(
                **CHART_LAYOUT, height=300,
                legend=dict(orientation="h", y=1.1, x=0, font=dict(size=10)),
            )
            fig_mon.update_yaxes(title_text="Avg Item/Survei", secondary_y=False,
                                 gridcolor="rgba(0,212,255,0.1)", title_font_color="#7fb3d3")
            fig_mon.update_yaxes(title_text="Angin / Gelombang", secondary_y=True,
                                 gridcolor=None, title_font_color="#7fb3d3")
            st.plotly_chart(fig_mon, use_container_width=True)

            st.divider()

            ocean_ins = generate_ocean_insights(df)
            if ocean_ins:
                st.markdown("#### 🧠 Insight Oseanografi")
                cols_oi = st.columns(len(ocean_ins))
                for col_oi, ins in zip(cols_oi, ocean_ins):
                    with col_oi:
                        st.markdown(ins, unsafe_allow_html=True)

    # ── REFERENSI ───────────────────────────────────────────────
    st.divider()
    st.markdown("""
    <div class="ref-box">
      <b style="color:#00d4ff;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase">
        📚 Referensi Dataset
      </b><br><br>
      Purba, Noir; Faizal, Ibnu; Martasuganda, Marine (2021).
      <i>Marine Debris Dataset in Coastal Areas in Indonesia</i>.
      Mendeley Data, V2.
      DOI: <a href="https://doi.org/10.17632/r3y43cdd3x.2" target="_blank">
      10.17632/r3y43cdd3x.2</a><br><br>
      <span style="font-size:.7rem;opacity:.75">
        Data oseanografi (opsional): ERA5 Reanalysis · Copernicus Climate Change Service (C3S) ·
        <a href="https://cds.climate.copernicus.eu" target="_blank"
           style="color:#7fb3d3">cds.climate.copernicus.eu</a>
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-size:.62rem;color:#7fb3d3;text-align:center;opacity:.6;margin-top:.5rem">'
        f'MIRISDA · Mifzal & Riska Intelligent Sea-Dashboard · '
        f'{len(df_full)} catatan · {df_full["place"].nunique()} lokasi · 2013–2018'
        f'</p>',
        unsafe_allow_html=True,
    )


main()