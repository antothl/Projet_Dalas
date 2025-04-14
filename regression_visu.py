import seaborn as sns
import matplotlib.pyplot as plt
import os

def save_correlation_heatmap(df, result_folder, filename="correlation_matrix.png"):
    # 1. Compute the correlation matrix
    corr = df.corr()

    # 2. Set up the plot
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        cbar=True,
        square=True,
        linewidths=0.5,
        linecolor='white'
    )

    plt.title("Feature Correlation Matrix", fontsize=14)
    plt.tight_layout()

    # 3. Save the plot
    os.makedirs(result_folder, exist_ok=True)
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()