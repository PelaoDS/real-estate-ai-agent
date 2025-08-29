"""Metrics calculation for performance evaluation."""

import time
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for performance evaluation metrics."""
    accuracy: float
    latency_ms: float
    is_correct: bool
    reasoning: str
    query: str
    configuration: str


class MetricsCalculator:
    """Calculate performance metrics for agent evaluation."""
    
    def __init__(self):
        self.results = []
    
    def calculate_accuracy(self, evaluations: List[Dict[str, Any]]) -> float:
        """Calculate average accuracy across evaluations."""
        if not evaluations:
            return 0.0
        
        total_accuracy = sum(eval_result.get('accuracy', 0.0) for eval_result in evaluations)
        return total_accuracy / len(evaluations)
    
    def calculate_correctness_rate(self, evaluations: List[Dict[str, Any]]) -> float:
        """Calculate percentage of correct results."""
        if not evaluations:
            return 0.0
        
        correct_count = sum(1 for eval_result in evaluations if eval_result.get('is_correct', False))
        return correct_count / len(evaluations)
    
    def measure_latency(self, func, *args, **kwargs) -> tuple:
        """Measure function execution time in milliseconds."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        return result, latency_ms
    
    def compile_results(self, configuration_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, float]]:
        """Compile results across all configurations."""
        summary = {}
        
        for config_name, evaluations in configuration_results.items():
            if evaluations:
                summary[config_name] = {
                    "accuracy": self.calculate_accuracy(evaluations),
                    "correctness_rate": self.calculate_correctness_rate(evaluations),
                    "avg_latency_ms": sum(eval_result.get('latency_ms', 0) for eval_result in evaluations) / len(evaluations),
                    "total_queries": len(evaluations)
                }
            else:
                summary[config_name] = {
                    "accuracy": 0.0,
                    "correctness_rate": 0.0,
                    "avg_latency_ms": 0.0,
                    "total_queries": 0
                }
        
        return summary
    
    def print_comparison_report(self, summary: Dict[str, Dict[str, float]]):
        """Print formatted comparison report."""
        print("\n" + "="*80)
        print("PERFORMANCE COMPARISON REPORT")
        print("="*80)
        
        # Header
        print(f"{'Configuration':<30} {'Accuracy':<12} {'Correct %':<12} {'Latency (ms)':<15}")
        print("-" * 80)
        
        # Results
        for config_name, metrics in summary.items():
            accuracy = metrics['accuracy']
            correctness = metrics['correctness_rate'] * 100
            latency = metrics['avg_latency_ms']
            
            print(f"{config_name:<30} {accuracy:<12.3f} {correctness:<12.1f} {latency:<15.1f}")
        
        print("="*80)
        
        # Best performers
        best_accuracy = max(summary.items(), key=lambda x: x[1]['accuracy'])
        best_latency = min(summary.items(), key=lambda x: x[1]['avg_latency_ms'])
        
        print(f"\nBest Accuracy: {best_accuracy[0]} ({best_accuracy[1]['accuracy']:.3f})")
        print(f"Best Latency: {best_latency[0]} ({best_latency[1]['avg_latency_ms']:.1f}ms)")
    
    def export_results_to_json(self, summary: Dict[str, Dict[str, float]], filename: str):
        """Export results to JSON file."""
        import json
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nResults exported to {filename}")


# Global metrics calculator
metrics_calculator = MetricsCalculator()