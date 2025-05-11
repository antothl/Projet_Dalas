import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
import re

# Apply global settings
plt.rcParams.update({
    'axes.spines.right': False,   # Enable right spine (solid)
    'axes.spines.top': False,     # Enable top spine (solid)
    'axes.grid': True,           # Enable grid
    'grid.alpha': 0.4,           # Make the grid transparent (adjust alpha)
    'xtick.direction': 'out',     # Tickmarks on x-axis (inside)
    'ytick.direction': 'out',     # Tickmarks on y-axis (inside)
    'grid.linestyle': '--',      # Dashed grid (can be changed)
    'axes.edgecolor': 'black',   # Ensure spines are visible
    'axes.linewidth': 1.2,        # Make spines slightly thicker
    'axes.labelsize': 11
})



def attack_defense_potential(df_full, result_folder, figure_name):
    # We'll use qcut to split the home_attack_defense_ratio into 5 quintile bins
    df_full["ratio_quintile"] = pd.qcut(
        df_full["home_attack_defense_ratio"],
        q=5,
        duplicates="drop"
    )

    # Prepare data for the boxplot: group by ratio_quintile
    grouped_scores = []
    labels = []
    # Sort the unique quintile labels so they appear in ascending order
    for category in sorted(df_full["ratio_quintile"].dropna().unique()):
        home_scores = df_full.loc[df_full["ratio_quintile"] == category, "home_score"]
        grouped_scores.append(home_scores.values)
        labels.append(str(category))

    plt.figure(figsize=(8, 5))
    plt.boxplot(grouped_scores, labels=labels, showmeans=True)
    plt.xlabel("Home Attack / Away Defense - Value ratio")
    plt.ylabel("Home Goals Scored")
    # plt.title("Boxplot: Home Goals vs. Home Attack/Defense Ratio (Raw Values)")
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, figure_name))
    plt.close()



def extract_lower_bound(label: str):
    """
    Extract the lower bound from a bin label like '(9949999.999, 41850000.0]'.
    Returns a float if successful, or None if no number is found.
    """
    match = re.search(r'\(([^,]+),', label)  # look for '(...,'
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

def defensive_potential(df_full, result_folder, figure_name):

    # 1) Prepare data as a pivot table
    pivot_df = df_full.pivot_table(
        values="goals_conceded_away",
        index="pos_gap_bin",
        columns="away_defense_bin",
        aggfunc="mean",
        observed=True
    )

    def reformat_bin_label(label):
        label_str = str(label)
        bounds = label_str.split(', ')
        lowerbound = bounds[0][1:]
        upperbound = bounds[1][:-1]
        lower_sci = f"{float(lowerbound):.1e}"
        upper_sci = f"{float(upperbound):.1e}"
        return f"({lower_sci}, {upper_sci}]"

    # Apply this to all column labels in pivot_df
    pivot_df.columns = [reformat_bin_label(col) for col in pivot_df.columns]

    # 2) Create a figure
    plt.figure(figsize=(9, 6))

    # 3) Plot directly with seaborn
    sns.heatmap(
        pivot_df,
        cmap="magma_r",                 # or another colormap
        cbar_kws={"label": "Mean Goals Conceded Away"}
    )

    # 4) Customize ticks/labels if needed
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Away Defense Value")
    plt.ylabel("Positional Gap (Away - Home)")

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, figure_name))
    plt.close()


def plot_violin_goals(df_melted, result_folder, figure_name):

    # Separate the data into four Series (dropna to avoid errors)
    scored_home = df_melted.loc[df_melted['variable'] == 'avg_goals_scored_home', 'goals'].dropna()
    scored_away = df_melted.loc[df_melted['variable'] == 'avg_goals_scored_away', 'goals'].dropna()
    conceded_home = df_melted.loc[df_melted['variable'] == 'avg_goals_conceded_home', 'goals'].dropna()
    conceded_away = df_melted.loc[df_melted['variable'] == 'avg_goals_conceded_away', 'goals'].dropna()

    # Prepare the data lists for plotting
    data_scored = [scored_home, scored_away]
    data_conceded = [conceded_home, conceded_away]

    # Statistical tests
    stat_scored, p_scored = mannwhitneyu(scored_home, scored_away, alternative="two-sided")
    stat_conceded, p_conceded = mannwhitneyu(conceded_home, conceded_away, alternative="two-sided")

    # Create two subplots side by side
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 6), sharey=True)

    # -- Left subplot: Goals Scored (Home, Away) --
    vp_scored = ax1.violinplot(data_scored, showmeans=True, showextrema=False)
    ax1.set_title("Goals Scored")
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(["Home", "Away"])
    ax1.set_ylabel("Goals per Match")

    vp_scored['bodies'][0].set_facecolor("skyblue")    # Home
    vp_scored['bodies'][0].set_edgecolor("black")
    vp_scored['bodies'][0].set_alpha(0.7)

    vp_scored['bodies'][1].set_facecolor("lightgreen") # Away
    vp_scored['bodies'][1].set_edgecolor("black")
    vp_scored['bodies'][1].set_alpha(0.7)

    vp_scored['cmeans'].set_color("red")

    # Annotate test results on left plot
    ax1.text(
        0.55, 0.1, f"U = {stat_scored:.1f}\np = {p_scored:.2f}*",
        transform=ax1.transAxes, fontsize=9,ha='right', multialignment='left',
        bbox=dict( boxstyle="round,pad=0.4", facecolor="lightgrey", edgecolor="dimgray")
        )

    # -- Right subplot: Goals Conceded (Home, Away) --
    vp_conceded = ax2.violinplot(data_conceded, showmeans=True, showextrema=False)
    ax2.set_title("Goals Conceded")
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(["Home", "Away"])

    vp_conceded['bodies'][0].set_facecolor("skyblue")    # Home
    vp_conceded['bodies'][0].set_edgecolor("black")
    vp_conceded['bodies'][0].set_alpha(0.7)

    vp_conceded['bodies'][1].set_facecolor("lightgreen") # Away
    vp_conceded['bodies'][1].set_edgecolor("black")
    vp_conceded['bodies'][1].set_alpha(0.7)

    vp_conceded['cmeans'].set_color("red")

    # Annotate test results on right plot
    ax2.text(
        0.58, 0.1, f"U = {stat_conceded:.1f}\np = {p_conceded:.2f}*",
        transform=ax2.transAxes, fontsize=9,ha='right', multialignment='left',
        bbox=dict( boxstyle="round,pad=0.4", facecolor="lightgrey", edgecolor="dimgray")
        )

    # -- Legend --
    home_patch = plt.Line2D([0], [0], marker='o', color='w', label='Home',
                            markerfacecolor='skyblue', markersize=10)
    away_patch = plt.Line2D([0], [0], marker='o', color='w', label='Away',
                            markerfacecolor='lightgreen', markersize=10)
    ax2.legend(handles=[home_patch, away_patch], loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, figure_name))
    plt.close()

def plot_separate_box_goals(df_melted, result_folder):
    # Séparation des données
    scored_home = df_melted.loc[df_melted['variable'] == 'avg_goals_scored_home', 'goals'].dropna()
    scored_away = df_melted.loc[df_melted['variable'] == 'avg_goals_scored_away', 'goals'].dropna()
    conceded_home = df_melted.loc[df_melted['variable'] == 'avg_goals_conceded_home', 'goals'].dropna()
    conceded_away = df_melted.loc[df_melted['variable'] == 'avg_goals_conceded_away', 'goals'].dropna()

    # Détermination de l'échelle Y commune
    all_values = scored_home.tolist() + scored_away.tolist() + conceded_home.tolist() + conceded_away.tolist()
    y_min = min(all_values)
    y_max = max(all_values)

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    ax1.boxplot([scored_home, scored_away], patch_artist=True,
                boxprops=dict(facecolor='skyblue'), medianprops=dict(color='red'))
    ax1.set_title("Average Goals Scored: Home vs Away", fontsize=14)
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(["Home", "Away"])
    ax1.set_ylabel("Average Goals per Match")
    ax1.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "goals_scored.png"))
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.boxplot([conceded_home, conceded_away], patch_artist=True,
                boxprops=dict(facecolor='lightcoral'), medianprops=dict(color='red'))
    ax2.set_title("Average Goals Conceded: Home vs Away", fontsize=14)
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(["Home", "Away"])
    ax2.set_ylabel("Average Goals per Match")
    ax2.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, "goals_conceded.png"))
    plt.close(fig2)

def prob_winning_home_away(df_2023, result_folder, figure_name):
    # 1. Prepare grouped data
    df_home = df_2023.groupby('home_prev_points')['home_win'].mean().reset_index()
    df_away = df_2023.groupby('away_prev_points')['away_win'].mean().reset_index()

    df_home['type'] = 'Home'
    df_home.rename(columns={'home_prev_points': 'prev_points', 'home_win': 'win_rate'}, inplace=True)

    df_away['type'] = 'Away'
    df_away.rename(columns={'away_prev_points': 'prev_points', 'away_win': 'win_rate'}, inplace=True)

    # 2. Combine into one DataFrame for plotting
    df_plot = pd.concat([df_home, df_away], ignore_index=True)

    # 3. Plot
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df_plot,
        x='prev_points',
        y='win_rate',
        hue='type',
        marker='o',
        palette={'Home': 'skyblue', 'Away': 'lightgreen'}
    )

    # 4. Style
    plt.xlabel("Points Earned in 2021–2022 vs Opponent")
    plt.ylabel("Win Rate in 2023")
    plt.ylim(0, 1)
    plt.grid(True)
    plt.legend(title="Game Type")
    plt.tight_layout()

    # 5. Save
    plt.savefig(os.path.join(result_folder, figure_name), dpi=300)
    plt.close()