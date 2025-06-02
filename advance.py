import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

def generate_pr_graph(csv_path="merged_ghi_pr.csv", start_date=None, end_date=None):
    """
    Generate a PR graph with moving average, GHI-colored scatter points,
    and budget PR line. Supports filtering by date range.

    Parameters:
        csv_path (str): Path to the merged CSV file
        start_date (str): Optional. Format 'YYYY-MM-DD'
        end_date (str): Optional. Format 'YYYY-MM-DD'
    """

    # Load and clean data
    df = pd.read_csv(csv_path)
    df.dropna(subset=['date', 'ghi', 'pr'], inplace=True)
    df['date'] = pd.to_datetime(df['date'], dayfirst=False)
    df = df.sort_values('date')

    # Filter by date range if provided
    if start_date:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['date'] <= pd.to_datetime(end_date)]

    if df.empty:
        print("No data available in the specified date range.")
        return

    # 30-day moving average of PR
    df['pr_30ma'] = df['pr'].rolling(window=30).mean()

    # Generate dynamic budget PR line
    base_budget = 73.9
    decay_rate = 0.008
    start_year = df['date'].min().year
    start_month = df['date'].min().month

    # Budget PR: July to June yearly intervals
    budget_data = []
    current_start = dt.date(start_year if start_month < 7 else start_year, 7, 1)
    year_count = 0

    while current_start <= df['date'].max().date():
        current_end = dt.date(current_start.year + 1, 6, 30)
        budget_value = base_budget * ((1 - decay_rate) ** year_count)
        budget_data.append((current_start, current_end, budget_value))
        current_start = dt.date(current_start.year + 1, 7, 1)
        year_count += 1

    def get_budget_for_date(date):
        for start, end, val in budget_data:
            if start <= date.date() <= end:
                return val
        return None

    df['budget_pr'] = df['date'].apply(get_budget_for_date)

    # Color based on GHI
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

    # Plotting
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    ax.plot(df['date'], df['pr_30ma'], color='red', label='30-Day Moving Avg (PR)', linewidth=2)
    ax.plot(df['date'], df['budget_pr'], color='darkgreen', linestyle='--', label='Budget PR', linewidth=2)
    ax.scatter(df['date'], df['pr'], c=df['color'], label='Daily PR (GHI colored)', alpha=0.7)

    # Highlight above-budget points
    above_budget = df[df['pr'] > df['budget_pr']]
    ax.scatter(above_budget['date'], above_budget['pr'], facecolors='none', edgecolors='black', label='Above Budget PR')

    # Add average PRs (last 7, 30, 60, 90 days in range)
    summary_text = ""
    latest = df['date'].max()
    for days in [7, 30, 60, 90]:
        past_date = latest - pd.Timedelta(days=days)
        avg = df[df['date'] >= past_date]['pr'].mean()
        summary_text += f"Last {days} days: {avg:.2f}\n"

    plt.text(1.01, 0.2, summary_text.strip(), transform=ax.transAxes, fontsize=10,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgrey"))

    # Format
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    plt.xticks(rotation=45)
    plt.title("Performance Ratio (PR) Evolution")
    plt.xlabel("Date")
    plt.ylabel("Performance Ratio (PR)")
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.tight_layout()

    # Save & show
    filename = f"pr_graph_{start_date or 'start'}_to_{end_date or 'end'}.png".replace(":", "-")
    plt.savefig(filename, dpi=300)
    plt.show()
    print(f"Graph saved as '{filename}'")

# Example usage
generate_pr_graph(
    csv_path="merged_ghi_pr.csv",
    start_date="yyyy-mm-dd",
    end_date="yyyy-mm-dd"
)
