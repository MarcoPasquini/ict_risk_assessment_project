import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
from pathlib import Path

def evaluate_statistics(data):
    parsed_report = parse_report(data)
    print("Saving Statistical Analysis:\n")
    plot_statistics(parsed_report)

def parse_report(report):
    rows = []
    for entry in report['binaries_report']:
        path_parts = entry['filename'].split('/')
        size = entry['size']
        
        binary_name = path_parts[-1].split('-')
        mode = binary_name[-1]
        binary_name = binary_name[0]
        try:
            trials = entry['test_result']['trials']
            successes = entry['test_result']['successes']
            p_hat = entry['test_result']['p_hat']
            avg_time_to_attack = entry['test_result']['avg_time_to_attack']
        except:
            continue
        
        rows.append({
            "Binary": binary_name,
            "Mode": mode,
            "Total": trials,
            "Success": successes,
            "size": size,
            "p_hat": p_hat, 
            "avg_time_to_attack": avg_time_to_attack 
        })
    return rows

def plot_statistics(data):

    df = pd.DataFrame(data)

    save_binary_size_overhead_plot(df)
    plot_time_to_compromise_on_file(df)
    plot_attack_statistics_on_file(df)
    plot_asr(df)

def plot_asr(df, output_filepath="./results/"):
    pivot_df = df.pivot(index='Binary', columns='Mode', values='p_hat')

    pivot_df['ASR_Medium'] = (1 - (pivot_df['medium'] / pivot_df['low'])) * 100
    pivot_df['ASR_High'] = (1 - (pivot_df['high'] / pivot_df['low'])) * 100

    pivot_df = pivot_df.fillna(0)

    asr_plot_df = pivot_df[['ASR_Medium', 'ASR_High']].reset_index()
    asr_melted = asr_plot_df.melt(
        id_vars='Binary',
        value_vars=['ASR_Medium', 'ASR_High'],
        var_name='Configuration',
        value_name='ASR_Percentage'
    )

    asr_melted['Configuration'] = asr_melted['Configuration'].str.replace('ASR_', '')
    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=asr_melted,
        x='Binary',
        y='ASR_Percentage',
        hue='Configuration',
        palette=['#ffcc5c', '#ff6f69']
    )

    plt.title('Attack Success Reduction (ASR)', fontsize=16)
    plt.ylabel('Reduction % (Higher is Better)', fontsize=12)
    plt.xlabel('Binary', fontsize=12)
    plt.ylim(0, 115)

    for container in plt.gca().containers:
        plt.gca().bar_label(container, fmt='%.0f%%', padding=3)

    plt.legend(title='Comparison vs Low')
    plt.savefig(Path(output_filepath) / 'attack_success_reduction.png', dpi=300)
    print("Attack success reduction saved.")
    plt.close()

def save_binary_size_overhead_plot(df, output_filepath="./results/"):

    df['size'] = pd.to_numeric(df['size'])
    
    pivot_df = df.pivot(index='Binary', columns='Mode', values='size')
    
    pivot_df['Medium'] = ((pivot_df['medium'] - pivot_df['low']) / pivot_df['low']) * 100
    pivot_df['High'] = ((pivot_df['high'] - pivot_df['low']) / pivot_df['low']) * 100

    plot_data = pivot_df[['Medium', 'High']].reset_index()
    
    df_melted = plot_data.melt(
        id_vars='Binary', 
        value_vars=['Medium', 'High'], 
        var_name='Configuration', 
        value_name='Overhead_Pct'
    )

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        data=df_melted,
        x='Binary',
        y='Overhead_Pct',
        hue='Configuration',
        palette=['#ffcc5c', '#ff6f69'] # Giallo (Medium) e Rosso (High)
    )

    plt.title('Binary Size Overhead (Lower is Better)', fontsize=16)
    plt.ylabel('Increase over Low (%)', fontsize=12)
    plt.xlabel('Binary', fontsize=12)
    
    plt.axhline(0, color='black', linewidth=0.8)

    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', padding=3)

    plt.legend(title='Protection Level')
    plt.tight_layout()

    plt.savefig(Path(output_filepath) / 'binary_size_overhead.png', dpi=300)
    print("Binary size overhead saved.")
    plt.close()

def plot_time_to_compromise_on_file(df, output_filepath="./results/"):
    order_modes = ['low', 'medium', 'high']
    plt.figure(figsize=(12, 6))
    chart = sns.barplot(
        data=df,
        x='Binary',
        y='avg_time_to_attack',
        hue='Mode',
        hue_order=order_modes,
        width=0.6
    )
    plt.title('Time to Compromise (Higher is Better)', fontsize=16)
    plt.ylabel('Seconds to compromission', fontsize=12)
    plt.xlabel('Binary', fontsize=12)
    plt.legend(title='Protection Level')
    plt.tight_layout()

    plt.savefig(Path(output_filepath) / 'time_to_compromise.png', dpi=300)
    print("Time to compromise saved.")
    plt.close()

def plot_attack_statistics_on_file(df, output_filepath="./results/"):
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="white")
    sns.set_context("notebook", font_scale=1.1)

    mode_order = ["low", "medium", "high"]

    g = sns.FacetGrid(df, col="Binary", height=4, aspect=0.8, sharey=True)

    g.map(sns.barplot, "Mode", "Total", order=mode_order, color="lightgrey", errorbar=None, label="Total")

    g.map(sns.barplot, "Mode", "Success", order=mode_order, color="salmon", errorbar=None, label="Success")

    g.fig.suptitle('Attacks: Total vs Success', fontsize=16)

    g.set_axis_labels("Mode", "Success")
    g.set_titles(col_template="{col_name}")

    g.add_legend(title="", adjust_subtitles=True)

    plt.subplots_adjust(top=0.80)

    plt.savefig(Path(output_filepath) / 'attack_statistics.png', dpi=300, bbox_inches='tight')
    print("Attack statistics saved on file.")
    plt.close()
