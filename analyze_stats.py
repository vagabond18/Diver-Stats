#!/usr/bin/env python3
"""
simple Helldivers 2 Stats Analyzer
reads CSV data and creates basic visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# style
sns.set_style("darkgrid")
sns.set_palette("husl")

def load_data(csv_path):
    """Load stats from CSV file"""
    df = pd.read_csv(csv_path)
    return df.iloc[0].to_dict()  # first row as dictionary

def calculate_basic_stats(stats):
    """Calculate basic statistics"""
    missions = stats['Missions Played']
    
    results = {
        'Total Kills': stats['Terminid Kills'] + stats['Automaton Kills'] + stats['Illuminate Kills'],
        'Mission Success Rate': (stats['Mission Won'] / missions * 100) if missions > 0 else 0,
        'Extraction Rate': (stats['Successful Extractions'] / missions * 100) if missions > 0 else 0,
        'K/D Ratio': stats['Terminid Kills'] + stats['Automaton Kills'] + stats['Illuminate Kills'] / stats['Deaths'] if stats['Deaths'] > 0 else 0,
        'Accuracy': (stats['Shots Hit'] / stats['Shots Fired'] * 100) if stats['Shots Fired'] > 0 else 0,
        'Samples Per Mission': stats['Samples Collected'] / missions if missions > 0 else 0,
        'XP Per Mission': stats['Total XP Earned'] / missions if missions > 0 else 0,
        'Objectives Per Mission': stats['Obj Completed'] / missions if missions > 0 else 0,
    }
    
    return results

def create_kill_breakdown_chart(stats, output_dir=None):
    """create enemy kills breakdown chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    kills = {
        'Terminid': stats['Terminid Kills'],
        'Automaton': stats['Automaton Kills'],
        'Illuminate': stats['Illuminate Kills'],
        'Friendly Fire': stats['Friendly Kills']
    }
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
    bars = ax.bar(kills.keys(), kills.values(), color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_title('Enemy Kills Breakdown', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Number of Kills', fontsize=12, fontweight='bold')
    ax.set_xlabel('Enemy Type', fontsize=12, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'kill_breakdown.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("[PASSED] Created kill_breakdown.png")

def create_combat_style_chart(stats, output_dir=None):
    """create combat style/method breakdown"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    combat_methods = {
        'Grenade': stats['Grenade Kills'],
        'Melee': stats['Melee Kills'],
        'Eagle Strikes': stats['Eagle Kills'],
        'Gun Fire': stats['Shots Hit'] // 10  # Approximate gun kills
    }
    
    colors = ['#2E8B57', '#FF8C00', '#DC143C', '#4169E1']
    wedges, texts, autotexts = ax.pie(
        combat_methods.values(),
        labels=combat_methods.keys(),
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        explode=[0.05, 0.05, 0.05, 0.05]
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    ax.set_title('Combat Style Breakdown', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'combat_style.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("[PASSED] Created combat_style.png")

def create_mission_stats_chart(stats, output_dir=None):
    """create mission statistics overview"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    missions = stats['Missions Played']
    
    # mission Success
    ax1 = axes[0, 0]
    success_data = [stats['Mission Won'], missions - stats['Mission Won']]
    colors1 = ['#2ECC71', '#E74C3C']
    ax1.pie(success_data, labels=['Won', 'Lost'], autopct='%1.1f%%', 
            colors=colors1, startangle=90)
    ax1.set_title('Mission Success Rate', fontweight='bold', fontsize=12)
    
    # extractions
    ax2 = axes[0, 1]
    extraction_data = [stats['Successful Extractions'], missions - stats['Successful Extractions']]
    colors2 = ['#3498DB', '#95A5A6']
    ax2.pie(extraction_data, labels=['Extracted', 'Failed'], autopct='%1.1f%%',
            colors=colors2, startangle=90)
    ax2.set_title('Extraction Rate', fontweight='bold', fontsize=12)
    
    # per mission metrics
    ax3 = axes[1, 0]
    metrics = {
        'Samples': stats['Samples Collected'] / missions,
        'XP (÷100)': stats['Total XP Earned'] / missions / 100,
        'Objectives': stats['Obj Completed'] / missions,
        'Deaths': stats['Deaths'] / missions
    }
    bars = ax3.bar(metrics.keys(), metrics.values(), color=['#F39C12', '#9B59B6', '#1ABC9C', '#E74C3C'])
    ax3.set_title('Average Per Mission', fontweight='bold', fontsize=12)
    ax3.set_ylabel('Count', fontweight='bold')
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # accuracy stats
    ax4 = axes[1, 1]
    accuracy = (stats['Shots Hit'] / stats['Shots Fired'] * 100) if stats['Shots Fired'] > 0 else 0
    ax4.barh(['Accuracy'], [accuracy], color='#16A085')
    ax4.set_xlim(0, 100)
    ax4.set_xlabel('Percentage', fontweight='bold')
    ax4.set_title('Shooting Accuracy', fontweight='bold', fontsize=12)
    ax4.text(accuracy + 2, 0, f'{accuracy:.1f}%', va='center', fontweight='bold', fontsize=14)
    
    plt.suptitle('Mission Statistics Overview', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'mission_stats.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("[PASSED] Created mission_stats.png")

def create_stratagem_usage_chart(stats, output_dir=None):
    """create stratagem usage chart"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    stratagems = {
        'Orbitals': stats['Orbitals Used'],
        'Eagles': stats['Eagles Used'],
        'Defensive': stats['Defensive Stratagems Used'],
        'Supply': stats['Supply Stratagems Used'],
        'Reinforcements': stats['Reinforce Used']
    }
    
    colors = ['#8A2BE2', '#FF1493', '#00CED1', '#FFD700', '#FF6347']
    bars = ax.bar(stratagems.keys(), stratagems.values(), color=colors, edgecolor='black', linewidth=1.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_title('Stratagem Usage', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Times Used', fontsize=12, fontweight='bold')
    ax.set_xlabel('Stratagem Type', fontsize=12, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    if output_dir:
        plt.savefig(output_dir / 'stratagem_usage.png', dpi=150, bbox_inches='tight')
        plt.close()
        plt.close()
    print("[PASSED] Created stratagem_usage.png")

def print_summary(stats, calculated_stats):
    """print summary statistics to console"""
    print("\n" + "="*60)
    print("HELLDIVERS 2 STATISTICS SUMMARY")
    print("="*60)
    
    print(f"\nMISSION STATISTICS")
    print(f"  • Total Missions: {stats['Missions Played']:,}")
    print(f"  • Missions Won: {stats['Mission Won']:,}")
    print(f"  • Success Rate: {calculated_stats['Mission Success Rate']:.1f}%")
    print(f"  • Extraction Rate: {calculated_stats['Extraction Rate']:.1f}%")
    
    print(f"\nCOMBAT STATISTICS")
    print(f"  • Total Kills: {calculated_stats['Total Kills']:,}")
    print(f"  • Terminid: {stats['Terminid Kills']:,}")
    print(f"  • Automaton: {stats['Automaton Kills']:,}")
    print(f"  • Illuminate: {stats['Illuminate Kills']:,}")
    print(f"  • K/D Ratio: {calculated_stats['K/D Ratio']:.2f}")
    print(f"  • Accuracy: {calculated_stats['Accuracy']:.1f}%")
    
    print(f"\nAVERAGES PER MISSION")
    print(f"  • XP Earned: {calculated_stats['XP Per Mission']:,.0f}")
    print(f"  • Samples: {calculated_stats['Samples Per Mission']:.1f}")
    print(f"  • Objectives: {calculated_stats['Objectives Per Mission']:.1f}")
    
    print("\n" + "="*60 + "\n")

def main():
    """main execution function"""
    print("Helldivers 2 Stats Analyzer")
    print("-" * 40)
    
    # find CSV file
    csv_file = Path('assets/26Feb2025.csv')
    if not csv_file.exists():
        print(f"[ERROR] CSV file not found at {csv_file}")
        return
    
    # create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # load and analyze data
    print(f"Loading data from {csv_file}")
    stats = load_data(csv_file)
    
    print("Calculating statistics...")
    calculated_stats = calculate_basic_stats(stats)
    
    # print summary
    print_summary(stats, calculated_stats)
    
    # Create visualizations
    print("Creating visualizations...")
    create_kill_breakdown_chart(stats, output_dir)
    create_combat_style_chart(stats, output_dir)
    create_mission_stats_chart(stats, output_dir)
    create_stratagem_usage_chart(stats, output_dir)
    
    print(f"\n[PASSED] Done! Charts saved to '{output_dir}/' directory")

if __name__ == "__main__":
    main()
