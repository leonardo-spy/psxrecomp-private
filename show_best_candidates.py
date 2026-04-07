#!/usr/bin/env python3
"""
Extract and display the top EntityUpdates candidates with full details.
"""

import re

def extract_candidates_with_entries(filepath):
    """Extract candidates and their entries from the output file."""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Split into array sections
    sections = content.split('\n====================================================================================================\n')
    
    candidates = []
    
    for section in sections[1:]:  # Skip header
        lines = section.strip().split('\n')
        if not lines or 'Array #' not in lines[0]:
            continue
        
        # Parse header
        header = lines[0]
        array_match = re.search(r'Array #(\d+)', header)
        if not array_match:
            continue
        
        array_num = int(array_match.group(1))
        
        # Parse composition line
        comp_line = None
        entry_lines = []
        for i, line in enumerate(lines):
            if 'Composition:' in line:
                comp_line = line
            if line.strip().startswith('[') and ']' in line:
                entry_lines.append(line)
        
        if not comp_line:
            continue
        
        # Parse composition
        comp_match = re.search(r'(\d+) overlay_code.*?(\d+) NULL.*?(\d+) unknown', comp_line)
        if comp_match:
            overlay_code = int(comp_match.group(1))
            nulls = int(comp_match.group(2))
            unknown = int(comp_match.group(3))
            
            # Extract entries
            entries = []
            for line in entry_lines:
                entry_match = re.search(r'\[(\d+)\]\s+\[([A-Z]+)\]\s+0x([0-9A-F]+)', line, re.IGNORECASE)
                if entry_match:
                    entries.append({
                        'idx': int(entry_match.group(1)),
                        'type': entry_match.group(2),
                        'addr': entry_match.group(3)
                    })
            
            # Extract offset info
            offset_match = re.search(r'Runtime address:\s+0x([0-9A-F]+)', section, re.IGNORECASE)
            if offset_match:
                runtime = offset_match.group(1)
                
                candidates.append({
                    'num': array_num,
                    'overlay_code': overlay_code,
                    'nulls': nulls,
                    'unknown': unknown,
                    'runtime': runtime,
                    'entries': entries
                })
    
    return candidates

def main():
    filepath = r"C:\Users\Leona\AppData\Local\Temp\copilot-tool-output-1775231068038-m6jghl.txt"
    
    candidates = extract_candidates_with_entries(filepath)
    
    print(f"Extracted {len(candidates)} candidates\n")
    
    # Filter for best candidates
    best = [c for c in candidates if c['overlay_code'] == 32 and c['unknown'] == 0]
    best.sort(key=lambda x: x['num'])
    
    print("=" * 150)
    print(f"TOP CANDIDATES: {len(best)} arrays with 32/32 overlay_code entries and 0 unknown")
    print("=" * 150)
    print()
    
    for cand in best[:15]:  # Show top 15
        print(f"Array #{cand['num']:5d} | Runtime: 0x{cand['runtime']}")
        print(f"  Entries ({len(cand['entries'])}): ", end="")
        
        # Show first 8 entries
        addr_list = [e['addr'] for e in cand['entries'][:8]]
        print(", ".join([f"0x{addr}" for addr in addr_list]))
        
        if len(cand['entries']) > 8:
            print(f"           ... and {len(cand['entries']) - 8} more")
        
        print()

if __name__ == "__main__":
    main()
