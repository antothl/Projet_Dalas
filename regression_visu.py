import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd

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


def plot_classification_metrics(y_test, y_pred, result_folder, filename="classification_metrics.png"):
    # Get report as dict
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    accuracy = accuracy_score(y_test, y_pred)

    # Convert to DataFrame
    df_metrics = pd.DataFrame(report_dict).T
    df_metrics = df_metrics.loc[["0", "1"], ["precision", "recall", "f1-score"]]
    df_metrics = df_metrics.rename(index={"0": "Win = 0", "1": "Win = 1"})

    # Plot
    plt.figure(figsize=(8, 4))
    df_metrics.plot(kind='barh', ax=plt.gca(), colormap='Set2', edgecolor='black')
    plt.xlim(0, 1)
    plt.title(f"Classification Metrics\nAccuracy: {accuracy:.2%}", fontsize=14)
    plt.xlabel("Score")
    plt.ylabel("Class")
    plt.legend(title="Metric", loc='lower right')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save
    plt.savefig(os.path.join(result_folder, filename), dpi=300)
    plt.close()