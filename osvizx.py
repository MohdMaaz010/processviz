import subprocess
import sys
import psutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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

# Initialize figure and axes
fig = plt.figure(figsize=(14, 14))
fig.suptitle('Real-Time Task Manager Simulation', fontsize=18, weight='bold')

# Define subplot positions
table_ax = fig.add_axes([0.05, 0.7, 0.4, 0.2])  
pie_ax = fig.add_axes([0.55, 0.7, 0.3, 0.25])  
legend_ax = fig.add_axes([0.87, 0.7, 0.1, 0.25])  
bar_ax = fig.add_axes([0.1, 0.2, 0.8, 0.4])    

# Adjusted textbox position
textbox_ax = fig.add_axes([0.45, 0.88, 0.085, 0.03])
textbox = TextBox(textbox_ax, "Processes:", initial="5")

# Draw a manual rectangle around the textbox
border = patches.Rectangle(
    (0, 0), 1, 1, transform=textbox_ax.transAxes,
    linewidth=2, edgecolor='black', facecolor='none'
)
textbox_ax.add_patch(border)

# Remove axis ticks and labels around the text box
textbox_ax.set_xticks([])
textbox_ax.set_yticks([])
textbox_ax.set_frame_on(False)
# Default process limit
process_limit = 5
colors = ['#FF6B6B', '#4D96FF', '#6BCB77', '#FFA36C', '#C47AFF', '#FFD700', 
          '#8A2BE2', '#FF4500', '#20B2AA', '#DC143C']

# Default process limit
# process_limit = 5  # You can change this to any number between 2 and 9

# Adjusted textbox position

def update_process_limit(text):
    """Update the process limit based on user input."""
    global process_limit
    try:
        value = int(text)
        if 2 <= value <= 9:  # Max limit is now 9
            process_limit = value
        else:
            print("Limit must be between 2 and 9. Resetting to default (5).")
            textbox.set_val("5")
            process_limit = 5
    except ValueError:
        print("Invalid input. Enter a number between 2 and 9.")
        # textbox.set_val(str(process_limit))

textbox.on_submit(update_process_limit)

def get_top_processes():
    """Fetch top processes sorted by CPU usage."""
    psutil.cpu_percent(interval=0.1)  # Ensure updated CPU values
    return sorted(
        psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']),
        key=lambda p: p.info['cpu_percent'],
        reverse=True
    )[:process_limit]

def display_process_table(processes):
    """Display process table with dynamically positioned heading."""
    table_ax.clear()
    table_ax.axis('off')

    # Prepare table data
    cell_text = [[p.info['pid'], p.info['name'][:10], f"{p.info['cpu_percent']:.2f}", 
                  f"{p.info['memory_percent']:.2f}"] for p in processes]

    # Column headers
    col_labels = ['PID', 'Name', 'CPU (%)', 'Mem (%)']

    table = table_ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc='center',
        cellLoc='center',
        colColours=['#DDDDDD'] * 4  
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(0.7, 1.2)

    # Add "Top Processes" heading above the table
    table_ax.text(0.5, 1.2, "Top Processes", fontsize=16, weight='bold', ha='center', transform=table_ax.transAxes)



def plot_bar_chart(processes):
    """Render bar chart with dynamic Y-axis scaling."""
    bar_ax.cla()
    bar_ax.set_title('CPU Usage (Bar Chart)', fontsize=14, weight='bold')
    bar_ax.text(0.5, 1.15, f"Total RAM Usage: {psutil.virtual_memory().percent:.2f}%", 
                 ha='center', fontsize=12, color='red', transform=bar_ax.transAxes, weight='bold')
    names = [f"{p.info['name']} (PID {p.info['pid']})" for p in processes]
    cpu_usages = [p.info['cpu_percent'] for p in processes]
    bar_ax.set_ylim(0, max(cpu_usages, default=100) * 1.2)
    bars = bar_ax.bar(names, cpu_usages, color=colors[:len(processes)], edgecolor='black')
    bar_ax.set_ylabel('CPU Usage (%)', fontsize=12)
    bar_ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10)
    for bar, usage in zip(bars, cpu_usages):
        bar_ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, f"{usage:.1f}%", 
                     ha='center', va='bottom', fontsize=9, weight='bold')

def plot_pie_chart(processes):
    """Render the pie chart with separate legend."""
    pie_ax.clear()
    pie_ax.text(0, 1.1, 'CPU Usage Distribution', fontsize=14, weight='bold', ha='center')

    names = [p.info['name'] for p in processes]
    cpu_usages = [max(p.info['cpu_percent'], 0.1) for p in processes]

    wedges, _ = pie_ax.pie(
        cpu_usages,
        colors=colors[:len(processes)],
        startangle=90,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
    )

    centre_circle = plt.Circle((0, 0), 0.65, fc='white')
    pie_ax.add_artist(centre_circle)

    # Update legend separately
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
