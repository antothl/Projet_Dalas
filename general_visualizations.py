import pandas as pd
import seaborn as sns
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import os
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