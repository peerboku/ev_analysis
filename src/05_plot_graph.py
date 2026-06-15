from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter
from matplotlib.dates import DateFormatter, YearLocator, MonthLocator

import matplotlib.dates as mdates

import matplotlib.patches as patches

import matplotlib.transforms as mtransforms

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg


INPUT_FILE = Path("data/final/ev_registrations_monthly_clean.csv")

df = pd.read_csv(INPUT_FILE)

# Convert month to datetime.
# Your final file uses "month" like "2024-01".
df["plot_date"] = pd.to_datetime(df["month"], errors="raise")

# Always sort time series before plotting.
df = df.sort_values("plot_date")

# Make sure numeric columns are actually numeric.
numeric_cols = [
    "total_new_registrations",
    "electric_new_registrations",
    "hybrid_new_registrations",
    "emission_free_share",
    "hybrid_share",
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


def format_thousands(x, _):
    return f"{int(x):,}"


def format_percent(x, _):
    return f"{x * 100:.0f}%"


# -------------------------------------------------------------------
# Observed monthly data for full timeframe
# -------------------------------------------------------------------

monthly = df.copy()

# Place each monthly observation around the middle of its month.
monthly["plot_date_mid"] = (
    monthly["plot_date"] + pd.offsets.MonthEnd(0)
) - pd.offsets.Day(14)

# Year helper for policy baseline.
monthly["year"] = monthly["plot_date"].dt.year


# ------------------------
# Add Trend Line EV Share
# ------------------------

trend_data = monthly[["plot_date_mid", "emission_free_share"]].dropna().copy()
trend_data["date_num"] = trend_data["plot_date_mid"].map(pd.Timestamp.toordinal)

slope, intercept = np.polyfit(
    trend_data["date_num"],
    trend_data["emission_free_share"],
    1
)

trend_data["trend"] = slope * trend_data["date_num"] + intercept

# --------------------
# Add Policy Lines for EU and AT
# --------------------

baseline_year = 2020

baseline_emission_free_share = monthly.loc[
    monthly["year"] == baseline_year, "emission_free_share"
].mean()

policy_EU_start = pd.Timestamp("2021-01-01")
policy_EU_end = pd.Timestamp("2034-12-31")


policy_AT_start = pd.Timestamp("2021-01-01")
policy_AT_end = pd.Timestamp("2029-12-31")


policy_line_EU = pd.DataFrame({
    "plot_date": [policy_EU_start, policy_EU_end],
    "emission_free_share": [baseline_emission_free_share, 1.0],
})

policy_line_AT = pd.DataFrame({
    "plot_date": [policy_AT_start, policy_AT_end],
    "emission_free_share": [baseline_emission_free_share, 1.0],
})



# ------------------
# Color and style settings
# ------------------

KD_BG = "#18181B"          # bg-gray-900
KD_PANEL = "#27272A"       # bg-gray-800
KD_GRID = "#71717B"        # dark:bg-gray-500
KD_TEXT = "#F4F4F5"        # bg-gray-100 / light text
KD_MUTED = "#9F9FA9"       # bg-gray-400
KD_MOBILITY = "#F5AF4A"    # bg-mobility
KD_FONT = "Barlow"                          # Correct Font implement later
KD_FONT_CONDENSED = "Barlow Condensed"      # correct font implement later

EV_COLOR = KD_MOBILITY # Use Klimadashboard color as main color

plt.rcParams.update({
    "font.family": "sans-serif",            # Implement KD_FONT here later
    "axes.facecolor": KD_BG,
    "figure.facecolor": KD_BG,
    "axes.edgecolor": KD_GRID,
    "axes.labelcolor": KD_TEXT,
    "xtick.color": KD_MUTED,
    "ytick.color": KD_MUTED,
    "text.color": KD_TEXT,
    "grid.color": KD_GRID,
    "grid.alpha": 0.25,
    "lines.linewidth": 1.8,
})

# Legend labels

label_legend_emission_free_share = "_nolegend_" #E-Fahrzeug-Anteil, monatlich beobachtet"
label_legend_policy = "_nolegend_" # Zielpfad: 100 % Elektrofahrzeug-Anteil bis 2030

DATE_PADDING = pd.DateOffset(months=3) # Adds some space to x-axis limits
FOCUS_VIEW_PADDING = pd.DateOffset(months=1) # Adds some space to x-axis limits
FULL_VIEW_PADDING = pd.DateOffset(months=6) # Adds some space to x-axis limits

# Make data points for month appear in the middle of the month
monthly["plot_date_mid"] = (
    monthly["plot_date"] + pd.offsets.Day(14)
)

# -----------------------
# Functions
# -----------------------

def style_kd_axis(ax):
    '''
    Determine visual style, colors, grid, border and tick positioning of graph.
    '''
    ax.set_facecolor(KD_BG)

    # Makes axis around the graph/border disappear
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Makes 0 axis visible
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color(KD_GRID)
    ax.spines["bottom"].set_alpha(0.4)

    # Positions values of axis label (f.ex. 20%, 40 %)
    ax.tick_params(axis="x", colors=KD_MUTED, direction="in", length=6, pad=-6)
    ax.tick_params(axis="y", colors=KD_MUTED, length=0, pad=-6)

    for label in ax.get_xticklabels():
        label.set_verticalalignment("bottom")

    for label in ax.get_yticklabels():
        label.set_horizontalalignment("left")
        label.set_transform(
            label.get_transform()
            + mtransforms.ScaledTranslation(
                0, 8 / 72, ax.figure.dpi_scale_trans
            )
        )

    # Sets color of axis label
    ax.xaxis.label.set_color(KD_TEXT)
    ax.yaxis.label.set_color(KD_TEXT)

    # Sets color of grid
    ax.grid(color=KD_GRID, alpha=0.35, linewidth=1, axis="y")

def add_kd_header(fig, title):
    '''
    Adds and styles the header of the dashboard.
    '''
    fig.patch.set_facecolor(KD_BG)
    header_y = 0.83 # y-axis start
    header_x = 0.08 # x-axis start
    header_w = 0.9 # width
    header_h = 0.15 # header height

    header = patches.FancyBboxPatch(
        (header_x, header_y),
        header_w,
        header_h,
        boxstyle="round,pad=0.0,rounding_size=0.03",
        transform=fig.transFigure,
        facecolor=KD_MOBILITY,
        edgecolor="none",
        zorder=10,
        clip_on=False,

    )
    fig.patches.append(header)

    # Overlay rectangle to remove bottom rounding
    bottom_fill = patches.Rectangle(
        (header_x, header_y),
        header_w,
        header_h - 0.03,
        transform=fig.transFigure,
        facecolor=KD_MOBILITY,
        edgecolor="none",
        zorder=11,
        clip_on=False,
    )
    fig.patches.append(bottom_fill)


    fig.text(
        header_x + header_x /2,
        header_y + header_h /2,
        title,
        color="white",
        fontsize=18,
        fontweight="bold",
        va="center",
        ha="left",
        zorder=12,
    )

    # Car icon on right side of header
    car_img = mpimg.imread("data/media/car_trans.png")
    imagebox = OffsetImage(car_img, zoom=0.14)

    car_icon = AnnotationBbox(
        imagebox,
        (header_x + header_w - 0.05, header_y + header_h / 2),
        xycoords=fig.transFigure,
        frameon=False,
        box_alignment=(0.5, 0.5),
        zorder=12,
    )

    fig.add_artist(car_icon)

def configure_share_yaxis(ax, zoom_to_40=False, show_labels=True):

    '''
    Controls data scale and y-axis values, depending on the Zoom.
    '''

    ymax = 0.4 if zoom_to_40 else 1.0

    ax.set_ylim(0, ymax * 1.04)  # tiny buffer so top tick isn't clipped

    if zoom_to_40:
        ticks = [0, 0.1, 0.2, 0.3, 0.4] # y-axis only goes to 40 %
    else:
        ticks = [0, 0.2, 0.4, 0.6, 0.8, 1.0]

    ax.set_yticks(ticks)

    if show_labels:
        labels = [f"{t * 100:.0f}" for t in ticks]
        labels[-1] += "%"
        ax.set_yticklabels(labels)
    else:
        ax.set_yticklabels([])

def plot_emission_free_share(focus_on_2026=False, zoom_to_40=False):
    fig, ax = plt.subplots(figsize=(11, 6))

    add_kd_header(
        fig,
        "Emissionsfreie PKW-Neuzulassungen"
    )

    # Observed EV share
    ax.plot(
        monthly["plot_date_mid"],
        monthly["emission_free_share"],
        marker=None,
        markersize=6,
        linewidth=2.5,
        color=KD_MOBILITY,
        label=label_legend_emission_free_share,
    )

    end_x = monthly["plot_date_mid"].iloc[-1]
    end_y = monthly["emission_free_share"].iloc[-1]

    end_point, = ax.plot(
        [end_x], [end_y],
        marker="o",
        fillstyle="none",
        markersize=8,
        color=EV_COLOR,
        linestyle="None",
        label="_nolegend_",
        )

    # Policy path

    ax.plot(
        policy_line_EU["plot_date"],
        policy_line_EU["emission_free_share"],
        linestyle=(0, (12, 6)),
        linewidth=2.2,
        color=KD_MOBILITY,
        alpha=0.5,
        label=label_legend_policy,
    )

    ax.plot(
        policy_line_AT["plot_date"],
        policy_line_AT["emission_free_share"],
        linestyle=(0, (12, 6)),
        linewidth=2.2,
        color=KD_MOBILITY,
        alpha=0.5,
        label=label_legend_policy,
    )

    ax.set_xlim(
        monthly["plot_date_mid"].min() - FULL_VIEW_PADDING,
        pd.Timestamp("2034-12-31"),
    )
    ax.xaxis.set_major_locator(YearLocator(base=2))
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))

    '''
    legend = ax.legend(
        loc="center right",
        facecolor=KD_BG,
        edgecolor=KD_GRID,
        labelcolor=KD_TEXT,
        framealpha=0.9,
    )
    '''




    # ----------------------
    # Policy Line
    # ----------------------

    policy_x_EU = policy_line_EU["plot_date"].iloc[-1]
    policy_y_EU = policy_line_EU["emission_free_share"].iloc[-1]

    policy_x_AT = policy_line_AT["plot_date"].iloc[-1]
    policy_y_AT = policy_line_AT["emission_free_share"].iloc[-1]

    ax.annotate(
        "EU-Ziel: 100 % (2035)",
        xy=(policy_x_EU, policy_y_EU),
        xytext=(-50, -10),
        textcoords="offset points",
        ha="right",
        va="top",
        color=EV_COLOR,
        fontsize=9,
        fontweight="bold",
        alpha=0.5,
    )

    ax.annotate(
        "AT-Ziel: 100% (2030)",
        xy=(policy_x_AT, policy_y_AT),
        xytext=(-50, -10),
        textcoords="offset points",
        ha="right",
        va="top",
        color=EV_COLOR,
        fontsize=9,
        fontweight="bold",
        alpha=0.5,
    )

    style_kd_axis(ax)
    configure_share_yaxis(ax, zoom_to_40, show_labels=True)



    # --------------
    # Label Box for last observed point
    # --------------

    last_x = monthly["plot_date_mid"].iloc[-1]
    last_y = monthly["emission_free_share"].iloc[-1]

    last_start = monthly["plot_date"].iloc[-1]
    last_end = last_start + pd.offsets.MonthEnd(0)

    last_period = (
        f"{last_start.strftime('%d.%m.%Y')} – "
        f"{last_end.strftime('%d.%m.%Y')}"
    )


    ax.annotate(
        f"{last_y:.1%} Anteil emissionsfreier PKW-Neuzulassungen im Zeitraum \n{last_period}",
        xy=(last_x, last_y),
        xytext=(12, -8),
        textcoords="offset points",
        ha="left",
        va="top",
        color=EV_COLOR,
        fontsize=11,
        fontweight="bold",
    )

    plt.subplots_adjust(top=0.82, bottom=0.13, left=0.08, right=0.97)

    '''
    plt.savefig(
        "../outputs/klimadashboard_v.2.1.png",
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    '''

    plt.show()


plot_emission_free_share()
