"""
Script to analyze the execution time of each step in the report generation pipeline
across different report sizes.

This script reads the hierarchical_status.json files from completed reports and
extracts timing information for each step, correlating it with the input size.
"""

import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import csv
from typing import Dict, List, Tuple, Any

import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.config import settings

def count_comments_in_report(report_dir: Path) -> int:
    """
    Count the number of comments in a report by reading the input CSV file.
    
    Args:
        report_dir: Path to the report directory
        
    Returns:
        int: Number of comments in the report
    """
    input_file = None
    report_slug = report_dir.name
    
    potential_input = settings.INPUT_DIR / f"{report_slug}.csv"
    if potential_input.exists():
        input_file = potential_input
    
    if input_file is None:
        for file in report_dir.glob("*.csv"):
            if "input" in file.name.lower() or "comments" in file.name.lower():
                input_file = file
                break
    
    if input_file is None:
        print(f"Could not find input file for report {report_slug}")
        return 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            count = sum(1 for _ in reader)
            return count
    except Exception as e:
        print(f"Error reading input file for report {report_slug}: {e}")
        return 0

def get_report_metadata(report_dir: Path) -> Dict[str, Any]:
    """
    Get metadata about a report from its status file.
    
    Args:
        report_dir: Path to the report directory
        
    Returns:
        dict: Report metadata including slug, title, and creation time
    """
    status_file = report_dir / "hierarchical_status.json"
    if not status_file.exists():
        return {}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
            
        return {
            "slug": report_dir.name,
            "title": status.get("question", "Unknown"),
            "created_at": status.get("start_time", "Unknown"),
            "status": status.get("status", "Unknown")
        }
    except Exception as e:
        print(f"Error reading status file for report {report_dir.name}: {e}")
        return {}

def get_step_durations(report_dir: Path) -> Dict[str, float]:
    """
    Extract the duration of each step from a report's status file.
    
    Args:
        report_dir: Path to the report directory
        
    Returns:
        dict: Dictionary mapping step names to durations in seconds
    """
    status_file = report_dir / "hierarchical_status.json"
    if not status_file.exists():
        return {}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
            
        durations = {}
        for job in status.get("completed_jobs", []):
            step = job.get("step")
            duration = job.get("duration")
            if step and duration is not None:
                durations[step] = duration
                
        return durations
    except Exception as e:
        print(f"Error reading status file for report {report_dir.name}: {e}")
        return {}

def analyze_reports() -> pd.DataFrame:
    """
    Analyze all reports in the report directory and collect timing data.
    
    Returns:
        pd.DataFrame: DataFrame containing timing data for all reports
    """
    report_data = []
    
    report_dirs = [d for d in settings.REPORT_DIR.iterdir() if d.is_dir()]
    
    for report_dir in report_dirs:
        status_file = report_dir / "hierarchical_status.json"
        if not status_file.exists():
            continue
            
        metadata = get_report_metadata(report_dir)
        if not metadata or metadata.get("status") != "completed":
            continue
            
        comment_count = count_comments_in_report(report_dir)
        
        durations = get_step_durations(report_dir)
        if not durations:
            continue
            
        report_data.append({
            "slug": metadata.get("slug", "Unknown"),
            "title": metadata.get("title", "Unknown"),
            "created_at": metadata.get("created_at", "Unknown"),
            "comment_count": comment_count,
            **durations
        })
    
    if report_data:
        df = pd.DataFrame(report_data)
        return df
    else:
        return pd.DataFrame()

def generate_summary(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Generate a summary of timing data by input size ranges.
    
    Args:
        df: DataFrame containing timing data
        
    Returns:
        dict: Summary statistics by input size range
    """
    if df.empty:
        return {}
        
    size_ranges = [(0, 50), (51, 100), (101, 200), (201, 500), (501, 1000), (1001, float('inf'))]
    
    step_names = [col for col in df.columns if col not in ["slug", "title", "created_at", "comment_count"]]
    
    summary = {}
    
    for start, end in size_ranges:
        range_label = f"{start}-{end if end != float('inf') else '+'}"
        
        range_df = df[(df["comment_count"] >= start) & (df["comment_count"] <= end)]
        
        if range_df.empty:
            continue
            
        avg_durations = {}
        for step in step_names:
            if step in range_df.columns:
                avg_durations[step] = range_df[step].mean()
                
        total_avg = sum(avg_durations.values())
        
        summary[range_label] = {
            "count": len(range_df),
            "avg_comment_count": range_df["comment_count"].mean(),
            "total_avg_duration": total_avg,
            "steps": avg_durations
        }
    
    return summary

def format_time(seconds: float) -> str:
    """
    Format time in seconds to a human-readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string (e.g., "2m 30s")
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def main():
    print("Analyzing report timing data...")
    
    df = analyze_reports()
    
    if df.empty:
        print("No report data found.")
        return
    
    print(f"Found {len(df)} completed reports.")
    
    summary = generate_summary(df)
    
    print("\n=== Summary by Input Size ===")
    for size_range, data in summary.items():
        print(f"\nInput Size: {size_range} comments ({data['count']} reports, avg {data['avg_comment_count']:.1f} comments)")
        print(f"Total Average Duration: {format_time(data['total_avg_duration'])}")
        
        print("\nStep Durations:")
        if isinstance(data['steps'], dict):
            for step, duration in data['steps'].items():
                print(f"  - {step}: {format_time(duration)}")
        else:
            print("  No step duration data available.")
    
    output_file = Path(__file__).parent / "report_timing_analysis.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDetailed data saved to {output_file}")
    
    try:
        plt.figure(figsize=(12, 8))
        
        step_names = [col for col in df.columns if col not in ["slug", "title", "created_at", "comment_count"]]
        
        ranges = list(summary.keys())
        
        bottom = [0] * len(ranges)
        
        for step in step_names:
            values = []
            for size_range in ranges:
                steps_data = summary[size_range]['steps']
                if isinstance(steps_data, dict) and step in steps_data:
                    values.append(steps_data[step] / 60)  # Convert to minutes
                else:
                    values.append(0)
            plt.bar(ranges, values, bottom=bottom, label=step)
            bottom = [b + v for b, v in zip(bottom, values)]
        
        plt.xlabel('Input Size (Number of Comments)')
        plt.ylabel('Average Duration (minutes)')
        plt.title('Average Report Generation Time by Input Size and Step')
        plt.legend()
        plt.tight_layout()
        
        chart_file = Path(__file__).parent / "report_timing_chart.png"
        plt.savefig(chart_file)
        print(f"Chart saved to {chart_file}")
        
    except Exception as e:
        print(f"Could not generate visualization: {e}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
