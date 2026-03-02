# Changelog - Helldivers 2 Stats Analyzer

## Recent Updates (February 18, 2026)

### 1. Removed Format Specifiers
- **Removed all number formatting** from print statements and chart labels
- Eliminated decimal precision formats (`.0f`, `.1f`, `.2f`)
- Removed thousand separators (`:,`)
- Changed pie chart percentages from `%1.1f%%` to `%d%%` (integer percentages)
- All numbers now display as raw values without formatting

### 2. Fixed Qt Platform Plugin Error
- **Added matplotlib backend configuration** to prevent Qt/Wayland errors
- Added `matplotlib.use('Agg')` before importing pyplot
- Script now runs without requiring display server or Qt platform plugins

### 3. Added Comparison Functionality
Complete comparison analysis between two time periods from stats.csv

#### New Functions Added:

**`calculate_deltas(stats_old, stats_new)`**
- Calculates the differences between two time periods
- Returns a dictionary of deltas for all numeric fields

**`create_comparison_chart(stats_old, stats_new, output_dir)`**
- Creates a 4-panel comparison visualization:
  - **Enemy Kills Comparison**: Side-by-side bars for Terminid, Automaton, Illuminate
  - **Mission Stats Comparison**: Missions Played, Won, and Extractions
  - **Stratagem Usage Comparison**: Orbitals, Eagles, Defensive, Supply
  - **Growth Metrics**: Horizontal bar chart showing changes (green for increases, red for decreases)
- Output: `comparison.png` in output directory

**`print_comparison_summary(stats_old, stats_new, calc_old, calc_new)`**
- Prints detailed progress report to console
- Shows:
  - Missions progress (new missions played/won, success rate change)
  - Combat progress (kill increases by type, deaths, accuracy change)
  - Collection progress (samples, XP earned)

#### Modified Functions:

**`load_data(csv_path)`**
- **Before**: Returned only first row as dictionary
- **After**: Returns tuple of (first_row, last_row) for comparison
- Returns `(stats, None)` if only one row exists

**`main()`**
- Now handles both single and multi-row CSV files
- Automatically detects if comparison data is available
- Generates comparison analysis when 2+ rows exist
- Uses latest stats for standard visualizations

## Usage

### Single Date Analysis
If `stats.csv` has one row, the script works as before:
- Loads and analyzes the single dataset
- Creates 4 standard visualization charts
- Prints summary statistics

### Comparison Analysis
If `stats.csv` has multiple rows, the script:
1. Uses the **first row** as baseline (old stats)
2. Uses the **last row** as current stats (new stats)
3. Creates all standard charts using latest stats
4. **Adds comparison analysis**:
   - Prints detailed progress summary
   - Creates `comparison.png` showing side-by-side comparisons

## Example Output

```
PROGRESS COMPARISON: 26-Feb2025 → 18Feb2026
======================================================================

MISSIONS PROGRESS
  New Missions Played: +993 (Total: 3716)
  New Missions Won: +943 (Total: 3557)
  Success Rate Change: -0.28%

COMBAT PROGRESS
  New Kills: +172537
    Terminid: +63279
    Automaton: +69779
    Illuminate: +39479
  New Deaths: +2929
  Accuracy Change: +2.46%

COLLECTION PROGRESS
  New Samples: +16619 (Total: 63912)
  New XP: +1631554 (Total: 4770532)
```

## Files Generated

### Standard Charts (always created):
- `kill_breakdown.png` - Bar chart of enemy kills by type
- `combat_style.png` - Pie chart of combat methods
- `mission_stats.png` - 4-panel mission overview
- `stratagem_usage.png` - Bar chart of stratagem usage

### Comparison Chart (created when 2+ rows in CSV):
- `comparison.png` - 4-panel comparison between time periods

## Technical Notes

- **Backend**: Uses matplotlib 'Agg' backend (non-interactive)
- **CSV Format**: Expects multi-row CSV with Date column
- **Comparison Logic**: Always compares first row vs last row
- **Color Scheme**: Green for positive growth, red for negative
