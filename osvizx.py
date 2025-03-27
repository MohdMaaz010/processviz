import subprocess
import sys
import psutil
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox, Button



# Function to install required libraries if not found
def install_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

for package in ['psutil', 'matplotlib', 'seaborn']:
    install_package(package)




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




fig, axes = plt.subplots(3, 2, figsize=(12, 10), gridspec_kw={'height_ratios': [0.6, 1, 1], 'wspace': 0.3, 'hspace': 0.6})
table_ax, pie_ax, bar_ax, mem_ax, disk_ax, net_ax = axes.flatten()

# Move everything slightly down by reducing the Y-coordinates
table_ax.set_position([0.05, 0.70, 0.50, 0.15])  
pie_ax.set_position([0.50, 0.59, 0.5, 0.30])  

bar_ax.set_position([0.05, 0.30, 0.45, 0.30])  
mem_ax.set_position([0.6, 0.29, 0.37, 0.22])  

disk_ax.set_position([0.07, 0.05, 0.24, 0.13])  
net_ax.set_position([0.70, 0.05, 0.24, 0.13])  

fig.suptitle('⚡ Real-Time Task Manager', fontsize=17,fontname="Segoe UI", weight='bold', color="#b5cdfa", y=0.94)

 


# Textbox & Button for process limit and termination
textbox_ax = fig.add_axes([0.47, 0.15, 0.085, 0.03])
textbox = TextBox(textbox_ax, "Processes:", initial="5", color="black", hovercolor="#555")

kill_textbox_ax = fig.add_axes([0.42, 0.08, 0.085, 0.03])
kill_textbox = TextBox(kill_textbox_ax, "Kill PID:", initial="", color="black", hovercolor="#555")

kill_button_ax = fig.add_axes([0.52, 0.08, 0.08, 0.03])
kill_button = Button(kill_button_ax, "Kill", color="red", hovercolor="darkred")

process_limit = 5
memory_history = []
disk_read_history, disk_write_history = [], []
net_sent_history, net_recv_history = [], []

MAX_HISTORY = 30
colors = sns.color_palette("coolwarm", 10)



# updated top process table for better visiblity
def update_process_limit(text):
    global process_limit
    try:
        value = int(text)
        process_limit = max(2, min(value, 9))
    except ValueError:
        textbox.set_val("5")
        process_limit = 5

textbox.on_submit(update_process_limit)


# fuction to kill a process
def kill_process(event):
    pid_text = kill_textbox.text.strip()
    try:
        pid = int(pid_text)
        p = psutil.Process(pid)
        p.terminate()
        print(f"Process {pid} terminated successfully.")
    except (psutil.NoSuchProcess, ValueError):
        print(f"Invalid PID: {pid_text}")

kill_button.on_clicked(kill_process)




def get_top_processes():
    psutil.cpu_percent(interval=0.1)
    return sorted(
        [p for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
         if p.info['cpu_percent'] is not None],
        key=lambda p: p.info['cpu_percent'],
        reverse=True
    )[:process_limit]



# fuction for realtime table updation
def update_table():
    table_ax.clear()
    processes = get_top_processes()

    if not processes:
        table_ax.text(0.5, 0.5, "No Processes", fontsize=12, ha="center", color="black")
        return

    data = [[p.info['pid'], p.info['name'], f"{p.info['cpu_percent']}%", f"{p.info['memory_percent']}%"] for p in processes]
    table_ax.axis("off")

    # Use the first color from the pie chart palette for the background
    light_blue = "#d1dae9"  # Lightest shade from `colors = sns.color_palette("coolwarm", 10)`

    table = table_ax.table(cellText=data, colLabels=["PID", "Name", "CPU%", "Mem%"], 
                           cellLoc="center", loc="center", colColours=["#333333"]*4)

    for (row, col), cell in table.get_celld().items():
        if row == 0:  # Header row
            cell.set_text_props(color="white")  # White text
            cell.set_facecolor("#333333")  # Grey background
        else:  # Data cells
            cell.set_text_props(color="black")  # Black text
            cell.set_facecolor(light_blue)  # Lightest blue background




def update_bar_chart():
    bar_ax.clear()
    processes = get_top_processes()

    if not processes:
        bar_ax.text(0.5, 0.5, "No Data", fontsize=12, ha="center", color="white")
        return

    names = [p.info['name'][:10] for p in processes]  # Process names
    cpu_usage = [p.info['cpu_percent'] for p in processes]  # CPU usage percentages

    bars = bar_ax.bar(names, cpu_usage, color=sns.color_palette("coolwarm", len(processes)))

    # Add percentage labels on top of each bar
    for bar, usage in zip(bars, cpu_usage):
        bar_ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{usage:.1f}%", 
                    ha='center', va='bottom', fontsize=10, color="white")

    bar_ax.set_title("🔥 Top CPU Processes", fontsize=12, weight="bold", color="#7597f6", pad=10)
    bar_ax.set_ylabel("CPU Usage (%)", color="white")
    
    # Ensure names are straight (no rotation)
    bar_ax.tick_params(axis="x", colors="white", rotation=0)  
    bar_ax.tick_params(axis="y", colors="white")





def plot_pie_chart(processes):
    pie_ax.clear()
    if not processes:
        return

    names = [p.info['name'][:10] for p in processes]
    cpu_usages = [max(p.info['cpu_percent'], 0.1) for p in processes]

    wedges, _ = pie_ax.pie(cpu_usages, colors=colors[:len(processes)], startangle=90,
                            wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
    pie_ax.set_title('🧩 CPU Distribution', fontsize=12, weight='bold', color="#7597f6", pad=10)
    
    # Add text list beside pie chart
    pie_ax.legend(names, loc="center left", bbox_to_anchor=(1, 0.5))




def update_memory_trend():
    mem_ax.clear()
    mem = psutil.virtual_memory()
    memory_history.append(mem.percent)
    if len(memory_history) > MAX_HISTORY:
        memory_history.pop(0)

    mem_ax.fill_between(range(len(memory_history)), memory_history, color='#4D96FF', alpha=0.4)
    mem_ax.plot(memory_history, color='#4D96FF', linewidth=2)

    # Add percentage label at the latest point
    mem_ax.text(len(memory_history) - 1, memory_history[-1], f"{memory_history[-1]:.1f}%", 
                ha='right', va='bottom', fontsize=10, color="white", weight="bold")

    mem_ax.set_title('📈 Memory Usage Trend', fontsize=12, weight='bold', color="#7597f6", pad=10)
    mem_ax.set_ylim(0, 100)




#fuction for disk activity monitering
def update_disk_activity():
    disk_ax.clear()
    disk = psutil.disk_io_counters()
    disk_read_history.append(disk.read_bytes / (1024 * 1024))
    disk_write_history.append(disk.write_bytes / (1024 * 1024))
    if len(disk_read_history) > MAX_HISTORY:
        disk_read_history.pop(0)
        disk_write_history.pop(0)
    
    disk_ax.plot(disk_read_history, color='cyan', linewidth=2, label='Read MB/s')
    disk_ax.plot(disk_write_history, color='magenta', linewidth=2, label='Write MB/s')
    disk_ax.legend()
    disk_ax.set_title('💾 Disk Activity', fontsize=12, weight='bold', color="#7597f6", pad=10)
    disk_ax.set_ylim(0, max(disk_read_history + disk_write_history) + 10 if disk_read_history else 10)

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
