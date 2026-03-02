#!/usr/bin/env python3
"""
simple Helldivers 2 Stats Analyzer
reads CSV data and creates basic visualizations
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # use non-interactive backend to avoid Qt errors
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


sns.set_style("darkgrid")
sns.set_palette("husl")

def load_data(csv_path):
    """Load stats from CSV file"""
    df = pd.read_csv(csv_path)
    if len(df) == 1:
        return df.iloc[0].to_dict(), None
    else:
        # return both rows for comparison
        return df.iloc[0].to_dict(), df.iloc[-1].to_dict()

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

def parse_time_to_hours(time_str):
    """Parse time string (HH:MM:SS) to total hours"""
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    return hours + minutes / 60 + seconds / 3600

def format_hours_to_readable(hours):
    """Format hours to readable string (e.g., '359 hours 27 minutes')"""
    whole_hours = int(hours)
    minutes = int((hours - whole_hours) * 60)
    return f"{whole_hours} hours {minutes} minutes"

def calculate_deltas(stats_old, stats_new):
    """Calculate the differences between two time periods"""
    deltas = {}
    for key in stats_old.keys():
        if key != 'Date' and isinstance(stats_old[key], (int, float)):
            deltas[key] = stats_new[key] - stats_old[key]
    return deltas

def create_comparison_chart(stats_old, stats_new, output_dir=None):
    """Create comparison chart showing progress between two dates"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # enemy kills comparison
    ax1 = axes[0, 0]
    enemies = ['Terminid', 'Automaton', 'Illuminate']
    old_kills = [stats_old['Terminid Kills'], stats_old['Automaton Kills'], stats_old['Illuminate Kills']]
    new_kills = [stats_new['Terminid Kills'], stats_new['Automaton Kills'], stats_new['Illuminate Kills']]
    
    x = np.arange(len(enemies))
    width = 0.35
    bars1 = ax1.bar(x - width/2, old_kills, width, label=stats_old['Date'], color='#95A5A6')
    bars2 = ax1.bar(x + width/2, new_kills, width, label=stats_new['Date'], color='#3498DB')
    
    ax1.set_title('Enemy Kills Comparison', fontweight='bold')
    ax1.set_ylabel('Kills')
    ax1.set_xticks(x)
    ax1.set_xticklabels(enemies)
    ax1.legend()
    
    # mission stats comparison
    ax2 = axes[0, 1]
    categories = ['Missions\nPlayed', 'Missions\nWon', 'Extractions']
    old_vals = [stats_old['Missions Played'], stats_old['Mission Won'], stats_old['Successful Extractions']]
    new_vals = [stats_new['Missions Played'], stats_new['Mission Won'], stats_new['Successful Extractions']]
    
    x2 = np.arange(len(categories))
    bars1 = ax2.bar(x2 - width/2, old_vals, width, label=stats_old['Date'], color='#95A5A6')
    bars2 = ax2.bar(x2 + width/2, new_vals, width, label=stats_new['Date'], color='#2ECC71')
    
    ax2.set_title('Mission Stats Comparison', fontweight='bold')
    ax2.set_ylabel('Count')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(categories)
    ax2.legend()
    
    # stratagem usage comparison
    ax3 = axes[1, 0]
    strats = ['Orbitals', 'Eagles', 'Defensive', 'Supply']
    old_strat = [stats_old['Orbitals Used'], stats_old['Eagles Used'], 
                 stats_old['Defensive Stratagems Used'], stats_old['Supply Stratagems Used']]
    new_strat = [stats_new['Orbitals Used'], stats_new['Eagles Used'],
                 stats_new['Defensive Stratagems Used'], stats_new['Supply Stratagems Used']]
    
    x3 = np.arange(len(strats))
    bars1 = ax3.bar(x3 - width/2, old_strat, width, label=stats_old['Date'], color='#95A5A6')
    bars2 = ax3.bar(x3 + width/2, new_strat, width, label=stats_new['Date'], color='#9B59B6')
    
    ax3.set_title('Stratagem Usage Comparison', fontweight='bold')
    ax3.set_ylabel('Uses')
    ax3.set_xticks(x3)
    ax3.set_xticklabels(strats, rotation=15, ha='right')
    ax3.legend()
    
    # growth metrics
    ax4 = axes[1, 1]
    deltas = calculate_deltas(stats_old, stats_new)
    metrics = {
        'Total Kills': deltas['Terminid Kills'] + deltas['Automaton Kills'] + deltas['Illuminate Kills'],
        'Missions': deltas['Missions Played'],
        'Deaths': deltas['Deaths'],
        'Samples': deltas['Samples Collected']
    }
    
    colors_growth = ['#2ECC71' if v > 0 else '#E74C3C' for v in metrics.values()]
    bars = ax4.barh(list(metrics.keys()), list(metrics.values()), color=colors_growth)
    ax4.set_title('Growth (New - Old)', fontweight='bold')
    ax4.set_xlabel('Change')
    ax4.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    
    plt.suptitle(f'Stats Comparison: {stats_old["Date"]} vs {stats_new["Date"]}', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(output_dir / 'comparison.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("[PASSED] Created comparison.png")

def create_progress_chart(stats_old, stats_new, calc_old, calc_new, output_dir=None):
    """Create detailed progress visualization showing improvements"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    deltas = calculate_deltas(stats_old, stats_new)
    
    # 1. Percentage Growth - Main metrics
    ax1 = fig.add_subplot(gs[0, 0])
    metrics_pct = {
        'Missions': (deltas['Missions Played'] / stats_old['Missions Played'] * 100),
        'Kills': ((deltas['Terminid Kills'] + deltas['Automaton Kills'] + deltas['Illuminate Kills']) / 
                  (stats_old['Terminid Kills'] + stats_old['Automaton Kills'] + stats_old['Illuminate Kills']) * 100),
        'Samples': (deltas['Samples Collected'] / stats_old['Samples Collected'] * 100),
        'XP': (deltas['Total XP Earned'] / stats_old['Total XP Earned'] * 100)
    }
    colors_pct = ['#3498DB', '#E74C3C', '#F39C12', '#9B59B6']
    bars = ax1.bar(metrics_pct.keys(), metrics_pct.values(), color=colors_pct, edgecolor='black', linewidth=1.5)
    ax1.set_title('Growth Rate (%)', fontweight='bold', fontsize=14)
    ax1.set_ylabel('Percentage Increase (%)', fontweight='bold')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:+.1f}%', ha='center', va='bottom' if height > 0 else 'top', 
                fontweight='bold', fontsize=10)
    
    # 2. Success Rates Comparison
    ax2 = fig.add_subplot(gs[0, 1])
    rates = ['Success\nRate', 'Extraction\nRate', 'Accuracy']
    old_rates = [calc_old['Mission Success Rate'], calc_old['Extraction Rate'], calc_old['Accuracy']]
    new_rates = [calc_new['Mission Success Rate'], calc_new['Extraction Rate'], calc_new['Accuracy']]
    
    x = np.arange(len(rates))
    width = 0.35
    bars1 = ax2.bar(x - width/2, old_rates, width, label=stats_old['Date'], color='#95A5A6')
    bars2 = ax2.bar(x + width/2, new_rates, width, label=stats_new['Date'], color='#2ECC71')
    
    ax2.set_title('Performance Rates (%)', fontweight='bold', fontsize=14)
    ax2.set_ylabel('Percentage', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(rates)
    ax2.set_ylim(0, 100)
    ax2.legend()
    
    # Add delta labels
    for i, (old_val, new_val) in enumerate(zip(old_rates, new_rates)):
        delta = new_val - old_val
        y_pos = max(old_val, new_val) + 2
        ax2.text(i, y_pos, f'{delta:+.1f}%', ha='center', fontweight='bold', 
                fontsize=9, color='green' if delta > 0 else 'red')
    
    # 3. Mission Time Comparison
    ax3 = fig.add_subplot(gs[1, 0])
    time_old_hours = parse_time_to_hours(stats_old['In Mission Time'])
    time_new_hours = parse_time_to_hours(stats_new['In Mission Time'])
    time_delta_hours = time_new_hours - time_old_hours
    
    bars = ax3.bar(['2025', '2026'], [time_old_hours, time_new_hours], 
                   color=['#95A5A6', '#3498DB'], edgecolor='black', linewidth=1.5)
    ax3.set_title('Total Mission Time', fontweight='bold', fontsize=14)
    ax3.set_ylabel('Hours', fontweight='bold')
    
    for bar, hours in zip(bars, [time_old_hours, time_new_hours]):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(hours)}h', ha='center', va='bottom', fontweight='bold')
    
    # Add delta annotation
    ax3.text(0.5, max(time_old_hours, time_new_hours) * 0.5, 
            f'+{int(time_delta_hours)}h\n({time_delta_hours/time_old_hours*100:+.1f}%)',
            ha='center', fontweight='bold', fontsize=12, 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 4. Kill Efficiency (Kills per Hour)
    ax4 = fig.add_subplot(gs[1, 1])
    total_kills_old = stats_old['Terminid Kills'] + stats_old['Automaton Kills'] + stats_old['Illuminate Kills']
    total_kills_new = stats_new['Terminid Kills'] + stats_new['Automaton Kills'] + stats_new['Illuminate Kills']
    kills_per_hour_old = total_kills_old / time_old_hours if time_old_hours > 0 else 0
    kills_per_hour_new = total_kills_new / time_new_hours if time_new_hours > 0 else 0
    
    bars = ax4.bar(['2025', '2026'], [kills_per_hour_old, kills_per_hour_new],
                   color=['#95A5A6', '#E74C3C'], edgecolor='black', linewidth=1.5)
    ax4.set_title('Kills per Hour', fontweight='bold', fontsize=14)
    ax4.set_ylabel('Kills/Hour', fontweight='bold')
    
    for bar, kph in zip(bars, [kills_per_hour_old, kills_per_hour_new]):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{kph:.1f}', ha='center', va='bottom', fontweight='bold')
    
    efficiency_change = ((kills_per_hour_new - kills_per_hour_old) / kills_per_hour_old * 100) if kills_per_hour_old > 0 else 0
    ax4.text(0.5, max(kills_per_hour_old, kills_per_hour_new) * 0.5,
            f'{efficiency_change:+.1f}%',
            ha='center', fontweight='bold', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 5. Enemy Distribution (Kill percentages)
    ax5 = fig.add_subplot(gs[2, 0])
    enemy_types = ['Terminid', 'Automaton', 'Illuminate']
    old_distro = [stats_old['Terminid Kills']/total_kills_old*100,
                  stats_old['Automaton Kills']/total_kills_old*100,
                  stats_old['Illuminate Kills']/total_kills_old*100]
    new_distro = [stats_new['Terminid Kills']/total_kills_new*100,
                  stats_new['Automaton Kills']/total_kills_new*100,
                  stats_new['Illuminate Kills']/total_kills_new*100]
    
    x = np.arange(len(enemy_types))
    width = 0.35
    bars1 = ax5.bar(x - width/2, old_distro, width, label=stats_old['Date'], color='#95A5A6')
    bars2 = ax5.bar(x + width/2, new_distro, width, label=stats_new['Date'], color='#FF6B6B')
    
    ax5.set_title('Enemy Kill Distribution', fontweight='bold', fontsize=14)
    ax5.set_ylabel('Percentage of Total Kills (%)', fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(enemy_types)
    ax5.legend()
    
    # 6. Resources per Mission
    ax6 = fig.add_subplot(gs[2, 1])
    resources = ['Samples/\nMission', 'XP/Mission\n(÷100)', 'Objectives/\nMission']
    old_resources = [
        stats_old['Samples Collected'] / stats_old['Missions Played'],
        stats_old['Total XP Earned'] / stats_old['Missions Played'] / 100,
        stats_old['Obj Completed'] / stats_old['Missions Played']
    ]
    new_resources = [
        stats_new['Samples Collected'] / stats_new['Missions Played'],
        stats_new['Total XP Earned'] / stats_new['Missions Played'] / 100,
        stats_new['Obj Completed'] / stats_new['Missions Played']
    ]
    
    x = np.arange(len(resources))
    width = 0.35
    bars1 = ax6.bar(x - width/2, old_resources, width, label=stats_old['Date'], color='#95A5A6')
    bars2 = ax6.bar(x + width/2, new_resources, width, label=stats_new['Date'], color='#F39C12')
    
    ax6.set_title('Average Resources per Mission', fontweight='bold', fontsize=14)
    ax6.set_ylabel('Count', fontweight='bold')
    ax6.set_xticks(x)
    ax6.set_xticklabels(resources)
    ax6.legend()
    
    # Add percentage change labels
    for i, (old_val, new_val) in enumerate(zip(old_resources, new_resources)):
        if old_val > 0:
            pct_change = ((new_val - old_val) / old_val * 100)
            y_pos = max(old_val, new_val) + 0.5
            ax6.text(i, y_pos, f'{pct_change:+.1f}%', ha='center', 
                    fontweight='bold', fontsize=9, color='green' if pct_change > 0 else 'red')
    
    plt.suptitle(f'Progress Analysis: {stats_old["Date"]} → {stats_new["Date"]}', 
                 fontsize=18, fontweight='bold', y=0.995)
    
    if output_dir:
        plt.savefig(output_dir / 'progress_analysis.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("[PASSED] Created progress_analysis.png")

def print_comparison_summary(stats_old, stats_new, calc_old, calc_new):
    """Print comparison summary between two time periods"""
    deltas = calculate_deltas(stats_old, stats_new)
    
    print("\n" + "="*70)
    print(f"PROGRESS COMPARISON: {stats_old['Date']} → {stats_new['Date']}")
    print("="*70)
    
    print("\nMISSIONS PROGRESS")
    missions_delta = deltas['Missions Played']
    missions_won_delta = deltas['Mission Won']
    missions_pct = (missions_delta / stats_old['Missions Played'] * 100) if stats_old['Missions Played'] > 0 else 0
    print(f"  New Missions Played: +{missions_delta} ({missions_pct:+.1f}%) - Total: {stats_new['Missions Played']}")
    print(f"  New Missions Won: +{missions_won_delta} - Total: {stats_new['Mission Won']}")
    success_rate_change = calc_new['Mission Success Rate'] - calc_old['Mission Success Rate']
    print(f"  Success Rate: {calc_old['Mission Success Rate']:.1f}% → {calc_new['Mission Success Rate']:.1f}% ({success_rate_change:+.1f}%)")
    extraction_rate_change = calc_new['Extraction Rate'] - calc_old['Extraction Rate']
    print(f"  Extraction Rate: {calc_old['Extraction Rate']:.1f}% → {calc_new['Extraction Rate']:.1f}% ({extraction_rate_change:+.1f}%)")
    
    # mission time comparison
    time_old_hours = parse_time_to_hours(stats_old['In Mission Time'])
    time_new_hours = parse_time_to_hours(stats_new['In Mission Time'])
    time_delta_hours = time_new_hours - time_old_hours
    time_pct = (time_delta_hours / time_old_hours * 100) if time_old_hours > 0 else 0
    print(f"  Mission Time: {format_hours_to_readable(time_old_hours)} → {format_hours_to_readable(time_new_hours)}")
    print(f"  New Time Played: +{format_hours_to_readable(time_delta_hours)} ({time_pct:+.1f}%)")
    
    print("\nCOMBAT PROGRESS")
    total_kills_delta = deltas['Terminid Kills'] + deltas['Automaton Kills'] + deltas['Illuminate Kills']
    total_kills_old = stats_old['Terminid Kills'] + stats_old['Automaton Kills'] + stats_old['Illuminate Kills']
    kills_pct = (total_kills_delta / total_kills_old * 100) if total_kills_old > 0 else 0
    print(f"  New Kills: +{total_kills_delta} ({kills_pct:+.1f}%)")
    print(f"  Terminid: +{deltas['Terminid Kills']}")
    print(f"  Automaton: +{deltas['Automaton Kills']}")
    print(f"  Illuminate: +{deltas['Illuminate Kills']}")
    deaths_pct = (deltas['Deaths'] / stats_old['Deaths'] * 100) if stats_old['Deaths'] > 0 else 0
    print(f"  New Deaths: +{deltas['Deaths']} ({deaths_pct:+.1f}%)")
    accuracy_change = calc_new['Accuracy'] - calc_old['Accuracy']
    print(f"  Accuracy: {calc_old['Accuracy']:.1f}% → {calc_new['Accuracy']:.1f}% ({accuracy_change:+.1f}%)")
    
    print("\nCOLLECTION PROGRESS")
    samples_pct = (deltas['Samples Collected'] / stats_old['Samples Collected'] * 100) if stats_old['Samples Collected'] > 0 else 0
    print(f"  New Samples: +{deltas['Samples Collected']} ({samples_pct:+.1f}%) - Total: {stats_new['Samples Collected']}")
    xp_pct = (deltas['Total XP Earned'] / stats_old['Total XP Earned'] * 100) if stats_old['Total XP Earned'] > 0 else 0
    print(f"  New XP: +{deltas['Total XP Earned']} ({xp_pct:+.1f}%) - Total: {stats_new['Total XP Earned']}")
    
    print("\n" + "="*70 + "\n")

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
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_title('Enemy Kills Breakdown', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Number of Kills', fontsize=12, fontweight='bold')
    ax.set_xlabel('Enemy Type', fontsize=12, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
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
        'Gun Fire': stats['Shots Hit'] // 10  # approx gun kills
    }
    
    colors = ['#2E8B57', '#FF8C00', '#DC143C', '#4169E1']
    wedges, texts, autotexts = ax.pie(
        combat_methods.values(),
        labels=combat_methods.keys(),
        autopct='%d%%',
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
    ax1.pie(success_data, labels=['Won', 'Lost'], autopct='%d%%', 
            colors=colors1, startangle=90)
    ax1.set_title('Mission Success Rate', fontweight='bold', fontsize=12)
    
    # extractions
    ax2 = axes[0, 1]
    extraction_data = [stats['Successful Extractions'], missions - stats['Successful Extractions']]
    colors2 = ['#3498DB', '#95A5A6']
    ax2.pie(extraction_data, labels=['Extracted', 'Failed'], autopct='%d%%',
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
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_title('Stratagem Usage', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Times Used', fontsize=12, fontweight='bold')
    ax.set_xlabel('Stratagem Type', fontsize=12, fontweight='bold')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
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
    print(f"  Total Missions: {stats['Missions Played']}")
    print(f"  Missions Won: {stats['Mission Won']}")
    print(f"  Success Rate: {calculated_stats['Mission Success Rate']:.1f}%")
    print(f"  Extraction Rate: {calculated_stats['Extraction Rate']:.1f}%")
    
    print(f"\nCOMBAT STATISTICS")
    print(f"  Total Kills: {calculated_stats['Total Kills']}")
    print(f"  Terminid: {stats['Terminid Kills']}")
    print(f"  Automaton: {stats['Automaton Kills']}")
    print(f"  Illuminate: {stats['Illuminate Kills']}")
    print(f"  K/D Ratio: {calculated_stats['K/D Ratio']:.1f}")
    print(f"  Accuracy: {calculated_stats['Accuracy']:.1f}%")
    
    print(f"\nAVERAGES PER MISSION")
    print(f"  XP Earned: {calculated_stats['XP Per Mission']:.1f}")
    print(f"  Samples: {calculated_stats['Samples Per Mission']:.1f}")
    print(f"  Objectives: {calculated_stats['Objectives Per Mission']:.1f}")
    
    print("\n" + "="*60 + "\n")

def main():
    """main execution function"""
    print("Helldivers 2 Stats Analyzer")
    print("-" * 40)
    
    # find CSV file
    csv_file = Path('./stats.csv')
    if not csv_file.exists():
        print(f"[ERROR] CSV file not found at {csv_file}")
        return
    
    # create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # load and analyze data
    print(f"Loading data from {csv_file}")
    stats_old, stats_new = load_data(csv_file)
    
    # use latest stats for main charts (or old stats if only one row)
    stats = stats_new if stats_new else stats_old
    
    print("Calculating statistics...")
    calculated_stats = calculate_basic_stats(stats)
    

    print_summary(stats, calculated_stats)

    print("Creating visualizations...")
    create_kill_breakdown_chart(stats, output_dir)
    create_combat_style_chart(stats, output_dir)
    create_mission_stats_chart(stats, output_dir)
    create_stratagem_usage_chart(stats, output_dir)
    
    # if we have two datasets, create comparison
    if stats_new:
        print("\nCreating comparison analysis...")
        calculated_stats_old = calculate_basic_stats(stats_old)
        calculated_stats_new = calculate_basic_stats(stats_new)
        
        print_comparison_summary(stats_old, stats_new, calculated_stats_old, calculated_stats_new)
        create_comparison_chart(stats_old, stats_new, output_dir)
        create_progress_chart(stats_old, stats_new, calculated_stats_old, calculated_stats_new, output_dir)
    
    print(f"\n[PASSED] Done! Charts saved to '{output_dir}/' directory")

if __name__ == "__main__":
    main()