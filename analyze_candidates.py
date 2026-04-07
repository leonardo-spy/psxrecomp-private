#!/usr/bin/env python3
"""
Analyze the output file and filter for the most promising EntityUpdates arrays.
"""

import re

def analyze_output_file(filepath):
    """Parse the output and find the best candidates."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split by array sections
    array_pattern = r'Array #(\d+)\s+File offset:\s+0x([0-9A-Fa-f]+)\s+\([\d,]+ bytes\)\s+Overlay offset:\s+0x([0-9A-Fa-f]+)\s+Runtime address:\s+0x([0-9A-Fa-f]+)\s+Entry count:\s+(\d+)\s+Composition:\s+(\d+) overlay_code,\s+(\d+) dra_code,\s+(\d+) base_exe,\s+(\d+) overlay_data,\s+(\d+) NULL,\s+(\d+) unknown'
    
    arrays = []
    for match in re.finditer(array_pattern, content):
        arr = {
            'num': int(match.group(1)),
            'file_offset': int(match.group(2), 16),
            'overlay_offset': int(match.group(3), 16),
            'runtime_addr': int(match.group(4), 16),
            'entry_count': int(match.group(5)),
            'overlay_code': int(match.group(6)),
            'dra_code': int(match.group(7)),
            'base_exe': int(match.group(8)),
            'overlay_data': int(match.group(9)),
            'null_count': int(match.group(10)),
            'unknown': int(match.group(11)),
        }
        # Calculate quality score
        code_entries = arr['overlay_code'] + arr['dra_code'] + arr['base_exe']
        arr['code_pct'] = (code_entries / arr['entry_count'] * 100) if arr['entry_count'] > 0 else 0
        arr['quality'] = code_entries - arr['unknown']  # Higher is better
        arrays.append(arr)
    
    return arrays

def main():
    filepath = r"C:\Users\Leona\AppData\Local\Temp\copilot-tool-output-1775231068038-m6jghl.txt"
    
    arrays = analyze_output_file(filepath)
    
    print(f"Total candidate arrays: {len(arrays)}\n")
    
    # Filter for high-quality candidates
    # Look for arrays that are mostly overlay_code and have few or no unknown entries
    
    print("=" * 130)
    print("BEST CANDIDATES (100% overlay_code):")
    print("=" * 130)
    
    pure_overlay = [a for a in arrays if a['overlay_code'] == a['entry_count']]
    print(f"\nFound {len(pure_overlay)} arrays with 100% overlay_code\n")
    
    for arr in pure_overlay[:30]:  # Show top 30
        print(f"Array #{arr['num']:5d} | Offset: 0x{arr['overlay_offset']:08X} | Runtime: 0x{arr['runtime_addr']:08X} | "
              f"Entries: {arr['entry_count']:2d} | File pos: 0x{arr['file_offset']:08X}")
    
    print("\n" + "=" * 130)
    print("HIGH-QUALITY CANDIDATES (90%+ code, no unknown):")
    print("=" * 130)
    
    high_quality = [a for a in arrays 
                    if a['code_pct'] >= 90 and a['unknown'] == 0 
                    and a['entry_count'] >= 8
                    and a not in pure_overlay]
    high_quality.sort(key=lambda x: (-x['code_pct'], -x['entry_count']))
    
    print(f"\nFound {len(high_quality)} arrays\n")
    
    for arr in high_quality[:30]:
        code = arr['overlay_code'] + arr['dra_code'] + arr['base_exe']
        print(f"Array #{arr['num']:5d} | Offset: 0x{arr['overlay_offset']:08X} | Runtime: 0x{arr['runtime_addr']:08X} | "
              f"Entries: {arr['entry_count']:2d} ({code} code) | Quality: {arr['quality']:3d}")
    
    print("\n" + "=" * 130)
    print("SUMMARY STATISTICS:")
    print("=" * 130)
    
    pure = len([a for a in arrays if a['overlay_code'] == a['entry_count']])
    mostly_code = len([a for a in arrays if a['code_pct'] >= 90])
    with_code = len([a for a in arrays if a['overlay_code'] > 0])
    
    print(f"Arrays with 100% overlay_code:      {pure}")
    print(f"Arrays with 90%+ code:               {mostly_code}")
    print(f"Arrays with any overlay_code:        {with_code}")
    print(f"Total arrays scanned:                {len(arrays)}")

if __name__ == "__main__":
    main()
