"""
Performance monitoring module for RAG components.
"""

import time
import psutil
import logging
from functools import wraps
from typing import Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

class PerformanceMonitor:
    """
    Monitors and logs performance metrics for RAG operations.
    """
    
    def __init__(self):
        self.metrics_history = []
        self._process = psutil.Process()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self._process.memory_info().rss / 1024 / 1024
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage."""
        return self._process.cpu_percent()
    
    def track_operation(self, operation_name: str):
        """Decorator to track performance metrics of an operation."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Start tracking
                start_time = datetime.now()
                start_memory = self._get_memory_usage()
                
                try:
                    # Execute operation
                    result = func(*args, **kwargs)
                    
                    # Collect metrics
                    end_time = datetime.now()
                    duration_ms = (end_time - start_time).total_seconds() * 1000
                    memory_usage = self._get_memory_usage()
                    cpu_usage = self._get_cpu_percent()
                    
                    # Create metrics record
                    metrics = PerformanceMetrics(
                        operation=operation_name,
                        start_time=start_time,
                        end_time=end_time,
                        duration_ms=duration_ms,
                        memory_usage_mb=memory_usage,
                        cpu_percent=cpu_usage,
                        additional_data={
                            'memory_change_mb': memory_usage - start_memory
                        }
                    )
                    
                    # Log metrics
                    self._log_metrics(metrics)
                    
                    # Store metrics
                    self.metrics_history.append(metrics)
                    
                    return result
                
                except Exception as e:
                    logger.error(f"Error in {operation_name}: {str(e)}")
                    raise
            
            return wrapper
        return decorator
    
    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics."""
        logger.info(
            f"Operation: {metrics.operation}\n"
            f"Duration: {metrics.duration_ms:.2f}ms\n"
            f"Memory Usage: {metrics.memory_usage_mb:.2f}MB\n"
            f"CPU Usage: {metrics.cpu_percent:.2f}%\n"
            f"Additional Data: {metrics.additional_data}"
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary statistics of collected metrics."""
        if not self.metrics_history:
            return {}
        
        durations = [m.duration_ms for m in self.metrics_history]
        memory_usages = [m.memory_usage_mb for m in self.metrics_history]
        cpu_usages = [m.cpu_percent for m in self.metrics_history]
        
        return {
            'total_operations': len(self.metrics_history),
            'duration_ms': {
                'mean': np.mean(durations),
                'median': np.median(durations),
                'std': np.std(durations),
                'min': np.min(durations),
                'max': np.max(durations)
            },
            'memory_mb': {
                'mean': np.mean(memory_usages),
                'median': np.median(memory_usages),
                'std': np.std(memory_usages),
                'min': np.min(memory_usages),
                'max': np.max(memory_usages)
            },
            'cpu_percent': {
                'mean': np.mean(cpu_usages),
                'median': np.median(cpu_usages),
                'std': np.std(cpu_usages),
                'min': np.min(cpu_usages),
                'max': np.max(cpu_usages)
            }
        }

# Global monitor instance
monitor = PerformanceMonitor()

class VectorStoreMetrics:
    """
    Tracks vector store specific metrics.
    """
    
    def __init__(self):
        self.query_times = []
        self.embedding_times = []
        self.index_sizes = []
    
    @monitor.track_operation("vector_store_query")
    def track_query(self, query_text: str, num_results: int):
        """Track vector store query performance."""
        start_time = time.time()
        
        # Return timing context
        class TimingContext:
            def __init__(self, metrics, start):
                self.metrics = metrics
                self.start = start
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start
                self.metrics.query_times.append({
                    'duration': duration,
                    'query_length': len(query_text),
                    'num_results': num_results,
                    'timestamp': datetime.now()
                })
        
        return TimingContext(self, start_time)
    
    @monitor.track_operation("vector_store_embedding")
    def track_embedding(self, text_length: int):
        """Track embedding generation performance."""
        start_time = time.time()
        
        class TimingContext:
            def __init__(self, metrics, start):
                self.metrics = metrics
                self.start = start
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start
                self.metrics.embedding_times.append({
                    'duration': duration,
                    'text_length': text_length,
                    'timestamp': datetime.now()
                })
        
        return TimingContext(self, start_time)
    
    def update_index_size(self, num_vectors: int, dimension: int):
        """Track vector store index size."""
        self.index_sizes.append({
            'num_vectors': num_vectors,
            'dimension': dimension,
            'timestamp': datetime.now()
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of vector store metrics."""
        if not any([self.query_times, self.embedding_times, self.index_sizes]):
            return {}
        
        summary = {}
        
        if self.query_times:
            durations = [q['duration'] for q in self.query_times]
            summary['query_performance'] = {
                'mean_duration': np.mean(durations),
                'median_duration': np.median(durations),
                'std_duration': np.std(durations),
                'total_queries': len(self.query_times)
            }
        
        if self.embedding_times:
            durations = [e['duration'] for e in self.embedding_times]
            summary['embedding_performance'] = {
                'mean_duration': np.mean(durations),
                'median_duration': np.median(durations),
                'std_duration': np.std(durations),
                'total_embeddings': len(self.embedding_times)
            }
        
        if self.index_sizes:
            latest_size = self.index_sizes[-1]
            summary['index_size'] = {
                'num_vectors': latest_size['num_vectors'],
                'dimension': latest_size['dimension'],
                'last_updated': latest_size['timestamp']
            }
        
        return summary

# Global vector store metrics instance
vector_metrics = VectorStoreMetrics()
