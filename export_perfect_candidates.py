#!/usr/bin/env python3
"""Generate a clean CSV export of all perfect EntityUpdates candidates - simplified"""

import re

def extract_perfect_candidates():
    """Extract all 100% overlay_code candidates."""
    
    filepath = r"C:\Users\Leona\AppData\Local\Temp\copilot-tool-output-1775231068038-m6jghl.txt"
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    candidates = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for Array # line
        if line.startswith('Array #'):
            array_match = re.search(r'Array #(\d+)', line)
            if array_match:
                array_num = int(array_match.group(1))
                
                # Read next 10 lines looking for key info
                file_offset = None
                overlay_offset = None
                runtime_addr = None
                is_perfect = False
                
                for j in range(i+1, min(i+15, len(lines))):
                    check_line = lines[j]
                    
                    if 'File offset:' in check_line:
                        match = re.search(r'0x([0-9A-F]+)', check_line)
                        if match:
                            file_offset = match.group(1)
                    
                    elif 'Overlay offset:' in check_line:
                        match = re.search(r'0x([0-9A-F]+)', check_line)
                        if match:
                            overlay_offset = match.group(1)
                    
                    elif 'Runtime address:' in check_line:
                        match = re.search(r'0x([0-9A-F]+)', check_line)
                        if match:
                            runtime_addr = match.group(1)
                    
                    elif 'Composition:' in check_line and '32 overlay_code' in check_line:
                        # Check if 0 NULL and 0 unknown
                        if '0 NULL, 0 unknown' in check_line:
                            is_perfect = True
                
                if is_perfect and overlay_offset and runtime_addr and file_offset:
                    candidates.append({
                        'array': array_num,
                        'overlay': overlay_offset,
                        'runtime': runtime_addr,
                        'file': file_offset
                    })
        
        i += 1
    
    return candidates

def main():
    print("Extracting perfect candidates...")
    candidates = extract_perfect_candidates()
    
    print("=" * 90)
    print(f"PERFECT ENTITYUPDATES CANDIDATES: {len(candidates)} found")
    print("=" * 90)
    print()
    print("Array#,OverlayOffset,RuntimeAddress,FileOffset")
    print("-" * 90)
    
    for cand in candidates:
        print(f"{cand['array']},0x{cand['overlay']},0x{cand['runtime']},0x{cand['file']}")
    
    print()
    print("=" * 90)
    print("Summary:")
    print(f"  Total perfect candidates: {len(candidates)}")
    print(f"  All with 32 entries of 100% overlay_code")
    print(f"  All with 0 NULL entries and 0 unknown values")
    print("=" * 90)

if __name__ == "__main__":
    main()
