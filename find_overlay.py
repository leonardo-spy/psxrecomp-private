#!/usr/bin/env python3
"""
Search PS1 CD image for CAT overlay and find EntityUpdates arrays.
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

def find_arrays_in_overlay(bin_path):
    """Find EntityUpdates arrays in the BIN file."""
    
    print(f"Opening BIN file: {bin_path}")
    
    if not os.path.exists(bin_path):
        print(f"ERROR: File not found: {bin_path}")
        return
    
    file_size = os.path.getsize(bin_path)
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    
    with open(bin_path, 'rb') as f:
        data = f.read()
    
    print(f"Searching for overlay header pattern...")
    print(f"Looking for: 0x801BB6D4 0x801BBAD8 0x801BDC68 0x801BDAF0")
    
    # Search for the pattern
    header_pos = data.find(HEADER_PATTERN)
    
    if header_pos == -1:
        print("Pattern not found directly. Searching for individual values...")
        # Try a broader search approach
        header_pos = search_for_header_nearby(data)
        if header_pos == -1:
            print("Could not find overlay header pattern.")
            return
    
    print(f"\nFound overlay header at offset: 0x{header_pos:08X} ({header_pos:,} bytes)")
    
    # The overlay starts at this position
    overlay_start = header_pos
    
    # Search for candidate arrays after the header
    search_start = overlay_start + 16  # Start after the header pattern
    
    print(f"\nScanning for EntityUpdates arrays starting at offset: 0x{search_start:08X}")
    print("-" * 100)
    
    candidates = []
    
    # Scan through the overlay looking for arrays of function pointers
    for offset in range(search_start, len(data) - 32, 4):
        # Read 8+ consecutive 32-bit LE values
        array_data = []
        code_count = 0
        null_count = 0
        unknown_count = 0
        
        for i in range(20):  # Check up to 20 entries per potential array
            if offset + i*4 + 4 > len(data):
                break
            
            value = struct.unpack('<I', data[offset + i*4:offset + i*4 + 4])[0]
            classification = classify_pointer(value)
            array_data.append((value, classification))
            
            if classification in ["overlay_code", "dra_code", "base_exe"]:
                code_count += 1
            elif classification == "NULL":
                null_count += 1
            else:
                unknown_count += 1
        
        # Check if this looks like an EntityUpdates array
        # Need at least 8 entries, and mostly code pointers (with possible NULLs)
        if len(array_data) >= 8:
            total_code = code_count + null_count
            if total_code >= len(array_data) * 0.7:  # At least 70% are code or NULL
                # Filter out if there are too many non-code entries
                non_code_non_null = unknown_count
                if non_code_non_null <= len(array_data) * 0.3:  # Allow up to 30% unknown
                    candidates.append((offset, array_data))
    
    print(f"Found {len(candidates)} candidate arrays\n")
    
    # Print results
    for idx, (array_offset, array_data) in enumerate(candidates[:50], 1):  # Print first 50
        file_offset = array_offset
        print(f"Candidate #{idx} at offset 0x{file_offset:08X} ({file_offset:,})")
        print(f"  (In CAT overlay, would be at 0x80180000 + 0x{array_offset - overlay_start:08X})")
        
        # Print the first 10 entries
        for i, (value, classification) in enumerate(array_data[:10]):
            symbol = ""
            if classification == "overlay_code":
                symbol = "  [OVL] "
            elif classification == "dra_code":
                symbol = "  [DRA] "
            elif classification == "base_exe":
                symbol = "  [EXE] "
            elif classification == "overlay_data":
                symbol = "  [DAT] "
            elif classification == "NULL":
                symbol = "  [NULL]"
            else:
                symbol = "  [UNK] "
            
            print(f"    [{i}] {symbol} 0x{value:08X}")
        
        if len(array_data) > 10:
            print(f"    ... and {len(array_data) - 10} more entries")
        print()

def search_for_header_nearby(data):
    """Search for the header pattern allowing some variations."""
    # Search for the first known value
    value = struct.pack('<I', 0x801BB6D4)
    
    pos = 0
    while True:
        pos = data.find(value, pos)
        if pos == -1:
            break
        
        # Check if the next 3 values match
        if pos + 16 <= len(data):
            vals = struct.unpack('<4I', data[pos:pos+16])
            if vals == (0x801BB6D4, 0x801BBAD8, 0x801BDC68, 0x801BDAF0):
                return pos
        
        pos += 1
    
    return -1

if __name__ == "__main__":
    # Use the Track 1 BIN file (usually contains the main overlay data)
    bin_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"
    
    find_arrays_in_overlay(bin_path)
    
    print("\n" + "=" * 100)
    print("If no results found, trying Track 2...")
    print("=" * 100 + "\n")
    
    bin_path2 = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 2).bin"
    
    if os.path.exists(bin_path2):
        find_arrays_in_overlay(bin_path2)
