import os
import sys
import ctypes
import platform
import psutil
import GPUtil
import logging
import threading
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
import torch.cuda
import torch.backends.cudnn as cudnn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('device_optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeviceMetrics:
    cpu_usage: float
    cpu_frequency: float
    memory_usage: float
    memory_available: float
    gpu_usage: Optional[float]
    gpu_memory_usage: Optional[float]
    disk_io: float
    network_io: float
    temperature: Dict[str, float]
    power_usage: Dict[str, float]

class DeviceOptimizer:
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == 'Windows'
        self.is_linux = self.system == 'Linux'
        self.is_mac = self.system == 'Darwin'
        
        # Initialize device monitoring
        self.monitoring_thread = None
        self.is_monitoring = False
        self.metrics_history = []
        self.max_history_size = 1000
        
        # Initialize resource pools
        self.thread_pool = ThreadPoolExecutor(max_workers=os.cpu_count())
        self.gpu_pool = None
        self._initialize_gpu_pool()
        
        # Initialize performance optimization
        self._optimize_system_settings()
        self._initialize_cuda()
        
        # Initialize resource limits
        self.cpu_limit = 0.8  # 80% CPU usage limit
        self.memory_limit = 0.8  # 80% memory usage limit
        self.gpu_limit = 0.8  # 80% GPU usage limit
        
    def _initialize_gpu_pool(self):
        """Initialize GPU resource pool if available"""
        try:
            if torch.cuda.is_available():
                self.gpu_pool = {
                    'device_count': torch.cuda.device_count(),
                    'current_device': torch.cuda.current_device(),
                    'device_properties': [torch.cuda.get_device_properties(i) for i in range(torch.cuda.device_count())]
                }
                logger.info(f"GPU pool initialized with {self.gpu_pool['device_count']} devices")
            else:
                logger.info("No CUDA-capable GPU available")
        except Exception as e:
            logger.error(f"Error initializing GPU pool: {e}")
            
    def _initialize_cuda(self):
        """Initialize CUDA settings for optimal performance"""
        try:
            if torch.cuda.is_available():
                # Enable cuDNN benchmarking for faster performance
                cudnn.benchmark = True
                
                # Set CUDA device properties
                for i in range(torch.cuda.device_count()):
                    torch.cuda.set_device(i)
                    torch.cuda.empty_cache()
                    
                # Set memory allocation strategy
                torch.cuda.set_per_process_memory_fraction(0.8)  # Use 80% of available GPU memory
                
                logger.info("CUDA initialized with optimal settings")
        except Exception as e:
            logger.error(f"Error initializing CUDA: {e}")
            
    def _optimize_system_settings(self):
        """Optimize system settings for better performance"""
        try:
            if self.is_windows:
                self._optimize_windows()
            elif self.is_linux:
                self._optimize_linux()
            elif self.is_mac:
                self._optimize_mac()
                
            # Set process priority
            self._set_process_priority()
            
            # Optimize memory management
            self._optimize_memory_management()
            
        except Exception as e:
            logger.error(f"Error optimizing system settings: {e}")
            
    def _optimize_windows(self):
        """Optimize Windows-specific settings"""
        try:
            # Set process priority
            pid = os.getpid()
            handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x00008000)  # ABOVE_NORMAL_PRIORITY_CLASS
            ctypes.windll.kernel32.CloseHandle(handle)
            
            # Optimize power settings
            os.system('powercfg /setactive SCHEME_BALANCED')
            
        except Exception as e:
            logger.error(f"Error optimizing Windows settings: {e}")
            
    def _optimize_linux(self):
        """Optimize Linux-specific settings"""
        try:
            # Set process priority using nice
            os.nice(-10)  # Higher priority
            
            # Optimize CPU governor
            os.system('echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor')
            
        except Exception as e:
            logger.error(f"Error optimizing Linux settings: {e}")
            
    def _optimize_mac(self):
        """Optimize macOS-specific settings"""
        try:
            # Set process priority
            os.nice(-10)  # Higher priority
            
        except Exception as e:
            logger.error(f"Error optimizing macOS settings: {e}")
            
    def _set_process_priority(self):
        """Set process priority based on OS"""
        try:
            if self.is_windows:
                pid = os.getpid()
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
                ctypes.windll.kernel32.SetPriorityClass(handle, 0x00008000)
                ctypes.windll.kernel32.CloseHandle(handle)
            else:
                os.nice(-10)
        except Exception as e:
            logger.error(f"Error setting process priority: {e}")
            
    def _optimize_memory_management(self):
        """Optimize memory management settings"""
        try:
            # Set memory allocation strategy
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.set_per_process_memory_fraction(0.8)
                
            # Set numpy memory management
            np.set_printoptions(threshold=1000)
            
        except Exception as e:
            logger.error(f"Error optimizing memory management: {e}")
            
    def start_monitoring(self):
        """Start device monitoring in a separate thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
    def stop_monitoring(self):
        """Stop device monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep history size limited
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                    
                # Check and optimize resources
                self._check_and_optimize_resources(metrics)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
    def _collect_metrics(self) -> DeviceMetrics:
        """Collect detailed device metrics"""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_frequency = cpu_freq.current if cpu_freq else 0
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available / (1024 * 1024 * 1024)  # GB
            
            # GPU metrics
            gpu_usage = None
            gpu_memory_usage = None
            if torch.cuda.is_available():
                gpu = GPUtil.getGPUs()[0]
                gpu_usage = gpu.load * 100
                gpu_memory_usage = gpu.memoryUtil * 100
                
            # Disk and network I/O
            disk_io = self._get_disk_io()
            network_io = self._get_network_io()
            
            # Temperature and power usage
            temperature = self._get_temperature()
            power_usage = self._get_power_usage()
            
            return DeviceMetrics(
                cpu_usage=cpu_usage,
                cpu_frequency=cpu_frequency,
                memory_usage=memory_usage,
                memory_available=memory_available,
                gpu_usage=gpu_usage,
                gpu_memory_usage=gpu_memory_usage,
                disk_io=disk_io,
                network_io=network_io,
                temperature=temperature,
                power_usage=power_usage
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return DeviceMetrics(0, 0, 0, 0, None, None, 0, 0, {}, {})
            
    def _get_disk_io(self) -> float:
        """Get disk I/O rate in MB/s"""
        try:
            disk_io = psutil.disk_io_counters()
            return (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)
        except Exception as e:
            logger.error(f"Error getting disk I/O: {e}")
            return 0.0
            
    def _get_network_io(self) -> float:
        """Get network I/O rate in MB/s"""
        try:
            net_io = psutil.net_io_counters()
            return (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
        except Exception as e:
            logger.error(f"Error getting network I/O: {e}")
            return 0.0
            
    def _get_temperature(self) -> Dict[str, float]:
        """Get device temperatures"""
        temperatures = {}
        try:
            if self.is_windows:
                # Windows temperature monitoring
                import wmi
                w = wmi.WMI(namespace="root\OpenHardwareMonitor")
                for sensor in w.Sensor():
                    if sensor.SensorType == 'Temperature':
                        temperatures[sensor.Name] = float(sensor.Value)
            elif self.is_linux:
                # Linux temperature monitoring
                for i in range(10):  # Check first 10 thermal zones
                    try:
                        with open(f'/sys/class/thermal/thermal_zone{i}/temp', 'r') as f:
                            temp = float(f.read()) / 1000.0
                            temperatures[f'zone{i}'] = temp
                    except:
                        continue
                        
            # GPU temperature if available
            if torch.cuda.is_available():
                gpu = GPUtil.getGPUs()[0]
                temperatures['gpu'] = gpu.temperature
                
        except Exception as e:
            logger.error(f"Error getting temperatures: {e}")
            
        return temperatures
        
    def _get_power_usage(self) -> Dict[str, float]:
        """Get device power usage"""
        power_usage = {}
        try:
            if self.is_windows:
                # Windows power monitoring
                import wmi
                w = wmi.WMI(namespace="root\OpenHardwareMonitor")
                for sensor in w.Sensor():
                    if sensor.SensorType == 'Power':
                        power_usage[sensor.Name] = float(sensor.Value)
            elif self.is_linux:
                # Linux power monitoring
                try:
                    with open('/sys/class/power_supply/BAT0/power_now', 'r') as f:
                        power_usage['battery'] = float(f.read()) / 1000000.0  # Convert to watts
                except:
                    pass
                    
            # GPU power usage if available
            if torch.cuda.is_available():
                gpu = GPUtil.getGPUs()[0]
                power_usage['gpu'] = gpu.power
                
        except Exception as e:
            logger.error(f"Error getting power usage: {e}")
            
        return power_usage
        
    def _check_and_optimize_resources(self, metrics: DeviceMetrics):
        """Check resource usage and optimize if needed"""
        try:
            # CPU optimization
            if metrics.cpu_usage > self.cpu_limit * 100:
                self._optimize_cpu()
                
            # Memory optimization
            if metrics.memory_usage > self.memory_limit * 100:
                self._optimize_memory()
                
            # GPU optimization
            if metrics.gpu_usage and metrics.gpu_usage > self.gpu_limit * 100:
                self._optimize_gpu()
                
            # Temperature optimization
            self._optimize_temperature(metrics.temperature)
            
            # Power optimization
            self._optimize_power(metrics.power_usage)
            
        except Exception as e:
            logger.error(f"Error optimizing resources: {e}")
            
    def _optimize_cpu(self):
        """Optimize CPU usage"""
        try:
            # Reduce thread pool size
            if self.thread_pool._max_workers > 2:
                self.thread_pool._max_workers = max(2, self.thread_pool._max_workers - 1)
                
            # Clear CPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            logger.error(f"Error optimizing CPU: {e}")
            
    def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            # Clear unused memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error optimizing memory: {e}")
            
    def _optimize_gpu(self):
        """Optimize GPU usage"""
        try:
            if torch.cuda.is_available():
                # Clear GPU cache
                torch.cuda.empty_cache()
                
                # Reduce GPU memory fraction
                current_fraction = torch.cuda.get_per_process_memory_fraction()
                if current_fraction > 0.5:
                    torch.cuda.set_per_process_memory_fraction(current_fraction - 0.1)
                    
        except Exception as e:
            logger.error(f"Error optimizing GPU: {e}")
            
    def _optimize_temperature(self, temperatures: Dict[str, float]):
        """Optimize device temperature"""
        try:
            # Check CPU temperature
            if 'cpu' in temperatures and temperatures['cpu'] > 80:
                self._reduce_cpu_load()
                
            # Check GPU temperature
            if 'gpu' in temperatures and temperatures['gpu'] > 80:
                self._reduce_gpu_load()
                
        except Exception as e:
            logger.error(f"Error optimizing temperature: {e}")
            
    def _optimize_power(self, power_usage: Dict[str, float]):
        """Optimize power usage"""
        try:
            # Check battery power
            if 'battery' in power_usage and power_usage['battery'] > 20:
                self._reduce_power_consumption()
                
            # Check GPU power
            if 'gpu' in power_usage and power_usage['gpu'] > 100:
                self._reduce_gpu_power()
                
        except Exception as e:
            logger.error(f"Error optimizing power: {e}")
            
    def _reduce_cpu_load(self):
        """Reduce CPU load to lower temperature"""
        try:
            # Reduce thread pool size
            if self.thread_pool._max_workers > 1:
                self.thread_pool._max_workers = max(1, self.thread_pool._max_workers - 1)
                
            # Set lower CPU priority
            if self.is_windows:
                pid = os.getpid()
                handle = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
                ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
                ctypes.windll.kernel32.CloseHandle(handle)
            else:
                os.nice(10)
                
        except Exception as e:
            logger.error(f"Error reducing CPU load: {e}")
            
    def _reduce_gpu_load(self):
        """Reduce GPU load to lower temperature"""
        try:
            if torch.cuda.is_available():
                # Clear GPU cache
                torch.cuda.empty_cache()
                
                # Reduce GPU memory usage
                current_fraction = torch.cuda.get_per_process_memory_fraction()
                if current_fraction > 0.3:
                    torch.cuda.set_per_process_memory_fraction(current_fraction - 0.1)
                    
        except Exception as e:
            logger.error(f"Error reducing GPU load: {e}")
            
    def _reduce_power_consumption(self):
        """Reduce power consumption"""
        try:
            # Reduce CPU frequency
            if self.is_linux:
                os.system('echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor')
                
            # Reduce GPU power limit if available
            if torch.cuda.is_available():
                gpu = GPUtil.getGPUs()[0]
                if hasattr(gpu, 'setPowerLimit'):
                    gpu.setPowerLimit(gpu.power * 0.8)  # Reduce to 80% of current power
                    
        except Exception as e:
            logger.error(f"Error reducing power consumption: {e}")
            
    def _reduce_gpu_power(self):
        """Reduce GPU power consumption"""
        try:
            if torch.cuda.is_available():
                # Reduce GPU memory usage
                current_fraction = torch.cuda.get_per_process_memory_fraction()
                if current_fraction > 0.3:
                    torch.cuda.set_per_process_memory_fraction(current_fraction - 0.1)
                    
                # Clear GPU cache
                torch.cuda.empty_cache()
                
        except Exception as e:
            logger.error(f"Error reducing GPU power: {e}")
            
    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop monitoring
            self.stop_monitoring()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear GPU resources
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            # Clear memory
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()

    def optimize_for_emotional_state(self, emotional_state: dict):
        """Dynamically adjust device optimization based on emotional/cognitive state."""
        try:
            # Example: If stress or anger is high, prioritize cooling and stability
            if emotional_state.get('angry', 0) > 0.7 or emotional_state.get('fear', 0) > 0.7:
                self.cpu_limit = 0.6
                self.memory_limit = 0.6
                self.gpu_limit = 0.6
                logger.info("Detected high stress/fear: Lowering resource limits for stability.")
            # If happy or focused, allow more aggressive optimization
            elif emotional_state.get('happy', 0) > 0.7 or emotional_state.get('neutral', 0) > 0.7:
                self.cpu_limit = 0.9
                self.memory_limit = 0.9
                self.gpu_limit = 0.9
                logger.info("Detected positive state: Raising resource limits for performance.")
            else:
                self.cpu_limit = 0.8
                self.memory_limit = 0.8
                self.gpu_limit = 0.8
        except Exception as e:
            logger.error(f"Error optimizing for emotional state: {e}") 