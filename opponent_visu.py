import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
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

    # Create two subplots side by side
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 6), sharey=True)

    # -- Left subplot: Goals Scored (Home, Away) --
    vp_scored = ax1.violinplot(data_scored, showmeans=True, showextrema=False)
    ax1.set_title("Goals Scored")
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(["Home", "Away"])
    ax1.set_ylabel("Goals per Match")

    # Assign consistent colors: index 0 = Home, index 1 = Away
    vp_scored['bodies'][0].set_facecolor("skyblue")    # Home
    vp_scored['bodies'][0].set_edgecolor("black")
    vp_scored['bodies'][0].set_alpha(0.7)

    vp_scored['bodies'][1].set_facecolor("lightgreen") # Away
    vp_scored['bodies'][1].set_edgecolor("black")
    vp_scored['bodies'][1].set_alpha(0.7)

    # Make the mean line red
    vp_scored['cmeans'].set_color("red")

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

    # -- Add a simple legend to the second subplot --
    home_patch = plt.Line2D([0], [0], marker='o', color='w', label='Home',
                            markerfacecolor='skyblue', markersize=10)
    away_patch = plt.Line2D([0], [0], marker='o', color='w', label='Away',
                            markerfacecolor='lightgreen', markersize=10)
    ax2.legend(handles=[home_patch, away_patch], loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, figure_name))
    plt.close()


def prob_winning_home_away(df_2023, result_folder, figure_name):

    # 1) Define binary outcomes for home/away wins
    df_2023['home_win'] = np.where(df_2023['home_score'] > df_2023['away_score'], 1, 0)
    df_2023['away_win'] = np.where(df_2023['away_score'] > df_2023['home_score'], 1, 0)

    # 2) Group by home_prev_points and compute mean of home_win & away_win
    grouped_home = df_2023.groupby('home_prev_points')['home_win'].mean()
    grouped_away = df_2023.groupby('away_prev_points')['away_win'].mean()

    # 3) Create side-by-side bar chart
    x_vals = np.arange(len(grouped_home.index))  # numeric positions for each unique home_prev_points
    bar_width = 0.4

    plt.figure(figsize=(8, 5))

    # Plot home win probabilities (blue bars)
    plt.bar(
        x_vals - bar_width/2, 
        grouped_home.values, 
        width=bar_width, 
        label="Home Win Probability",
        color="skyblue"
    )

    # Plot away win probabilities (green bars)
    plt.bar(
        x_vals + bar_width/2, 
        grouped_away.values, 
        width=bar_width, 
        label="Away Win Probability",
        color="lightgreen"
    )

    # 4) Labeling
    plt.xlabel("Points previous games vs. Team")
    plt.ylabel("Probability of Win")

    # Set x-ticks to match the home_prev_points categories
    plt.xticks(x_vals, grouped_home.index)

    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, figure_name))
    plt.close()