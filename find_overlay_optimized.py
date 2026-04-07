#!/usr/bin/env python3
"""
Search PS1 CD image for CAT overlay and find EntityUpdates arrays.
Optimized version - reads specific sectors only.
"""

import struct
import os

# Known overlay header pattern (4 consecutive 32-bit LE values)
HEADER_PATTERN = struct.pack('<4I', 0x801BB6D4, 0x801BBAD8, 0x801BDC68, 0x801BDAF0)

# Memory region classification
def classify_pointer(value):
    """Classify a 32-bit pointer value by memory region."""
    if value == 0:
        return "NULL"
    elif 0x801A0000 <= value < 0x801E0000:
        return "overlay_code"
    elif 0x800A0000 <= value < 0x80180000:
        return "dra_code"
    elif 0x80010000 <= value < 0x800A0000:
        return "base_exe"
    elif 0x80180000 <= value < 0x801A0000:
        return "overlay_data"
    else:
        return "unknown"

def find_arrays_near_header(data, overlay_start):
    """Find EntityUpdates arrays near the header."""
    
    print(f"Overlay header found at offset 0x{overlay_start:08X}")
    print(f"Searching for EntityUpdates arrays in overlay data...\n")
    
    candidates = []
    
    # Start search from right after the header, but limit to reasonable overlay size
    # CAT overlay is probably not more than a few MB
    search_start = overlay_start + 16
    search_end = min(overlay_start + 0x1000000, len(data))  # Search up to 16MB from header
    
    offset = search_start
    while offset < search_end - 32:
        # Read potential array
        array_data = []
        code_count = 0
        null_count = 0
        unknown_count = 0
        
        for i in range(32):  # Check up to 32 entries per potential array
            if offset + i*4 + 4 > len(data):
                break
            
            try:
                value = struct.unpack('<I', data[offset + i*4:offset + i*4 + 4])[0]
            except:
                break
            
            classification = classify_pointer(value)
            array_data.append((value, classification))
            
            if classification in ["overlay_code", "dra_code", "base_exe"]:
                code_count += 1
            elif classification == "NULL":
                null_count += 1
            else:
                unknown_count += 1
        
        # Check if this looks like an EntityUpdates array
        if len(array_data) >= 8:
            # Calculate what percentage are code/null
            code_or_null = code_count + null_count
            if code_or_null >= len(array_data) * 0.75:  # At least 75% are code or NULL
                # Check that unknown entries are reasonable (< 25%)
                if unknown_count <= len(array_data) * 0.25:
                    candidates.append((offset, array_data))
                    offset += len(array_data) * 4  # Skip past this array
                    continue
        
        offset += 4
    
    return candidates

def find_overlay_header(bin_path):
    """Find the CAT overlay header in the BIN file."""
    
    print(f"Opening BIN file: {bin_path}")
    
    if not os.path.exists(bin_path):
        print(f"ERROR: File not found: {bin_path}")
        return None, None
    
    file_size = os.path.getsize(bin_path)
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    # Read the file in chunks to avoid loading everything at once
    # But we need to search the whole thing for the pattern
    print(f"\nSearching for overlay header pattern...")
    print(f"Looking for: 0x801BB6D4 0x801BBAD8 0x801BDC68 0x801BDAF0")
    
    with open(bin_path, 'rb') as f:
        data = f.read()
    
    # Search for the pattern
    header_pos = data.find(HEADER_PATTERN)
    
    if header_pos != -1:
        return data, header_pos
    
    print("Direct pattern match not found. Searching for sequence near these values...")
    
    # More flexible search - look for the first value and check surrounding context
    search_val = struct.pack('<I', 0x801BB6D4)
    pos = 0
    while True:
        pos = data.find(search_val, pos)
        if pos == -1:
            break
        
        # Check context around this position
        if pos + 16 <= len(data):
            vals = struct.unpack('<4I', data[pos:pos+16])
            if (vals[0] == 0x801BB6D4 and 
                vals[1] in (0x801BBAD8, 0x801BBA00, 0x801BBC00) and  # Allow some variation
                vals[2] in (0x801BDC68, 0x801BDC00) and
                vals[3] in (0x801BDAF0, 0x801BDA00)):
                print(f"Found matching pattern at offset 0x{pos:08X}")
                print(f"  Values: 0x{vals[0]:08X} 0x{vals[1]:08X} 0x{vals[2]:08X} 0x{vals[3]:08X}")
                return data, pos
        
        pos += 1
    
    return None, None

def main():
    # Try Track 1 BIN file first (usually contains the main overlay data)
    bin_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"
    
    data, overlay_start = find_overlay_header(bin_path)
    
    if data is None:
        print("\nPattern not found in Track 1. Trying Track 2...")
        bin_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 2).bin"
        data, overlay_start = find_overlay_header(bin_path)
    
    if data is None:
        print("ERROR: Could not find overlay header pattern in either track.")
        return
    
    print(f"\n" + "=" * 100)
    candidates = find_arrays_near_header(data, overlay_start)
    
    if not candidates:
        print("No EntityUpdates arrays found.")
        return
    
    print(f"\nFound {len(candidates)} candidate EntityUpdates arrays:\n")
    
    for idx, (array_offset, array_data) in enumerate(candidates, 1):
        overlay_relative = array_offset - overlay_start
        runtime_addr = 0x80180000 + overlay_relative
        
        print(f"\n{'=' * 100}")
        print(f"Array #{idx}")
        print(f"  File offset:     0x{array_offset:08X} ({array_offset:,} bytes)")
        print(f"  Overlay offset:  0x{overlay_relative:08X}")
        print(f"  Runtime address: 0x{runtime_addr:08X}")
        print(f"  Entry count:     {len(array_data)}")
        
        # Count types
        code_count = sum(1 for _, c in array_data if c == "overlay_code")
        dra_count = sum(1 for _, c in array_data if c == "dra_code")
        exe_count = sum(1 for _, c in array_data if c == "base_exe")
        data_count = sum(1 for _, c in array_data if c == "overlay_data")
        null_count = sum(1 for _, c in array_data if c == "NULL")
        unk_count = sum(1 for _, c in array_data if c == "unknown")
        
        print(f"  Composition:     {code_count} overlay_code, {dra_count} dra_code, {exe_count} base_exe,")
        print(f"                   {data_count} overlay_data, {null_count} NULL, {unk_count} unknown")
        print(f"\n  Entries:")
        
        for i, (value, classification) in enumerate(array_data):
            symbol = {
                "overlay_code": "[OVL]",
                "dra_code": "[DRA]",
                "base_exe": "[EXE]",
                "overlay_data": "[DAT]",
                "NULL": "[NULL]",
                "unknown": "[UNK]"
            }.get(classification, "?????")
            
            print(f"    [{i:2d}] {symbol} 0x{value:08X}")
    
    print(f"\n" + "=" * 100)

if __name__ == "__main__":
    main()
