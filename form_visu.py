import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

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

def plot_goals_boxplot(df_full, result_folder, filename):
    # Define consistent palette
    palette = {
        0: "lightgray",     # Loss or draw
        1: "mediumseagreen" # Win
    }

    # Plot
    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(
        data=df_full,
        x="league",
        y="score_last_3",
        hue="win",
        palette=palette
    )

    # Fix legend manually
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles=handles,
        labels=["Loss or Draw", "Win"],
        title="Match Outcome"
    )

    # Labels and style
    plt.xlabel("League")
    plt.ylabel("Goals Scored (Last 3 Matches)")
    plt.ylim(-2, 20)
    plt.xticks(rotation=30)
    plt.tight_layout()

    # Save plot
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()



def plot_possession_shots_goals_heatmap(df, result_folder, filename):

    # Define bins
    possession_bins = range(30, 71, 10)  # 30% to 70% in 5-point steps
    shots_bins = range(0, 30, 6)        # 0 to 25 shots in 3-shot steps

    # Apply binning
    df["possession_bin"] = pd.cut(df["possession"], bins=possession_bins, right=False)
    df["shots_bin"] = pd.cut(df["shots"], bins=shots_bins, right=False)

    # Compute average goals per bin
    heatmap_data = (
        df.groupby(["possession_bin", "shots_bin"], observed=False)["goals"]
        .mean()
        .unstack()
        .sort_index(ascending=True)
    )

    # Plot heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="YlOrRd",
        cbar_kws={'label': 'Avg Goals Scored'},
        linewidths=0.5,
        linecolor='white'
    )

    plt.xlabel("Shot Attempts (Last 3 Matches)")
    plt.ylabel("Possession % (Last 3 Matches)")
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Save plot
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()


def plot_yellows_saves_goals_conceded_heatmap(df_full, result_folder, filename):

    # Bin variables
    yellow_bins = np.arange(0, 8, 1.5)  # 0 to 10 cards, step 1
    saves_bins = np.arange(0, 8, 1.5)   # 0 to 10 saves, step 1

    df_full["yellow_bin"] = pd.cut(df_full["yellow_cards"], bins=yellow_bins, right=False)
    df_full["saves_bin"] = pd.cut(df_full["saves"], bins=saves_bins, right=False)

    # Compute average goals conceded per bin combo
    heatmap_data = (
        df_full.groupby(["yellow_bin", "saves_bin"], observed=False)["goals_conceded"]
        .mean()
        .unstack()
        .sort_index(ascending=True)
    )

    # Plot heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        cbar_kws={'label': 'Avg Goals Conceded'},
        linewidths=0.5,
        linecolor='white'
    )

    plt.xlabel("Saves (Last 3 Matches)")
    plt.ylabel("Yellow Cards (Last 3 Matches)")
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()

    # Save plot
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()



def plot_win_rate_by_goals_scored_and_conceded(df_plot, result_folder, filename):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_plot, x="goals", y="win_rate", hue="type", palette=["royalblue", "tomato"])

    plt.xlabel("Goals")
    plt.ylabel("Win Rate")
    plt.ylim(0, 1.1)
    plt.legend(title="")
    plt.xticks(sorted(df_plot["goals"].unique()))
    plt.tight_layout()

    # Save
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()


def plot_win_rate_by_recent_points(df_full, result_folder, filename):

    # Group and compute win rate
    grouped = df_full.groupby(["league", "points_last_5"])["win"].mean().reset_index()

    # Plot
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=grouped,
        x="points_last_5",
        y="win",
        hue="league",
        marker="o",
        palette="Set2"
    )

    # Style
    plt.xlabel("Points Earned")
    plt.ylabel("Win Rate")
    plt.xticks(range(0, 16))  # Points can range from 0 to 9
    plt.ylim(0, 1)
    plt.legend(title="League")
    plt.grid(True)
    plt.tight_layout()

    # Save
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()