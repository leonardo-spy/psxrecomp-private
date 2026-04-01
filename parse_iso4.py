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
    # Search for SLUS markers
    print("\nSearching for SLUS markers...")
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
        sector_num = pos // SECTOR_SIZE
        offset_in_sector = pos % SECTOR_SIZE
        print(f"Found SLUS at file offset 0x{pos:08x} ({pos:,}) - Sector {sector_num}, offset {offset_in_sector}")
        pos += 1
    
    # Check F_MAP.BIN at LBA 863
    print(f"\n=== EXAMINING F_MAP.BIN DATA (LBA 863) ===")
    map_data = read_sector_data(f, 863, 2048)
    
    print(f"First 16 bytes (hex): {map_data[:16].hex()}")
    
    print("\nFirst 256 bytes (hex):")
    for i in range(0, min(256, len(map_data)), 16):
        hex_str = " ".join(f"{b:02x}" for b in map_data[i:i+16])
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in map_data[i:i+16])
        print(f"  {i:03x}: {hex_str:<48} {ascii_str}")
    
    # Now check what's actually at the beginning of Track 1
    # PS1 Mode 2 CD data starts at sector 0
    # Let's look at sector 0-10
    print(f"\n=== FIRST FEW SECTORS OF ISO ===")
    for sect in [0, 1, 2, 10, 16]:
        sect_data = read_sector_data(f, sect, 64)
        print(f"Sector {sect}: {sect_data.hex()}")
        # Try to interpret as ASCII
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in sect_data)
        print(f"          ASCII: {ascii_str}")
    
    # Look for the actual directory entries
    # In PS1 Mode 2 ISO, files are stored differently
    # Let's look at the SLUS file which we know exists at offset 563200 bytes from end
    print(f"\n=== LOOKING AT SLUS_000.67 FILE ===")
    f.seek(file_size - 563200)
    slus_header = f.read(64)
    print(f"SLUS file header: {slus_header.hex()}")
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in slus_header)
    print(f"                ASCII: {ascii_str}")
    
    # The file is at a specific offset. Let's find it in the directory structure.
    # Read all directory entries by looking at FAT or file table
    print(f"\n=== READING ALL VALID F_MAP ENTRIES ===")
    
    # Get all the F_MAP data (32KB)
    f.seek(863 * SECTOR_SIZE + HEADER_OFFSET)
    map_full = f.read(32768)
    
    print(f"Total F_MAP size: {len(map_full)} bytes")
    
    # Parse as 8-byte entries (LBA + Size)
    print("\nAll valid entries in F_MAP (LBA < 2^30, Size < 2^30):")
    entries = []
    for i in range(0, len(map_full) // 8):
        offset = i * 8
        lba = struct.unpack('<I', map_full[offset:offset+4])[0]
        size = struct.unpack('<I', map_full[offset+4:offset+8])[0]
        
        # Reasonable bounds for PS1
        if 0 < lba < 0x20000000 and 0 < size < 0x20000000:
            entries.append((i, lba, size))
    
    # Print first and last entries to understand the structure
    print(f"\nTotal valid entries: {len(entries)}")
    if entries:
        print("\nFirst 20 entries:")
        for idx, lba, size in entries[:20]:
            size_mb = size / 1024 / 1024
            print(f"  Entry[{idx:3d}]: LBA {lba:8d}  Size {size:10d} ({size_mb:7.2f} MB)")
        
        print("\nLast 10 entries:")
        for idx, lba, size in entries[-10:]:
            size_mb = size / 1024 / 1024
            print(f"  Entry[{idx:3d}]: LBA {lba:8d}  Size {size:10d} ({size_mb:7.2f} MB)")

print("\nDone.")
