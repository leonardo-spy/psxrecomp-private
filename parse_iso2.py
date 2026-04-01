import struct

iso_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"

# CD-ROM .bin files use 2352-byte sectors
# Data starts at: sector * 2352 + 24 bytes (for sync/header)
SECTOR_SIZE = 2352
HEADER_OFFSET = 24

def read_sector_data(f, sector_num, size=2048):
    """Read data from a sector in a .bin file"""
    offset = sector_num * SECTOR_SIZE + HEADER_OFFSET
    f.seek(offset)
    return f.read(size)

def hex_dump(data, title=""):
    """Print hex dump of data"""
    if title:
        print(f"\n{title}")
    for i in range(0, min(len(data), 512), 16):
        hex_str = " ".join(f"{b:02x}" for b in data[i:i+16])
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data[i:i+16])
        print(f"{i:04x}: {hex_str:<48} {ascii_str}")

with open(iso_path, 'rb') as f:
    # Check first few sectors to understand the layout
    print("=== Checking first few sectors ===")
    
    # Sector 0
    s0 = read_sector_data(f, 0, 2048)
    print(f"Sector 0 first 16 bytes: {s0[:16].hex()}")
    
    # Sector 16 (PVD)
    s16 = read_sector_data(f, 16, 2048)
    print(f"Sector 16 first byte: {s16[0]} (should be 0x01 for PVD)")
    print(f"Sector 16 ident: {s16[1:6]} = {s16[1:6].decode('ascii', errors='ignore')}")
    
    # Check if this looks like a valid PVD
    if s16[0] == 1 and s16[1:6] == b'CD001':
        print("✓ Valid PVD found at sector 16")
        
        # Read root dir info
        root_lba_le = struct.unpack('<I', s16[156:160])[0]
        root_lba_be = struct.unpack('>I', s16[160:164])[0]
        root_size_le = struct.unpack('<I', s16[164:168])[0]
        root_size_be = struct.unpack('>I', s16[168:172])[0]
        
        print(f"Root LBA (LE): {root_lba_le}")
        print(f"Root LBA (BE): {root_lba_be}")
        print(f"Root Size (LE): {root_size_le}")
        print(f"Root Size (BE): {root_size_be}")
        
        # Try little-endian (typical for ISO)
        if root_size_le < 100000:
            print(f"\n✓ Using little-endian root info")
            root_lba = root_lba_le
            root_size = root_size_le
        else:
            print(f"\n⚠ Root size seems wrong, trying to find directory records...")
            root_lba = root_lba_le
            root_size = 10 * 2048  # Read first 10 sectors
    
    # Read root directory
    print(f"\n=== ROOT DIRECTORY at LBA {root_lba} ===")
    root_data = read_sector_data(f, root_lba, min(root_size, 50000))
    
    print(f"Read {len(root_data)} bytes")
    print(f"First 64 bytes (hex):")
    hex_dump(root_data[:64])
    
    # Parse directory records
    print("\n=== PARSING DIRECTORY RECORDS ===")
    offset = 0
    entry_num = 0
    
    while offset < len(root_data) and entry_num < 50:
        if offset + 34 > len(root_data):
            break
        
        dir_len = root_data[offset]
        if dir_len == 0:
            print(f"End of directory at offset {offset}")
            break
        
        if dir_len < 33:  # Invalid record length
            print(f"Invalid record at offset {offset}, length {dir_len}")
            break
        
        try:
            extent_lba = struct.unpack('<I', root_data[offset+2:offset+6])[0]
            data_length = struct.unpack('<I', root_data[offset+10:offset+14])[0]
            file_flags = root_data[offset+25]
            name_len = root_data[offset+32]
            
            is_dir = (file_flags & 0x02) != 0
            name = root_data[offset+33:offset+33+name_len].decode('ascii', errors='ignore')
            
            if name_len > 0 and name not in ['.', '..']:
                dir_str = "[DIR]" if is_dir else "[FILE]"
                print(f"{entry_num:2d}. {dir_str:6s} LBA:{extent_lba:6d}  Size:{data_length:10d}  Name: {name}")
            
            offset += dir_len
            entry_num += 1
        except Exception as e:
            print(f"Error parsing record at offset {offset}: {e}")
            break
    
    # Now read F_MAP.BIN from LBA 863
    print(f"\n=== F_MAP.BIN at LBA 863 ===")
    map_data = read_sector_data(f, 863, 32768)
    
    print(f"Read {len(map_data)} bytes")
    
    # Parse as LBA/Size pairs
    print("\nFirst 32 entries (format: LBA + Size as 32-bit LE values):")
    valid_count = 0
    for i in range(min(32, len(map_data) // 8)):
        offset = i * 8
        lba = struct.unpack('<I', map_data[offset:offset+4])[0]
        size = struct.unpack('<I', map_data[offset+4:offset+8])[0]
        
        # Filter clearly invalid entries
        if lba < 0x40000000 and size < 0x40000000:
            print(f"  [{i:3d}] LBA: {lba:8d}  Size: {size:10d} (0x{size:08x}) bytes")
            valid_count += 1
    
    print(f"\nValid-looking entries (all that seem reasonable):")
    count = 0
    for i in range(len(map_data) // 8):
        offset = i * 8
        lba = struct.unpack('<I', map_data[offset:offset+4])[0]
        size = struct.unpack('<I', map_data[offset+4:offset+8])[0]
        
        # Reasonable bounds: LBA < 2^29, Size < 2^29 (realistic for PS1 game)
        if 0 < lba < 0x20000000 and 0 < size < 0x20000000:
            print(f"  [{i:3d}] LBA: {lba:8d}  Size: {size:10d} ({size/1024/1024:.1f}MB)")
            count += 1
            if count >= 40:
                print("  ... (truncated)")
                break

print("\n=== Done ===")
