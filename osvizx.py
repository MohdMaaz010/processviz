import subprocess
import sys
import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox

# Function to install required libraries if not found
def install_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        print(f"{package_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Install necessary libraries
for package in ['psutil', 'matplotlib']:
    install_package(package)

# Initialize figure and axes for custom layout
fig = plt.figure(figsize=(14, 14))  # This is roughly 35.56 cm x 35.56 cm
fig.suptitle('Real-Time Task Manager Simulation', fontsize=18, weight='bold')

# Define subplot positions
table_ax = fig.add_axes([0.05, 0.7, 0.4, 0.2])  # Table (Top-Left)
pie_ax = fig.add_axes([0.55, 0.7, 0.3, 0.25])   # Pie Chart (Top-Right)
legend_ax = fig.add_axes([0.87, 0.7, 0.1, 0.25])  # Legend Box (Right of Pie Chart)
bar_ax = fig.add_axes([0.1, 0.2, 0.8, 0.4])     # Bar Chart (Bottom)

# Convert 3cm x 1cm to figure coordinates
# fig_width, fig_height = fig.get_size_inches()
# textbox_width = (3 / 2.54) / fig_width
# textbox_height = (1 / 2.54) / fig_height

# Adjusted textbox position to avoid overlap
textbox_ax = fig.add_axes([0.45, 0.88, 0.085, 0.03])
# textbox_ax = fig.add_axes([0.35, 0.88, textbox_width, textbox_height])  
textbox = TextBox(textbox_ax, "Processes:", initial="5")

# Default process limit
process_limit = 5
colors = ['#FF6B6B', '#4D96FF', '#6BCB77', '#FFA36C', '#C47AFF', '#FFD700', '#8A2BE2', '#FF4500', '#20B2AA', '#DC143C']

def update_process_limit(text):
    """Update the process limit based on user input."""
    global process_limit
    try:
        value = int(text)
        if 2 <= value <= 10:
            process_limit = value
        else:
            print("Limit must be between 2 and 10. Resetting to default (5).")
            textbox.set_val("5")
            process_limit = 5
    except ValueError:
        print("Invalid input. Enter a number between 2 and 10.")
        textbox.set_val(str(process_limit))

textbox.on_submit(update_process_limit)

def get_top_processes():
    """Fetch top processes sorted by CPU usage."""
    return sorted(
        psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']),
        key=lambda p: p.info['cpu_percent'],
        reverse=True
    )[:process_limit]
def adjust_table_title():
    """Adjust the title position dynamically above the table."""
    table_ax.set_title('Top Processes', fontsize=14, weight='bold', 
                       pad=(table_ax.get_position().bounds[3] * 100+20))

def display_process_table(processes):
    """Display process table and dynamically adjust title position."""
    table_ax.clear()
    table_ax.axis('off')
    #     table_ax.set_title('Top Processes', fontsize=14, weight='bold', pad=10)  # Increase padding

    cell_text = [[p.info['pid'], p.info['name'][:10], f"{p.info['cpu_percent']:.2f}", f"{p.info['memory_percent']:.2f}"] for p in processes]
    table = table_ax.table(
        cellText=cell_text,
        colLabels=['PID', 'Name', 'CPU (%)', 'Mem (%)'],
        loc='center',
        cellLoc='center',
        colColours=['#DDDDDD'] * 4
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(0.7, 1.2)

    # Adjust title position dynamically
    adjust_table_title()

# def display_process_table(processes):
#     """Display process table with smaller column width."""
#     table_ax.clear()
#     table_ax.axis('off')
#     # table_ax.set_title('Top Processes', fontsize=14, weight='bold')

#     cell_text = [[p.info['pid'], p.info['name'][:10], f"{p.info['cpu_percent']:.2f}", f"{p.info['memory_percent']:.2f}"] for p in processes]
#     table = table_ax.table(
#         cellText=cell_text,
#         colLabels=['PID', 'Name', 'CPU (%)', 'Mem (%)'],
#         loc='center',
#         cellLoc='center',
#         colColours=['#DDDDDD'] * 4
#     )
#     table.auto_set_font_size(False)
#     table.set_fontsize(9)
#     table.scale(0.7, 1.2)

def plot_bar_chart(processes):
    """Render a bar chart and fix label visibility."""
    bar_ax.clear()
    bar_ax.set_title('CPU Usage (Bar Chart)', fontsize=14, weight='bold')

    names = [f"{p.info['name']} (PID {p.info['pid']})" for p in processes]
    cpu_usages = [p.info['cpu_percent'] for p in processes]
    
    bars = bar_ax.bar(names, cpu_usages, color=colors[:len(processes)], edgecolor='black')
    bar_ax.set_ylabel('CPU Usage (%)', fontsize=12)
    bar_ax.set_ylim(0, max(cpu_usages) + 10)
    bar_ax.set_xticks(range(len(names)))
    bar_ax.set_xticklabels(names, rotation=0, ha='center', fontsize=10)

    for bar, usage in zip(bars, cpu_usages):
        bar_ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, f"{usage:.1f}%", 
                    ha='center', va='bottom', fontsize=9, weight='bold')

def plot_pie_chart(processes):
    """Render the pie chart with a separate legend."""
    pie_ax.clear()
    pie_ax.text(-1.5, 1, 'CPU Usage Distribution', fontsize=14, weight='bold', ha='center', va='center')

    names = [p.info['name'] for p in processes]
    cpu_usages = [max(p.info['cpu_percent'], 0.1) for p in processes]

    wedges, _ = pie_ax.pie(
        cpu_usages,
        colors=colors[:len(processes)],
        startangle=90,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
    )

    # Add a central white circle for a donut effect
    centre_circle = plt.Circle((0, 0), 0.65, fc='white')
    pie_ax.add_artist(centre_circle)

    # Update the legend separately
    legend_ax.clear()
    legend_ax.axis('off')

    legend_text = [[p.info['name'], f"{p.info['cpu_percent']:.1f}%"] for p in processes]
    legend_table = legend_ax.table(
        cellText=legend_text,
        colLabels=['Process', 'CPU %'],
        loc='center',
        cellLoc='left',
        colColours=['#DDDDDD', '#DDDDDD']
    )
    legend_table.auto_set_font_size(False)
    legend_table.set_fontsize(9)
    legend_table.scale(0.9, 1.2)

def update(frame):
    """Update function called by FuncAnimation."""
    top_processes = get_top_processes()
    display_process_table(top_processes)
    plot_bar_chart(top_processes)
    plot_pie_chart(top_processes)

# Start animation
animation = FuncAnimation(fig, update, interval=1000)
plt.show()
