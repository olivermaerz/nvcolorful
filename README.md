# nvcolorful 
## NVIDIA GPU Color Monitor for RGB Fans

nvcolorful is a Python script that monitors NVIDIA GPU usage and dynamically changes fan/RGB colors via liquidctl based on GPU utilization.

## Why nvcolorful?

Two birds with one stone: When I built a PC to run LLMs/Ollama, I found the case fans and CPU fans with their rainbow color animation more than annoying. And sometimes I wasn't sure if an LLM model was really utilizing the GPU or just running on the CPU. 

That's when I thought: How cool would it be if the color of the RGB fans changes based on the utilization of the GPU? The fans show a steady deep blue when the GPU is at 0% usage, a steady dark red when it's fully used, and smoothly transitions between colors based on utilization.


## Features

- Monitors GPU #0 (you can change the GPU # in the script)
- Changes colors between dark blue (low usage) and dark red (high usage)
- Updates colors via liquidctl 
- Suitable for running at boot via crontab

## Installation / Setup

> **Note:** These instructions are for Ubuntu Server 24.04 LTS. If you're using a different distribution, adjust the package installation commands accordingly.

### Step 1: Install Prerequisites

Install liquidctl (required for controlling RGB fans):
```bash
sudo apt install liquidctl
```

Install Python and pip (if not already installed):
```bash
sudo apt install python3-pip python3-venv
```

### Step 2: Set Up Python Virtual Environment

Create a virtual environment (replace `/path/to/venv` with your desired location):
```bash
python3 -m venv /path/to/venv
```

Activate the virtual environment and install dependencies:
```bash
source /path/to/venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Step 3: Make Script Executable

```bash
chmod +x gpu_color_monitor.py
```

### Step 4: Configure Sudo (Only if running crontab as non-root user)

If you plan to run the script via crontab as a regular user (not root), you need to set up passwordless sudo for liquidctl:

```bash
sudo visudo
```

Add this line (replace `username` with your actual username):
```
username ALL=(ALL) NOPASSWD: /usr/bin/liquidctl *
```

**Note:** If you run crontab as root (using `sudo crontab -e`), you can skip this step.

### Step 5: Test the Script

Test the script manually to make sure everything works:
```bash
/path/to/venv/bin/python3 gpu_color_monitor.py
```

Press `Ctrl+C` to stop the script when you're satisfied it's working.

## Crontab Setup (Run at Boot)

To automatically start the script when your system boots, add it to crontab.

### Option 1: Run as Root (Recommended - No sudo setup needed)

```bash
sudo crontab -e
```

Add this line (replace paths with your actual paths):
```
@reboot /path/to/venv/bin/python3 /path/to/nvcolorful/gpu_color_monitor.py >> /var/log/gpu_color_monitor_cron.log 2>&1
```

**Advantage:** Runs as root, so no passwordless sudo configuration needed.

### Option 2: Run as Regular User

If you prefer to run as your regular user (and completed Step 4 above):

```bash
crontab -e
```

Add the same line as above:
```
@reboot /path/to/venv/bin/python3 /path/to/nvcolorful/gpu_color_monitor.py >> /var/log/gpu_color_monitor_cron.log 2>&1
```

**Important:** Replace:
- `/path/to/venv/bin/python3` with the actual path to your virtual environment's Python executable
- `/path/to/nvcolorful` with the actual path to the nvcolorful directory


## Configuration

You can modify these variables in the script:

- `GPU_INDEX`: Which GPU to monitor (default: 0)
- `UPDATE_INTERVAL`: How often to check GPU usage in seconds (default: 2)
- `DARK_BLUE`: RGB tuple for low usage color (default: (0, 0, 139))
- `DARK_RED`: RGB tuple for high usage color (default: (139, 0, 0))

## Logging

The script logs to:
- `/var/log/gpu_color_monitor.log` - Main log file
- Console output (when run manually)

## Troubleshooting

1. **Permission denied errors**: 
   - If running as a regular user, make sure you completed Step 4 (passwordless sudo setup)
   - Or switch to running crontab as root using `sudo crontab -e`

2. **Module not found (nvidia-ml-py)**: 
   - Make sure you activated your virtual environment and installed dependencies: `pip install -r requirements.txt`
   - Verify you're using the correct Python from your venv: `/path/to/venv/bin/python3`

3. **liquidctl not found**: 
   - Install liquidctl: `sudo apt install liquidctl`
   - Verify it's in your PATH: `which liquidctl`

4. **GPU not detected**: 
   - Make sure NVIDIA drivers are installed: `nvidia-smi` should work
   - Verify the GPU is accessible: `nvidia-smi` should show your GPU
   - Check that `pynvml` can access the GPU by running the script manually

5. **Script doesn't start at boot**:
   - Check crontab logs: `cat /var/log/gpu_color_monitor_cron.log`
   - Verify the paths in your crontab entry are correct and absolute
   - Make sure the script is executable: `chmod +x gpu_color_monitor.py`
