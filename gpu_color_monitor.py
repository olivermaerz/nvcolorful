#!/usr/bin/env python3
"""
nvcolorful - NVIDIA GPU Color Monitor for RGB Fans
Monitors GPU usage and updates liquidctl fan colors accordingly.
Dark blue for low usage, red for high usage.
"""

import subprocess
import time
import sys
import logging
import os
from typing import Tuple

try:
    import pynvml
except ImportError:
    print("Error: pynvml not installed. Install with: pip install nvidia-ml-py")
    sys.exit(1)

# Configure logging
log_handlers = [logging.StreamHandler()]
try:
    log_handlers.append(logging.FileHandler('/var/log/gpu_color_monitor.log'))
except (PermissionError, OSError):
    # Fallback to home directory if /var/log is not writable
    home_log = os.path.expanduser('~/gpu_color_monitor.log')
    log_handlers.append(logging.FileHandler(home_log))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)

# GPU index to monitor (0 is the first GPU change this to the GPU you want to monitor)
GPU_INDEX = 0

# Color definitions (RGB values) - you can change these to your liking
DARK_BLUE = (0, 0, 139)  # Dark blue for low usage
DARK_RED = (139, 0, 0)   # Dark red for high usage

# Update interval in seconds
UPDATE_INTERVAL = 2

def hex_color(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def interpolate_color(usage: float) -> str:
    """
    Interpolate between dark blue and dark red based on GPU usage.
    
    Args:
        usage: GPU usage percentage (0-100)
    
    Returns:
        Hex color string
    """
    # Clamp usage between 0 and 100
    usage = max(0, min(100, usage))
    
    # Normalize to 0-1 range
    factor = usage / 100.0
    
    # Interpolate RGB values
    r = int(DARK_BLUE[0] + (DARK_RED[0] - DARK_BLUE[0]) * factor)
    g = int(DARK_BLUE[1] + (DARK_RED[1] - DARK_BLUE[1]) * factor)
    b = int(DARK_BLUE[2] + (DARK_RED[2] - DARK_BLUE[2]) * factor)
    
    color = (r, g, b)
    return hex_color(color)

def get_gpu_usage(handle) -> float:
    """
    Get GPU utilization percentage for the specified GPU handle.
    
    Args:
        handle: NVML device handle (obtained from pynvml)
    
    Returns:
        GPU usage percentage (0-100)
    """
    try:
        utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
        return float(utilization.gpu)
    except Exception as e:
        logging.error(f"Error getting GPU usage: {e}")
        raise


def set_liquidctl_color(color: str) -> bool:
    """
    Set liquidctl color using sudo.
    
    Args:
        color: Hex color string (e.g., "#ff0000")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["sudo", "liquidctl", "set", "sync", "color", "fixed", color]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logging.debug(f"Successfully set color to {color}")
            return True
        else:
            logging.error(f"liquidctl failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logging.error("liquidctl command timed out")
        return False
    except Exception as e:
        logging.error(f"Error setting liquidctl color: {e}")
        return False


def main():
    """Main monitoring loop."""
    logging.info("Starting GPU color monitor")
    
    # Initialize NVML and get GPU handle
    handle = None
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(GPU_INDEX)
        logging.info(f"Monitoring GPU #{GPU_INDEX}")
    except Exception as e:
        logging.error(f"Failed to initialize NVML: {e}")
        sys.exit(1)
    
    last_color = None
    
    try:
        while True:
            try:
                # Get GPU usage
                usage = get_gpu_usage(handle)
                
                # Calculate color based on usage
                color = interpolate_color(usage)
                
                # Only update if color changed (to avoid unnecessary calls)
                if color != last_color:
                    logging.info(f"GPU usage: {usage:.1f}% - Setting color to {color}")
                    if set_liquidctl_color(color):
                        last_color = color
                    else:
                        logging.warning("Failed to set color, will retry on next iteration")
                
                # Wait before next check
                time.sleep(UPDATE_INTERVAL)
                
            except KeyboardInterrupt:
                logging.info("Received interrupt signal, shutting down")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(UPDATE_INTERVAL)  # Wait before retrying
                
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception as e:
            logging.debug(f"Error shutting down NVML: {e}")
        logging.info("GPU color monitor stopped")


if __name__ == "__main__":
    main()
