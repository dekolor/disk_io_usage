import psutil
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Threshold for disk I/O in bytes
DISK_USAGE_THRESHOLD = int(os.getenv('DISK_USAGE_THRESHOLD')) * 1024 * 1024  # Example: 50MB

# Function to send notification to Discord
def send_discord_notification(process_name, disk_io):
    data = {
        "content": f"⚠️ High disk usage detected!\n\n**Process**: {process_name}\n**Disk Usage**: {disk_io / (1024 * 1024):.2f} MB"
    }
    response = requests.post(os.getenv('DISCORD_WEBHOOK_URL'), json=data)
    if response.status_code == 204:
        print(f"Notification sent for {process_name}.")
    else:
        print(f"Failed to send notification. Status code: {response.status_code}")

# Main loop to monitor disk usage
def monitor_disk_usage():
    while True:
        # Iterate through all processes
        for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
            try:
                # Get disk I/O statistics for the process
                io_counters = proc.info['io_counters']
                if io_counters:
                    # Calculate total disk read + write
                    total_io = io_counters.read_bytes + io_counters.write_bytes
                    
                    # Check if the total disk usage exceeds the threshold
                    if total_io > DISK_USAGE_THRESHOLD:
                        send_discord_notification(proc.info['name'], total_io)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sleep for a while before checking again
        time.sleep(10)

if __name__ == "__main__":
    monitor_disk_usage()
