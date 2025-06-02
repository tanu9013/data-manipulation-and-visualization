import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

def generate_pr_graph(csv_path="merged_ghi_pr.csv"):
    """
    Generate a performance graph showing PR evolution with moving average,
    GHI-based scatter coloring, and dynamic yearly budget PR line.
    """

    # Load and clean data
    df = pd.read_csv(csv_path)
    df.dropna(subset=['date', 'ghi', 'pr'], inplace=True)
    df['date'] = pd.to_datetime(df['date'], dayfirst=False)
    df = df.sort_values('date')

    # Compute 30-day moving average for PR
    df['pr_30ma'] = df['pr'].rolling(window=30).mean()

    # Generate budget line dynamically
    start_date = df['date'].min()
    end_date = df['date'].max()
    base_budget = 73.9
    decay_rate = 0.008  # 0.8%

    # Build yearly budget mapping
    budget_data = []
    current_start = dt.date(start_date.year, 7, 1)  # Start from July of that year
    year_count = 0

    while current_start <= end_date.date():
        current_end = dt.date(current_start.year + 1, 6, 30)
        budget_value = base_budget * ((1 - decay_rate) ** year_count)
        budget_data.append((current_start, current_end, budget_value))
        current_start = dt.date(current_start.year + 1, 7, 1)
        year_count += 1

    # Assign budget PR value for each date in df
    def get_budget_for_date(date):
        for start, end, val in budget_data:
            if start <= date.date() <= end:
                return val
        return None

    df['budget_pr'] = df['date'].apply(get_budget_for_date)

    # Scatter color by GHI
    def ghi_color(ghi):
        if ghi < 2:
            return 'navy'
        elif ghi < 4:
            return 'lightblue'
        elif ghi < 6:
            return 'orange'
        else:
            return 'brown'

    df['color'] = df['ghi'].apply(ghi_color)

    # Create plot
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    # Plot 30-day PR moving average
    ax.plot(df['date'], df['pr_30ma'], color='red', label='30-Day Moving Avg (PR)', linewidth=2)

    # Budget PR line
    ax.plot(df['date'], df['budget_pr'], color='darkgreen', linestyle='--', label='Budget PR', linewidth=2)

    # Scatter plot
    ax.scatter(df['date'], df['pr'], c=df['color'], label='Daily PR (colored by GHI)', alpha=0.7)

    # Highlight points above budget line
    above_budget = df[df['pr'] > df['budget_pr']]
    ax.scatter(above_budget['date'], above_budget['pr'], facecolors='none', edgecolors='black', label='Above Budget PR')

    # Average PR stats
    latest = df['date'].max()
    summary_text = ""
    for days in [7, 30, 60, 90]:
        past_date = latest - pd.Timedelta(days=days)
        avg_val = df[df['date'] >= past_date]['pr'].mean()
        summary_text += f"Last {days} days: {avg_val:.2f}\n"

    plt.text(1.01, 0.2, summary_text.strip(), transform=ax.transAxes, fontsize=10,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgrey"))

    # Format x-axis
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    plt.xticks(rotation=45)

    # Labels and legend
    plt.title("PR Evolution with Budget Line & GHI Impact")
    plt.xlabel("Date")
    plt.ylabel("PR")
    plt.grid(True)
    plt.legend(loc='upper left')

    # Save or show
    plt.tight_layout()
    plt.savefig("pr_graph.png", dpi=300)
    plt.show()
    print("Graph saved as 'pr_graph.png'")

# Run it
generate_pr_graph("merged_ghi_pr.csv")
