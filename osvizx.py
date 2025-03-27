import subprocess
import sys
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox

# Function to install required libraries if not found
def install_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

for package in ['psutil', 'matplotlib', 'seaborn']:
    install_package(package)

# Styling settings
sns.set_style("darkgrid")
plt.rcParams.update({
    "axes.facecolor": "#1E1E1E",
    "axes.edgecolor": "#444",
    "text.color": "#EEEEEE",
    "axes.labelcolor": "#EEEEEE",
    "xtick.color": "#EEEEEE",
    "ytick.color": "#EEEEEE",
    "grid.color": "#444",
    "figure.facecolor": "#1E1E1E"
})

# Create figure and subplots
fig, axes = plt.subplots(3, 2, figsize=(12, 10), gridspec_kw={'height_ratios': [0.6, 1, 1], 'wspace': 0.3, 'hspace': 0.6})
table_ax, pie_ax, bar_ax, mem_ax, disk_ax, net_ax = axes.flatten()

# Position adjustments
table_ax.set_position([0.05, 0.70, 0.50, 0.15])
pie_ax.set_position([0.50, 0.59, 0.5, 0.30])
bar_ax.set_position([0.05, 0.30, 0.45, 0.30])
mem_ax.set_position([0.6, 0.29, 0.37, 0.22])
disk_ax.set_position([0.07, 0.05, 0.24, 0.13])
net_ax.set_position([0.70, 0.05, 0.24, 0.13])

fig.suptitle('⚡ Real-Time Task Manager', fontsize=17, fontname="Segoe UI", weight='bold', color="#b5cdfa", y=0.94)

# Process limit control
textbox_ax = fig.add_axes([0.47, 0.15, 0.085, 0.03])
textbox = TextBox(textbox_ax, "Processes:", initial="5", color="black", hovercolor="#555")

# Global variables
process_limit = 5
MAX_HISTORY = 30
colors = sns.color_palette("coolwarm", 10)
prev_disk_io = psutil.disk_io_counters()
prev_net_io = psutil.net_io_counters()
update_interval = 1  # Seconds between updates

# Metric histories
memory_history = []
disk_read_history, disk_write_history = [], []
net_sent_history, net_recv_history = [], []

def update_process_limit(text):
    global process_limit
    try:
        process_limit = max(2, min(int(text), 9))
    except ValueError:
        textbox.set_val("5")
        process_limit = 5

textbox.on_submit(update_process_limit)

def get_top_processes():
    psutil.cpu_percent(interval=0.1)  # Ensures CPU measurement accuracy
    return sorted(
        [p for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
         if p.info['cpu_percent'] is not None],
        key=lambda p: p.info['cpu_percent'],
        reverse=True
    )[:process_limit]

def update_table():
    table_ax.clear()
    processes = get_top_processes()

    if not processes:
        table_ax.text(0.5, 0.5, "No Processes", fontsize=12, ha="center", color="black")
        return

    data = [[p.info['pid'], p.info['name'], f"{p.info['cpu_percent']:.1f}%", f"{p.info['memory_percent']:.1f}%"] 
            for p in processes]
    
    table_ax.axis("off")
    table = table_ax.table(
        cellText=data,
        colLabels=["PID", "Name", "CPU%", "Mem%"],
        cellLoc="center",
        loc="center",
        colColours=["#333333"]*4
    )

    for (row, col), cell in table.get_celld().items():
        cell.set_facecolor("#d1dae9" if row else "#333333")
        cell.set_text_props(color="black" if row else "white")

def update_bar_chart():
    bar_ax.clear()
    processes = get_top_processes()
    
    if not processes:
        bar_ax.text(0.5, 0.5, "No Data", fontsize=12, ha="center", color="white")
        return

    names = [p.info['name'][:10] for p in processes]
    cpu_usage = [p.info['cpu_percent'] for p in processes]
    
    bars = bar_ax.bar(names, cpu_usage, color=sns.color_palette("coolwarm", len(processes)))
    for bar, usage in zip(bars, cpu_usage):
        bar_ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{usage:.1f}%", 
                    ha='center', va='bottom', fontsize=10, color="white")
    
    bar_ax.set_title("🔥 Top CPU Processes", fontsize=12, weight="bold", color="#7597f6", pad=10)
    bar_ax.tick_params(axis="x", rotation=45)

def plot_pie_chart(processes):
    pie_ax.clear()
    if not processes:
        return

    names = [f"{p.info['name'][:10]} ({p.info['pid']})" for p in processes]
    cpu_usages = [max(p.info['cpu_percent'], 0.1) for p in processes]
    
    pie_ax.pie(cpu_usages, labels=names, colors=colors[:len(processes)], 
               startangle=90, wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
    pie_ax.set_title('🧩 CPU Distribution', fontsize=12, weight='bold', color="#7597f6", pad=10)

def update_memory_trend():
    mem_ax.clear()
    current_mem = psutil.virtual_memory().percent
    memory_history.append(current_mem)
    
    # Maintain fixed history length
    if len(memory_history) > MAX_HISTORY:
        memory_history.pop(0)
    
    # Create time axis with proper scaling
    time_window = len(memory_history) * update_interval
    x = np.linspace(-time_window, 0, len(memory_history))
    
    mem_ax.fill_between(x, memory_history, color='#4D96FF', alpha=0.4)
    mem_ax.plot(x, memory_history, color='#4D96FF', linewidth=2)
    mem_ax.text(0, current_mem, f"{current_mem:.1f}%", 
                ha='left', va='bottom', fontsize=10, color="white", weight="bold")
    
    # Axis configuration
    mem_ax.set_title('📈 Memory Usage Trend', fontsize=12, weight='bold', color="#7597f6", pad=10)
    mem_ax.set_ylim(0, 100)
    mem_ax.set_xlim(-time_window, 0)
    
    # Dynamic time labels
    mem_ax.set_xticks(np.linspace(-time_window, 0, 5))
    mem_ax.set_xticklabels([f"{-t:.0f}s" for t in np.linspace(time_window, 0, 5)])

def update_disk_activity():
    global prev_disk_io
    disk_ax.clear()
    
    current_disk_io = psutil.disk_io_counters()
    read_rate = (current_disk_io.read_bytes - prev_disk_io.read_bytes) / (1024**2 * update_interval)
    write_rate = (current_disk_io.write_bytes - prev_disk_io.write_bytes) / (1024**2 * update_interval)
    prev_disk_io = current_disk_io
    
    disk_read_history.append(read_rate)
    disk_write_history.append(write_rate)
    
    if len(disk_read_history) > MAX_HISTORY:
        disk_read_history.pop(0)
        disk_write_history.pop(0)
    
    disk_ax.plot(disk_read_history, color='cyan', label='Read MB/s')
    disk_ax.plot(disk_write_history, color='magenta', label='Write MB/s')
    disk_ax.legend()
    disk_ax.set_title('💾 Disk Activity', fontsize=12, weight='bold', color="#7597f6", pad=10)
    
    max_rate = max(max(disk_read_history + disk_write_history), 0.1)
    disk_ax.set_ylim(0, max_rate * 1.1)

def update_network_activity():
    global prev_net_io
    net_ax.clear()
    
    current_net_io = psutil.net_io_counters()
    sent_rate = (current_net_io.bytes_sent - prev_net_io.bytes_sent) / (1024**2 * update_interval)
    recv_rate = (current_net_io.bytes_recv - prev_net_io.bytes_recv) / (1024**2 * update_interval)
    prev_net_io = current_net_io
    
    net_sent_history.append(sent_rate)
    net_recv_history.append(recv_rate)
    
    if len(net_sent_history) > MAX_HISTORY:
        net_sent_history.pop(0)
        net_recv_history.pop(0)
    
    net_ax.plot(net_sent_history, color='lime', label='Upload MB/s')
    net_ax.plot(net_recv_history, color='orange', label='Download MB/s')
    net_ax.legend()
    net_ax.set_title('🌐 Network Activity', fontsize=12, weight='bold', color="#7597f6", pad=10)
    
    max_rate = max(max(net_sent_history + net_recv_history), 0.1)
    net_ax.set_ylim(0, max_rate * 1.1)

def update(frame):
    top_processes = get_top_processes()
    update_table()
    plot_pie_chart(top_processes)
    update_memory_trend()
    update_disk_activity()
    update_network_activity()
    update_bar_chart()
    plt.tight_layout()

animation = FuncAnimation(fig, update, interval=update_interval*1000, cache_frame_data=False)
plt.show()
