
import subprocess
import sys
import psutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox
from datetime import datetime
import numpy as np

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

# Initialize figure with proper layout
plt.rcParams['toolbar'] = 'None'  # Disable toolbar
fig = plt.figure(figsize=(14, 12))
fig.suptitle('Real-Time Task Manager Simulation', fontsize=16, weight='bold')

# Define subplot positions with perfect spacing
gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 0.1, 1], width_ratios=[1, 0.8], 
                     hspace=0.4, wspace=0.3)

# Top row: Process table and pie chart
table_ax = fig.add_subplot(gs[0, 0])  # Process table (left)
pie_ax = fig.add_subplot(gs[0, 1])    # Pie chart (right)

# Middle row: Empty space for separation
# Bottom row: CPU and memory graphs
bar_ax = fig.add_subplot(gs[2, 0])    # CPU usage bar chart (left)
mem_ax = fig.add_subplot(gs[2, 1])    # Memory trend graph (right)

# Textbox for process limit
textbox_ax = fig.add_axes([0.45, 0.90, 0.085, 0.03])
textbox = TextBox(textbox_ax, "Processes:", initial="5")

# Style the textbox
border = patches.Rectangle(
    (0, 0), 1, 1, transform=textbox_ax.transAxes,
    linewidth=1, edgecolor='gray', facecolor='none'
)
textbox_ax.add_patch(border)
textbox_ax.set_xticks([])
textbox_ax.set_yticks([])
textbox_ax.set_frame_on(False)

# Color scheme and default process limit
colors = ['#FF6B6B', '#4D96FF', '#6BCB77', '#FFA36C', '#C47AFF', 
          '#FFD700', '#8A2BE2', '#FF4500', '#20B2AA', '#DC143C']
process_limit = 5
memory_history = []
MAX_HISTORY = 30

def update_process_limit(text):
    """Update the process limit based on user input."""
    global process_limit
    try:
        value = int(text)
        if 2 <= value <= 9:
            process_limit = value
        else:
            print("Limit must be between 2 and 9. Resetting to default (5).")
            textbox.set_val("5")
            process_limit = 5
    except ValueError:
        print("Invalid input. Enter a number between 2 and 9.")

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
    """Display process table with proper spacing."""
    table_ax.clear()
    table_ax.axis('off')

    cell_text = [[p.info['pid'], p.info['name'][:12], 
                f"{p.info['cpu_percent']:.1f}", 
                f"{p.info['memory_percent']:.1f}"] for p in processes]

    table = table_ax.table(
        cellText=cell_text,
        colLabels=['PID', 'Name', 'CPU%', 'Mem%'],
        loc='center',
        cellLoc='center',
        colWidths=[0.15, 0.35, 0.2, 0.2]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    table_ax.set_title('Top Processes', fontsize=12, weight='bold', pad=10)

def plot_bar_chart(processes):
    """Render a bar chart with perfect spacing."""
    bar_ax.clear()
    names = [f"{p.info['name'][:10]}\n(PID:{p.info['pid']})" for p in processes]
    cpu_usages = [p.info['cpu_percent'] for p in processes]

    bars = bar_ax.bar(names, cpu_usages, color=colors[:len(processes)], 
                     edgecolor='black', width=0.6)
    bar_ax.set_title('CPU Usage by Process', fontsize=12, weight='bold', pad=10)
    bar_ax.set_ylabel('CPU Usage (%)', fontsize=10)
    bar_ax.set_ylim(0, max(cpu_usages) + 10 if cpu_usages else 100)
    bar_ax.tick_params(axis='x', labelsize=8, rotation=0)
    bar_ax.tick_params(axis='y', labelsize=8)
    bar_ax.grid(axis='y', linestyle='--', alpha=0.6)

    for bar, usage in zip(bars, cpu_usages):
        bar_ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                   f"{usage:.1f}%", ha='center', va='bottom', 
                   fontsize=8, weight='bold')

def plot_pie_chart(processes):
    """Render the pie chart with perfect spacing."""
    pie_ax.clear()
    if not processes:
        return
        
    names = [p.info['name'][:10] for p in processes]
    cpu_usages = [max(p.info['cpu_percent'], 0.1) for p in processes]

    wedges, texts = pie_ax.pie(
        cpu_usages,
        colors=colors[:len(processes)],
        startangle=90,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
        textprops={'fontsize': 0}  # Hide inner labels
    )
    
    # Add white circle in center
    pie_ax.add_artist(plt.Circle((0, 0), 0.4, fc='white'))
    pie_ax.set_title('CPU Distribution', fontsize=12, weight='bold', pad=10)
    
    # Create compact legend with perfect spacing
    legend = pie_ax.legend(wedges, [f"{n}\n({u:.1f}%)" for n, u in zip(names, cpu_usages)],
                         loc='center left', 
                         fontsize=8, 
                         bbox_to_anchor=(1.1, 0.5),
                         frameon=False)

def update_memory_trend():
    """Update the memory usage trend graph with perfect spacing."""
    mem_ax.clear()
    mem = psutil.virtual_memory()
    memory_history.append(mem.percent)
    
    if len(memory_history) > MAX_HISTORY:
        memory_history.pop(0)
    
    mem_ax.plot(memory_history, color='#4D96FF', linewidth=1.5)
    mem_ax.fill_between(range(len(memory_history)), memory_history, 
                       color='#4D96FF', alpha=0.2)
    mem_ax.set_title('Memory Usage Trend', fontsize=12, weight='bold', pad=10)
    mem_ax.set_ylabel('Usage (%)', fontsize=10)
    mem_ax.set_xlabel('Time (updates)', fontsize=8)
    mem_ax.set_ylim(0, 100)
    mem_ax.tick_params(axis='both', labelsize=8)
    mem_ax.grid(True, linestyle='--', alpha=0.6)
    
    if memory_history:
        mem_ax.text(len(memory_history)-1, memory_history[-1], 
                   f"Current: {memory_history[-1]:.1f}%", 
                   ha='right', va='bottom', fontsize=8, weight='bold')

def update(frame):
    """Update function called by FuncAnimation."""
    try:
        top_processes = get_top_processes()
        display_process_table(top_processes)
        plot_pie_chart(top_processes)
        plot_bar_chart(top_processes)
        update_memory_trend()
        
        fig.suptitle('Real-Time Task Manager Simulation', 
                    fontsize=16, weight='bold', y=0.98)
        
    except Exception as e:
        print(f"Error updating: {e}")

# Configure to remove footer and toolbar
plt.rcParams['figure.constrained_layout.use'] = True
plt.rcParams['figure.constrained_layout.h_pad'] = 0.2
plt.rcParams['figure.constrained_layout.w_pad'] = 0.2

# Start animation
animation = FuncAnimation(fig, update, interval=1000)
plt.show()
