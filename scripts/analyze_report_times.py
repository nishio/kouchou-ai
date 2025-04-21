"""
Script to analyze the execution time of each step in the report generation pipeline
across different report sizes.

This script reads the hierarchical_status.json files from completed reports and
extracts timing information for each step, correlating it with the input size.
"""

import json
import os
import pandas as pd
from pathlib import Path
import csv
from typing import Dict, List, Tuple, Any

import sys
REPORT_DIR = Path(__file__).parent.parent / "server/broadlistening/pipeline/outputs"
INPUT_DIR = Path(__file__).parent.parent / "server/broadlistening/pipeline/inputs"

def analyze_comments_in_report(report_dir: Path) -> Dict[str, float]:
    """
    Count the number of comments and calculate average comment length in a report.
    
    Args:
        report_dir: Path to the report directory
        
    Returns:
        dict: Dictionary with comment count and average length
    """
    input_file = None
    report_slug = report_dir.name
    
    potential_input = INPUT_DIR / f"{report_slug}.csv"
    if potential_input.exists():
        input_file = potential_input
    
    if input_file is None:
        for file in report_dir.glob("*.csv"):
            if "input" in file.name.lower() or "comments" in file.name.lower():
                input_file = file
                break
    
    if input_file is None:
        print(f"Could not find input file for report {report_slug}")
        return {"comment_count": 0, "avg_comment_length": 0}
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            
            comments = []
            for row in reader:
                if row and len(row) > 0:
                    comments.append(row[0])  # Assuming comment text is in the first column
            
            comment_count = len(comments)
            
            if comment_count > 0:
                total_length = sum(len(comment) for comment in comments)
                avg_length = total_length / comment_count
            else:
                avg_length = 0
                
            return {
                "comment_count": comment_count,
                "avg_comment_length": avg_length
            }
    except Exception as e:
        print(f"Error reading input file for report {report_slug}: {e}")
        return {"comment_count": 0, "avg_comment_length": 0}

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
    
    report_dirs = [d for d in REPORT_DIR.iterdir() if d.is_dir()]
    
    for report_dir in report_dirs:
        status_file = report_dir / "hierarchical_status.json"
        if not status_file.exists():
            continue
            
        metadata = get_report_metadata(report_dir)
        if not metadata or metadata.get("status") != "completed":
            continue
            
        comment_info = analyze_comments_in_report(report_dir)
        
        durations = get_step_durations(report_dir)
        if not durations:
            continue
            
        report_data.append({
            "slug": metadata.get("slug", "Unknown"),
            "title": metadata.get("title", "Unknown"),
            "created_at": metadata.get("created_at", "Unknown"),
            "comment_count": comment_info["comment_count"],
            "avg_comment_length": comment_info["avg_comment_length"],
            **durations
        })
    
    if report_data:
        df = pd.DataFrame(report_data)
        return df
    else:
        return pd.DataFrame()



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
    
    avg_comment_count = df["comment_count"].mean()
    avg_comment_length = df["avg_comment_length"].mean()
    
    print(f"\n=== Overall Averages ===")
    print(f"Average Comment Count: {avg_comment_count:.1f}")
    print(f"Average Comment Length: {avg_comment_length:.1f} characters")
    
    step_names = [col for col in df.columns if col not in ["slug", "title", "created_at", "comment_count", "avg_comment_length"]]
    
    print("\n=== Average Step Durations ===")
    total_avg_duration = 0
    for step in step_names:
        avg_duration = df[step].mean()
        total_avg_duration += avg_duration
        print(f"  - {step}: {format_time(avg_duration)}")
    
    print(f"\nTotal Average Duration: {format_time(total_avg_duration)}")
    
    print("\n=== Individual Report Data ===")
    for _, row in df.sort_values("comment_count").iterrows():
        print(f"\nReport: {row['title']} ({row['slug']})")
        print(f"Comments: {row['comment_count']} (avg length: {row['avg_comment_length']:.1f} characters)")
        
        report_total_duration = 0
        print("Step Durations:")
        for step in step_names:
            duration = row[step]
            report_total_duration += duration
            print(f"  - {step}: {format_time(duration)}")
        
        print(f"Total Duration: {format_time(report_total_duration)}")
    
    output_file = Path(__file__).parent / "report_timing_analysis.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDetailed data saved to {output_file}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
