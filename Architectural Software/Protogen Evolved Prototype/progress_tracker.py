"""
Progress Tracker Module for Protogen
Provides real-time progress updates and transparency for all operations.
"""

import sys
import time
from typing import Optional, Callable

class ProgressTracker:
    """
    Tracks and displays progress for long-running operations.
    Provides transparency about what the system is doing.
    """
    
    def __init__(self, verbose: bool = True, use_color: bool = True):
        """
        Initialize the progress tracker.
        
        Args:
            verbose: Whether to show detailed progress information
            use_color: Whether to use ANSI color codes (disable for Windows CMD)
        """
        self.verbose = verbose
        self.use_color = use_color and sys.stdout.isatty()
        self.current_operation = None
        self.start_time = None
        
        # ANSI color codes
        self.colors = {
            'green': '\033[92m',
            'blue': '\033[94m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'cyan': '\033[96m',
            'magenta': '\033[95m',
            'reset': '\033[0m',
            'bold': '\033[1m'
        } if self.use_color else {k: '' for k in ['green', 'blue', 'yellow', 'red', 'cyan', 'magenta', 'reset', 'bold']}
    
    def start_operation(self, operation_name: str):
        """Start tracking a new operation."""
        self.current_operation = operation_name
        self.start_time = time.time()
        if self.verbose:
            print(f"\n{self.colors['cyan']}▶ {operation_name}{self.colors['reset']}")
    
    def end_operation(self, success: bool = True):
        """End the current operation and show elapsed time."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            status = f"{self.colors['green']}✓" if success else f"{self.colors['red']}✗"
            print(f"{status} {self.current_operation} {self.colors['reset']}({elapsed:.2f}s)")
        self.current_operation = None
        self.start_time = None
    
    def update_status(self, message: str, level: str = 'info'):
        """
        Update the current status with a message.
        
        Args:
            message: Status message to display
            level: Message level ('info', 'warning', 'error', 'success')
        """
        if not self.verbose:
            return
        
        icons = {
            'info': '  ℹ',
            'warning': '  ⚠',
            'error': '  ✗',
            'success': '  ✓',
            'process': '  ⚙'
        }
        
        colors = {
            'info': self.colors['blue'],
            'warning': self.colors['yellow'],
            'error': self.colors['red'],
            'success': self.colors['green'],
            'process': self.colors['magenta']
        }
        
        icon = icons.get(level, '  •')
        color = colors.get(level, '')
        
        print(f"{color}{icon} {message}{self.colors['reset']}")
    
    def show_progress_bar(self, current: int, total: int, prefix: str = '', 
                         suffix: str = '', length: int = 50, fill: str = '█'):
        """
        Display a progress bar.
        
        Args:
            current: Current progress value
            total: Total value (100%)
            prefix: Text before the progress bar
            suffix: Text after the progress bar
            length: Character length of the bar
            fill: Fill character for the bar
        """
        if not self.verbose or total == 0:
            return
        
        percent = min(100, (100 * current) // total)
        filled_length = length * current // total
        bar = fill * filled_length + '-' * (length - filled_length)
        
        # Calculate ETA if we have start time
        eta_str = ''
        if self.start_time and current > 0:
            elapsed = time.time() - self.start_time
            rate = current / elapsed
            remaining = (total - current) / rate if rate > 0 else 0
            eta_str = f" ETA: {remaining:.1f}s"
        
        print(f'\r{prefix} |{self.colors["green"]}{bar}{self.colors["reset"]}| {percent}% {suffix}{eta_str}', end='')
        
        if current >= total:
            print()  # New line when complete
    
    def log_decision(self, decision: str, reason: str):
        """
        Log a system decision with its reasoning for transparency.
        
        Args:
            decision: The decision made
            reason: Why the decision was made
        """
        if self.verbose:
            print(f"{self.colors['magenta']}  🔍 DECISION:{self.colors['reset']} {decision}")
            print(f"{self.colors['blue']}     REASON:{self.colors['reset']} {reason}")
    
    def log_action(self, action: str, details: Optional[str] = None):
        """
        Log a system action for transparency.
        
        Args:
            action: The action being taken
            details: Additional details about the action
        """
        if self.verbose:
            print(f"{self.colors['cyan']}  ⚡ ACTION:{self.colors['reset']} {action}")
            if details:
                print(f"{self.colors['blue']}     DETAILS:{self.colors['reset']} {details}")
    
    def show_metrics(self, metrics: dict):
        """
        Display a set of metrics in a formatted way.
        
        Args:
            metrics: Dictionary of metric names and values
        """
        if not self.verbose:
            return
        
        print(f"\n{self.colors['bold']}📊 Metrics:{self.colors['reset']}")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {self.colors['green']}{value:.4f}{self.colors['reset']}")
            else:
                print(f"  {key}: {self.colors['green']}{value}{self.colors['reset']}")
    
    def show_summary(self, title: str, items: dict):
        """
        Display a summary section.
        
        Args:
            title: Title of the summary
            items: Dictionary of items to display
        """
        if not self.verbose:
            return
        
        print(f"\n{self.colors['bold']}{self.colors['cyan']}═══ {title} ═══{self.colors['reset']}")
        for key, value in items.items():
            print(f"  {key}: {self.colors['yellow']}{value}{self.colors['reset']}")
    
    def process_with_progress(self, items: list, process_func: Callable, 
                             operation_name: str = "Processing"):
        """
        Process a list of items with progress tracking.
        
        Args:
            items: List of items to process
            process_func: Function to call for each item
            operation_name: Name of the operation for display
        
        Returns:
            List of results from process_func
        """
        self.start_operation(operation_name)
        results = []
        total = len(items)
        
        for i, item in enumerate(items, 1):
            self.show_progress_bar(i, total, prefix=operation_name, 
                                  suffix=f"({i}/{total})")
            result = process_func(item)
            results.append(result)
        
        self.end_operation(success=True)
        return results


class FileProgressTracker(ProgressTracker):
    """
    Specialized progress tracker for file processing operations.
    """
    
    def process_file_with_progress(self, file_path: str, chunk_size: int = 1024):
        """
        Read a file and show progress.
        
        Args:
            file_path: Path to the file to read
            chunk_size: Size of chunks to read (for progress updates)
        
        Yields:
            Chunks of file content
        """
        import os
        
        file_size = os.path.getsize(file_path)
        bytes_read = 0
        
        self.start_operation(f"Reading file: {os.path.basename(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                bytes_read += len(chunk.encode('utf-8'))
                self.show_progress_bar(bytes_read, file_size, 
                                      prefix="Reading", 
                                      suffix=f"{bytes_read}/{file_size} bytes")
                yield chunk
        
        self.end_operation(success=True)
    
    def process_text_with_progress(self, text: str, chunk_size: int = 1000):
        """
        Process text in chunks with progress tracking.
        
        Args:
            text: Text to process
            chunk_size: Size of chunks (in characters)
        
        Yields:
            Chunks of text
        """
        total_length = len(text)
        processed = 0
        
        self.start_operation(f"Processing text ({total_length} characters)")
        
        for i in range(0, total_length, chunk_size):
            chunk = text[i:i + chunk_size]
            processed += len(chunk)
            
            self.show_progress_bar(processed, total_length,
                                  prefix="Processing",
                                  suffix=f"{processed}/{total_length} chars")
            yield chunk
        
        self.end_operation(success=True)


# Example usage
if __name__ == "__main__":
    # Test the progress tracker
    tracker = ProgressTracker(verbose=True, use_color=True)
    
    # Test operation tracking
    tracker.start_operation("Initializing System")
    time.sleep(0.5)
    tracker.update_status("Loading configuration", level='info')
    time.sleep(0.5)
    tracker.update_status("Configuration loaded successfully", level='success')
    tracker.end_operation(success=True)
    
    # Test progress bar
    tracker.start_operation("Processing Data")
    for i in range(101):
        tracker.show_progress_bar(i, 100, prefix="Progress", suffix="Complete")
        time.sleep(0.02)
    tracker.end_operation(success=True)
    
    # Test decision logging
    tracker.log_decision(
        "Prune weak edges from knowledge graph",
        "Entropy exceeds threshold (5.2 > 5.0), indicating chaos"
    )
    
    # Test action logging
    tracker.log_action(
        "Creating new concept node",
        "Concept: 'KNOWLEDGE', Hash: a3f2b1c4"
    )
    
    # Test metrics display
    tracker.show_metrics({
        "Coherence (Entropy)": 4.2567,
        "Benevolence Index": 0.8234,
        "Total Concepts": 156,
        "Total Links": 342
    })
    
    # Test summary
    tracker.show_summary("Final State", {
        "Status": "READY",
        "Processing Time": "2.34s",
        "Concepts Created": 25,
        "Patterns Discovered": 8
    })
