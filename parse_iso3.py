import struct
import os

iso_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"

# CD-ROM .bin files use 2352-byte sectors
SECTOR_SIZE = 2352
HEADER_OFFSET = 24

def read_sector_data(f, sector_num, size=2048):
    """Read data from a sector in a .bin file"""
    offset = sector_num * SECTOR_SIZE + HEADER_OFFSET
    f.seek(offset)
    return f.read(size)

# Get file size
file_size = os.path.getsize(iso_path)
max_sector = file_size // SECTOR_SIZE
max_lba_data = file_size // 2048

print(f"File size: {file_size:,} bytes")
print(f"File size in sectors (2352-byte): {max_sector:,}")
print(f"File size in 2048-byte LBA blocks: {max_lba_data:,}")

with open(iso_path, 'rb') as f:
    # The .bin file contains 2352-byte sectors from a CD
    # But PS1 ISOs often have a custom layout
    # Let's look for "SLUS" (PS1 game identifier)
    
    print("\n=== Searching for SLUS markers ===")
    f.seek(0)
    data = f.read(min(1000000, file_size))
    
    slus_positions = []
    search_term = b'SLUS'
    pos = 0
    while True:
        pos = data.find(search_term, pos)
        if pos == -1:
            break
        slus_positions.append(pos)
        print(f"Found SLUS at file offset 0x{pos:08x} ({pos:,})")
        pos += 1
    
    # Check if this might be at a sector boundary
    if slus_positions:
        first_pos = slus_positions[0]
        sector_num = first_pos // SECTOR_SIZE
        offset_in_sector = first_pos % SECTOR_SIZE
        print(f"  → Sector {sector_num}, offset {offset_in_sector} in sector")
        
        # The actual data might start right at the sector
        if offset_in_sector == HEADER_OFFSET:
            print(f"  → This looks like data at sector boundary!")
    
    # Now look at the ISO structure from the SLUS position
    if slus_positions:
        # Read from the SLUS location backwards to find the ISO header
        iso_start = slus_positions[0]
        print(f"\n=== Looking for ISO structure near SLUS ===")
        
        # PS1 discs might not follow standard ISO-9660 
        # Let's read the directory info differently
        f.seek(0)
        all_data = f.read(min(10000000, file_size))
        
        # Look for the string "PSXES" or common PS1 identifiers
        print("\nSearching for common PS1/game file identifiers...")
        
        for identifier in [b'TITLE0', b'F_MAP', b'ST0', b'F_TITLE']:
            pos = 0
            count = 0
            while True:
                pos = all_data.find(identifier, pos)
                if pos == -1 or count >= 3:
                    break
                print(f"Found '{identifier.decode('ascii', errors='ignore')}' at offset 0x{pos:08x} ({pos:,})")
                pos += 1
                count += 1
    
    # Direct check on F_MAP.BIN at LBA 863
    print(f"\n=== Examining F_MAP.BIN data (LBA 863) ===")
    map_data = read_sector_data(f, 863, 2048)
    
    # Check the first few bytes
    print(f"First 16 bytes: {map_data[:16].hex()}")
    print(f"As ASCII: {map_data[:16]}")
    
    # The entries seem to be 8 bytes each, but with padding at start
    # Let's check if there's a header
    print("\nFirst 256 bytes (hex):")
    for i in range(0, min(256, len(map_data)), 16):
        hex_str = " ".join(f"{b:02x}" for b in map_data[i:i+16])
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in map_data[i:i+16])
        print(f"  {i:03x}: {hex_str:<48} {ascii_str}")
    
    # Try to find the pattern - maybe there's file metadata at the start
    print("\n=== Reading actual directory/file listing ===")
    
    # Let's try to use the tmp_list_iso.exe by looking at its behavior
    # Or we can read from known sectors. Let's check the SLUS file we found
    f.seek(0)
    slus_file_offset = file_size - 563200  # SLUS_000.67 is 563200 bytes at end
    print(f"SLUS file should be around offset {slus_file_offset:,}")
    
    f.seek(slus_file_offset)
    slus_data = f.read(512)
    print(f"SLUS file header (first 64 bytes): {slus_data[:64].hex()}")
    
print("\n=== Done ===")
