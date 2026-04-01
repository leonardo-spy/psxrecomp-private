import struct
import os

iso_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"

# CD-ROM .bin files use 2352-byte sectors
# Data starts at: sector * 2352 + 24 bytes (for sync/header)
SECTOR_SIZE = 2352
HEADER_OFFSET = 24
ISO_SECTOR_SIZE = 2048  # ISO-9660 data sector size

def read_sector_data(f, sector_num, size=2048):
    """Read data from a sector in a .bin file"""
    offset = sector_num * SECTOR_SIZE + HEADER_OFFSET
    f.seek(offset)
    return f.read(size)

# Open the ISO and read PVD (Primary Volume Descriptor) at sector 16
with open(iso_path, 'rb') as f:
    # Read PVD
    pvd_data = read_sector_data(f, 16, 2048)
    
    print("=== PRIMARY VOLUME DESCRIPTOR (Sector 16) ===")
    print(f"PVD Type: {pvd_data[0]}")
    print(f"Standard Identifier: {pvd_data[1:6].decode('ascii', errors='ignore')}")
    
    # Parse root directory extent (LBA) - at offset 156-159 (little-endian)
    root_dir_lba = struct.unpack('<I', pvd_data[156:160])[0]
    root_dir_size = struct.unpack('<I', pvd_data[164:168])[0]
    
    print(f"Root Directory LBA: {root_dir_lba}")
    print(f"Root Directory Size: {root_dir_size} bytes")
    print()
    
    # Read root directory entries
    print("=== ROOT DIRECTORY ENTRIES ===")
    root_data = read_sector_data(f, root_dir_lba, root_dir_size)
    
    offset = 0
    entry_count = 0
    files_found = []
    
    while offset < len(root_data) and entry_count < 100:
        if offset + 34 > len(root_data):
            break
        
        dir_rec_len = root_data[offset]
        if dir_rec_len == 0:
            break
        
        # Parse directory record
        extent_lba = struct.unpack('<I', root_data[offset+2:offset+6])[0]
        data_length = struct.unpack('<I', root_data[offset+10:offset+14])[0]
        file_flags = root_data[offset+25]
        name_len = root_data[offset+32]
        
        name = root_data[offset+33:offset+33+name_len].decode('ascii', errors='ignore')
        
        # Skip "." and ".."
        if name_len > 0 and name not in ['.', '..']:
            is_dir = (file_flags & 0x02) != 0
            dir_indicator = "[DIR]" if is_dir else "[FILE]"
            print(f"{entry_count:2d}. {dir_indicator:6s} LBA: {extent_lba:5d}  Size: {data_length:8d}  Name: {name}")
            files_found.append((name, extent_lba, data_length, is_dir))
        
        offset += dir_rec_len
        entry_count += 1
    
    print(f"\nTotal entries: {entry_count}")
    
    # Look for F_TITLE0.BIN and F_MAP.BIN specifically
    print("\n=== LOOKING FOR KEY FILES ===")
    for name, lba, size, is_dir in files_found:
        if 'TITLE' in name.upper() or 'MAP' in name.upper():
            print(f"Found: {name} at LBA {lba}, size {size}")
    
    # Try to read F_MAP.BIN from LBA 863
    print("\n=== READING F_MAP.BIN (LBA 863) ===")
    try:
        map_data = read_sector_data(f, 863, 32768)
        print(f"Read {len(map_data)} bytes from LBA 863")
        
        # F_MAP.BIN format: each entry is typically 8 bytes (or varies)
        # Common PS1 format: 4 bytes LBA + 4 bytes size
        print("First 20 entries (assuming 8-byte format with LBA + Size):")
        for i in range(min(20, len(map_data) // 8)):
            offset = i * 8
            entry_lba = struct.unpack('<I', map_data[offset:offset+4])[0]
            entry_size = struct.unpack('<I', map_data[offset+4:offset+8])[0]
            
            # Filter out padding (0xFFFFFFFF entries)
            if entry_lba != 0xFFFFFFFF and entry_size != 0xFFFFFFFF:
                print(f"  [{i:2d}] LBA: {entry_lba:6d}  Size: {entry_size:8d} bytes")
        
        print("\nAll non-zero F_MAP entries:")
        count = 0
        for i in range(0, min(4096, len(map_data) // 8)):
            offset = i * 8
            if offset + 8 > len(map_data):
                break
            entry_lba = struct.unpack('<I', map_data[offset:offset+4])[0]
            entry_size = struct.unpack('<I', map_data[offset+4:offset+8])[0]
            
            if entry_lba != 0 and entry_lba != 0xFFFFFFFF and entry_size != 0 and entry_size != 0xFFFFFFFF:
                print(f"  [{i:3d}] LBA: {entry_lba:6d}  Size: {entry_size:8d} bytes ({entry_size/1024:.1f}KB)")
                count += 1
                if count > 50:
                    print("  ... (truncated, too many entries)")
                    break
                    
    except Exception as e:
        print(f"Error reading F_MAP.BIN: {e}")

print("\n=== Done ===")
