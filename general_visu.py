import pandas as pd
import seaborn as sns
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import os
import numpy as np
import math

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

def value_goals_correlation(merged_table_teams, x_vars, y_vars, result_folder, figure_name):

    # Create subplots with correct shape: rows = y, columns = x
    fig, axes = plt.subplots(len(y_vars), len(x_vars), figsize=(6 * len(x_vars), 4 * len(y_vars)))
    axes = np.array(axes).reshape(len(y_vars), len(x_vars))  # ensure shape consistency

    for row_idx, y in enumerate(y_vars):
        for col_idx, x in enumerate(x_vars):
            ax = axes[row_idx, col_idx]

            # Scatter + regression
            sns.scatterplot(data=merged_table_teams, x=x, y=y, ax=ax, s=40, alpha=0.6)
            sns.regplot(data=merged_table_teams, x=x, y=y, ax=ax,
                        scatter=False, color='red', line_kws={'lw': 2})

            # Correlation
            sub_df = merged_table_teams[[x, y]].dropna()
            corr, pval = pearsonr(sub_df[x], sub_df[y])
            corr_text = f"r = {corr:.2f}" + (" *" if pval < 0.05 else "")
            ax.text(0.05, 0.95, corr_text, transform=ax.transAxes,
                    verticalalignment='top', bbox=dict(boxstyle="round", facecolor="white", alpha=0.6))

            # Axis labels
            if col_idx == 0:
                ax.set_ylabel(y)
            else:
                ax.set_ylabel('')
            if row_idx == len(y_vars) - 1:
                ax.set_xlabel(x)
            else:
                ax.set_xlabel('')

    plt.tight_layout()
    plt.savefig(os.path.join(result_folder, figure_name))
    plt.close()


def correlation_heatmap(df, cols, result_folder, filename):
    # Compute correlation matrix
    corr = df[cols].corr()

    # Set style
    sns.set_theme(style="whitegrid", font_scale=1.2)

    # Create figure
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(
        corr,
        cmap='YlGnBu',  # alternative: 'mako', 'viridis', 'rocket'
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        linecolor='white',
        square=True,
        cbar_kws={"shrink": 0.8}
    )

    plt.title("Correlation Matrix", fontsize=16, weight='bold', pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    # Save and close
    output_path = os.path.join(result_folder, filename)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_avg_top_bottom_by_league(df_league_avg, result_folder, filename):
    leagues = df_league_avg["league"]
    x = np.arange(len(leagues))
    width = 0.35

    with plt.style.context({
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.grid': True,
        'grid.alpha': 0.4,
        'grid.linestyle': '--',
        'axes.edgecolor': 'black',
        'axes.linewidth': 1.2,
        'axes.labelsize': 11,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
    }):
        fig, ax = plt.subplots(figsize=(10, 5))

        # Bars
        ax.bar(x - width/2, df_league_avg["top_avg_value"], width=width,
               label="Top 5", color="springgreen", alpha=0.9)
        ax.bar(x + width/2, df_league_avg["bottom_avg_value"], width=width,
               label="Bottom 5", color="lightcoral", alpha=0.9)

        # Labels and ticks
        ax.set_xticks(x)
        ax.set_xticklabels(leagues, rotation=45, ha="right", fontsize=11)
        ax.set_ylabel("Average Market Value", fontsize=11)
        ax.legend()

        # Enforce tick direction manually
        ax.tick_params(axis='x', direction='out')
        ax.tick_params(axis='y', direction='out')

        plt.tight_layout()
        os.makedirs(result_folder, exist_ok=True)
        plt.savefig(os.path.join(result_folder, filename), dpi=300)
        plt.close()


def league_match_stats(df_stats, column_map, df_anova, result_folder, filename):
    categories = list(column_map.values())
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    leagues = df_stats["league"].tolist()
    data = df_stats[categories].values

    # Determine grid size
    num_leagues = len(leagues)
    total_plots = num_leagues + 1  # one extra for the ANOVA
    ncols = 2
    nrows = math.ceil(total_plots / ncols)

    # Use default color cycle
    color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                             subplot_kw=dict(polar=True),
                             figsize=(ncols * 6, nrows * 5))

    axes = np.array(axes).reshape(-1)

    for idx, ax in enumerate(axes):
        if idx < num_leagues:
            values = data[idx].tolist()
            values += values[:1]

            color = color_cycle[idx % len(color_cycle)]

            ax.plot(angles, values, label=leagues[idx], color=color)
            ax.fill(angles, values, alpha=0.1, color=color)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=10)
            ax.set_title(leagues[idx], fontsize=13, pad=10, weight='bold')
            ax.set_yticks([])
            ax.grid(True, linestyle="--", alpha=0.3)

        elif idx == num_leagues:
            # This is the "extra" subplot: turn off polar and show ANOVA
            axes[idx].remove()  # remove polar projection
            ax = fig.add_subplot(nrows, ncols, idx + 1)  # replace with regular axis

            ax.axis('off')  # turn off axis frame

            # Format ANOVA result lines
            lines = [r"$\bf{ANOVA\ Test\ Results}$"]  # title line, LaTeX bold
            lines.append("")
            for _, row in df_anova.iterrows():
                pval = f"{row['p-value']:.4f}"           # round to 2 decimal
                sig_marker = "*" if row['p-value'] < 0.05 else " "
                lines.append(f"{row['Variable']:<18}  F = {row['F-statistic']:05.2f}   p = {pval:<7} {sig_marker}")
            
            # Join into single string
            full_text = "\n".join(lines)

            # Display text in a centered fancy box
            ax.text(
                0.5, 0.5, full_text,
                fontsize=11,
                family='monospace',
                ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.6", facecolor="#f9f9f9", edgecolor="gray", alpha=0.95)
            )

        else:
            ax.axis('off')  # hide any remaining unused subplots

    plt.subplots_adjust(hspace=0.5)
    # fig.suptitle("Average Match Stats per League", fontsize=16, y=1.02)
    plt.tight_layout()
    os.makedirs(result_folder, exist_ok=True)
    plt.savefig(os.path.join(result_folder, filename), dpi=300, bbox_inches='tight')
    plt.close()