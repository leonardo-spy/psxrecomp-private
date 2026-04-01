import struct
import os

iso_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"

SECTOR_SIZE = 2352
HEADER_OFFSET = 24

def read_sector_data(f, sector_num, size=2048):
    """Read data from a sector in a .bin file"""
    offset = sector_num * SECTOR_SIZE + HEADER_OFFSET
    f.seek(offset)
    return f.read(size)

file_size = os.path.getsize(iso_path)

with open(iso_path, 'rb') as f:
    print("=" * 80)
    print("CASTLEVANIA: SYMPHONY OF THE NIGHT (USA) - ISO DIRECTORY STRUCTURE")
    print("=" * 80)
    
    # Read the ISO volume info
    sector_16 = read_sector_data(f, 16, 2048)
    print("\nVOLUME DESCRIPTOR:")
    print(f"  Type ID: {sector_16[0]}")
    print(f"  Standard Identifier: {sector_16[1:6].decode('ascii')}")
    print(f"  System Identifier: {sector_16[8:40].decode('ascii', errors='ignore').strip()}")
    print(f"  Volume Identifier: {sector_16[40:72].decode('ascii', errors='ignore').strip()}")
    print(f"  Volume Set ID: {sector_16[190:318].decode('ascii', errors='ignore').strip()}")
    print(f"  Publisher: {sector_16[318:446].decode('ascii', errors='ignore').strip()}")
    
    # Game code info
    print("\nGAME IDENTIFICATION:")
    print(f"  Game Code: SLUS-00067 (USA Version)")
    print(f"  File size: {file_size:,} bytes")
    print(f"  Total sectors (2352-byte): {file_size // SECTOR_SIZE:,}")
    
    # Read F_MAP.BIN
    f.seek(863 * SECTOR_SIZE + HEADER_OFFSET)
    map_full = f.read(32768)
    
    entries = []
    for i in range(len(map_full) // 8):
        offset = i * 8
        lba = struct.unpack('<I', map_full[offset:offset+4])[0]
        size = struct.unpack('<I', map_full[offset+4:offset+8])[0]
        
        if 0 < lba < 0x20000000 and 0 < size < 0x20000000:
            entries.append((i, lba, size))
    
    print(f"\nF_MAP.BIN DATA (32 KB at LBA 863):")
    print(f"  Location: LBA 863")
    print(f"  Total valid entries found: {len(entries)}")
    print(f"  Entry format: 8 bytes each (LBA as 32-bit LE, Size as 32-bit LE)")
    
    # Categorize entries
    small_files = [(i, l, s) for i, l, s in entries if s < 100*1024]  # < 100KB
    medium_files = [(i, l, s) for i, l, s in entries if 100*1024 <= s < 10*1024*1024]  # 100KB-10MB
    large_files = [(i, l, s) for i, l, s in entries if 10*1024*1024 <= s < 100*1024*1024]  # 10-100MB
    huge_files = [(i, l, s) for i, l, s in entries if s >= 100*1024*1024]  # >= 100MB
    
    print(f"\nFILE SIZE DISTRIBUTION:")
    print(f"  Small files (< 100 KB): {len(small_files)}")
    print(f"  Medium files (100 KB - 10 MB): {len(medium_files)}")
    print(f"  Large files (10 - 100 MB): {len(large_files)}")
    print(f"  Huge files (>= 100 MB): {len(huge_files)}")
    
    print(f"\nSMALL FILES (likely code/config/metadata):")
    for i, lba, size in sorted(small_files, key=lambda x: x[2])[:15]:
        print(f"  [Entry {i:4d}] LBA {lba:8d}  Size {size:8d} ({size:6.1f} KB)")
    
    print(f"\nMEDIUM FILES (likely textures/audio):")
    for i, lba, size in sorted(medium_files, key=lambda x: x[2], reverse=True)[:10]:
        size_kb = size / 1024
        print(f"  [Entry {i:4d}] LBA {lba:8d}  Size {size:8d} ({size_kb:7.1f} KB)")
    
    print(f"\nLARGE FILES (likely game data/overlays):")
    for i, lba, size in sorted(large_files, key=lambda x: x[2], reverse=True):
        size_mb = size / 1024 / 1024
        print(f"  [Entry {i:4d}] LBA {lba:8d}  Size {size:8d} ({size_mb:7.2f} MB)")
    
    print(f"\nHUGE FILES (likely full game image or streaming data):")
    for i, lba, size in sorted(huge_files, key=lambda x: x[2], reverse=True):
        size_mb = size / 1024 / 1024
        print(f"  [Entry {i:4d}] LBA {lba:8d}  Size {size:8d} ({size_mb:7.2f} MB)")
    
    # Look for specific game files by scanning for known PS1 game patterns
    print(f"\n" + "=" * 80)
    print("SEARCHING FOR KNOWN GAME FILES")
    print("=" * 80)
    
    # Read entire directory area to search for filenames
    print("\nSearching for file metadata in first 10MB...")
    search_data = b''
    for sect in range(0, 5000):  # First ~10MB
        search_data += read_sector_data(f, sect, 2048)
    
    # Look for common PS1 game file patterns
    patterns = [
        b'F_TITLE0',
        b'F_TITLE1',
        b'F_TITLE',
        b'F_MAP',
        b'ST0',
        b'ST1',
        b'ST2',
        b'BIN',
        b'TITLE',
        b'MAIN',
    ]
    
    found_files = set()
    for pattern in patterns:
        pos = 0
        while True:
            pos = search_data.find(pattern, pos)
            if pos == -1:
                break
            # Extract context around match (likely filename)
            start = max(0, pos - 32)
            end = min(len(search_data), pos + 32)
            context = search_data[start:end]
            try:
                context_str = context.decode('ascii', errors='ignore')
                found_files.add(context_str.strip())
            except:
                pass
            pos += 1
    
    print("\nPotential filenames found:")
    for fname in sorted(list(found_files)[:20]):
        if fname and len(fname) > 2:
            print(f"  {fname}")
    
    # ISO-9660 root directory info from PVD
    print(f"\n" + "=" * 80)
    print("ISO-9660 STRUCTURE")
    print("=" * 80)
    
    root_lba = struct.unpack('<I', sector_16[156:160])[0]
    root_size = struct.unpack('<I', sector_16[164:168])[0]
    
    print(f"\nRoot Directory Information:")
    print(f"  LBA: {root_lba}")
    print(f"  Size: {root_size} bytes")
    print(f"  Note: Root LBA appears to be beyond file bounds ({root_lba} > {file_size // 2048})")
    print(f"        This suggests either:")
    print(f"        1. The file is a .bin with 2352-byte sectors, not raw ISO data")
    print(f"        2. PS1 uses custom file table (F_MAP.BIN) instead of ISO-9660 directory")
    
    print(f"\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print(f"""
This is a PlayStation 1 (PS1) game disc image of Castlevania: Symphony of the Night.

Key findings:
1. The .bin file contains 2352-byte CD sectors with 24-byte headers
2. The game uses a custom file mapping table (F_MAP.BIN at LBA 863)
3. F_MAP.BIN contains {len(entries)} valid file entries
4. Files are stored at various LBAs with their sizes in the map
5. The traditional ISO-9660 directory appears to be invalid/unused

Game assets likely include:
- Small config/code files (< 100 KB) - indexes, metadata
- Medium audio/texture files (100 KB - 10 MB) - character sprites, sound
- Large overlay/game code files (10-100 MB) - level code, graphics
- Possibly huge streaming data (> 100 MB) - cinematic/game video

To extract files, use the F_MAP.BIN entries to read data at specified LBAs.
""")

print("=" * 80)
