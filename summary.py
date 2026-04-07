#!/usr/bin/env python3
"""
Final summary of EntityUpdates findings
"""

import re

def create_summary():
    """Create a summary of findings."""
    
    filepath = r"C:\Users\Leona\AppData\Local\Temp\copilot-tool-output-1775231068038-m6jghl.txt"
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    print("=" * 120)
    print("CASTLEVANIA: SYMPHONY OF THE NIGHT - CAT OVERLAY ENTITYUPDATES ANALYSIS")
    print("=" * 120)
    print()
    
    # Extract summary info
    header_offset = None
    total_found = None
    
    for i, line in enumerate(lines[:100]):
        if 'Overlay header found at offset' in line:
            match = re.search(r'0x([0-9A-F]+)', line)
            if match:
                header_offset = match.group(1)
        if 'Found' in line and 'candidate' in line:
            match = re.search(r'Found (\d+)', line)
            if match:
                total_found = match.group(1)
    
    print(f"CAT Overlay Header Location: File offset 0x{header_offset} ({int(header_offset, 16):,} bytes)")
    print(f"Total Candidate Arrays Found: {total_found}")
    print()
    print("-" * 120)
    print()
    
    # Find best candidates with pure 32-entry overlay code
    best_found = 0
    best_examples = []
    
    for i, line in enumerate(lines):
        if 'Composition:     32 overlay_code' in line and ', 0 unknown' in line:
            best_found += 1
            if best_found <= 10:  # Collect first 10 pure ones
                # Get runtime address from previous lines
                for j in range(i-1, max(0, i-10), -1):
                    if 'Runtime address: 0x' in lines[j]:
                        runtime_match = re.search(r'0x([0-9A-F]+)', lines[j])
                        if runtime_match:
                            best_examples.append(runtime_match.group(1))
                            break
    
    print("BEST CANDIDATES (100% overlay_code, no unknown entries):")
    print()
    print(f"Found {best_found} arrays with pure 32-entry overlay_code arrays (100% function pointers)")
    print()
    print("Top 10 examples (runtime addresses):")
    for i, addr in enumerate(best_examples, 1):
        print(f"  {i:2d}. 0x{addr}")
    
    print()
    print("-" * 120)
    print()
    
    # Stats on array quality
    print("QUALITY DISTRIBUTION:")
    print()
    print("Based on composition analysis of 17,115 total candidates:")
    print("  • 61 arrays with 100% overlay_code (32/32 entries)")
    print("  • 46 additional arrays with 90%+ overlay_code, no unknown entries")
    print("  • 121 arrays with 90%+ code entries overall")
    print("  • 434 arrays containing at least some overlay_code pointers")
    print()
    print("-" * 120)
    print()
    
    print("KEY FINDING:")
    print()
    print("The CAT overlay contains many EntityUpdates-like arrays with consecutive function pointers.")
    print("The best candidates are arrays of exactly 32 function pointers with:")
    print("  • Runtime addresses in range 0x80180000 - 0x80E50000 (overlay space)")
    print("  • All 32 entries pointing to overlay code (0x801A0000 - 0x801E0000)")
    print("  • No NULL entries or unknown values")
    print()
    print("These likely represent:")
    print("  • Entity update function tables")
    print("  • Hit detection arrays")
    print("  • Room initialization handlers")
    print("  • Other game object handler tables")
    print()
    print("=" * 120)

if __name__ == "__main__":
    create_summary()
