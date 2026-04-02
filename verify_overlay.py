import struct

iso_path = r"C:\Users\Leona\Documents\GitHub\psxrecomp\CastlevaniaRecomp\isos\Castlevania - Symphony of the Night (USA) (Track 1).bin"

# Sector parameters
SECTOR_SIZE = 2352  # Raw BIN format
USER_DATA_OFFSET = 24  # User data starts at byte 24 in each sector

# Overlay F_TITLE0 parameters
OVERLAY_START_SECTOR = 30031
OVERLAY_LOAD_ADDRESS = 0x80180000
OVERLAY_SIZE = 355112

# Task 1: Read first 32 bytes from sector 30031
sector_byte_offset = OVERLAY_START_SECTOR * SECTOR_SIZE + USER_DATA_OFFSET
print(f"Task 1: Reading first 32 bytes from sector {OVERLAY_START_SECTOR}")
print(f"Sector byte offset: {sector_byte_offset} (0x{sector_byte_offset:X})")
print(f"Sector in file: sector {OVERLAY_START_SECTOR} * {SECTOR_SIZE} = {OVERLAY_START_SECTOR * SECTOR_SIZE} + 24 offset = {sector_byte_offset}\n")

try:
    with open(iso_path, 'rb') as f:
        f.seek(sector_byte_offset)
        first_32_bytes = f.read(32)
        
        print("First 32 bytes (hex):")
        hex_str = ' '.join(f'{b:02x}' for b in first_32_bytes)
        print(hex_str)
        print()
        
        # Also show as 32-bit words for better readability
        print("As 32-bit words (little-endian):")
        for i in range(0, 32, 4):
            word = struct.unpack('<I', first_32_bytes[i:i+4])[0]
            print(f"  +0x{i:02X}: 0x{word:08X}")
        print()
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Task 2: Read data at overlay offset 0x2AED8
overlay_offset = 0x2AED8
sector_offset = overlay_offset // SECTOR_SIZE
offset_in_sector = overlay_offset % SECTOR_SIZE

target_sector = OVERLAY_START_SECTOR + sector_offset
target_byte_offset = target_sector * SECTOR_SIZE + USER_DATA_OFFSET + offset_in_sector

print(f"Task 2: Reading data at overlay offset 0x{overlay_offset:X}")
print(f"This is {overlay_offset} bytes = {sector_offset} sectors + {offset_in_sector} bytes into sector")
print(f"Target sector: {OVERLAY_START_SECTOR} + {sector_offset} = {target_sector}")
print(f"Byte offset in file: {target_byte_offset} (0x{target_byte_offset:X})")
print(f"Memory address: 0x{OVERLAY_LOAD_ADDRESS + overlay_offset:08X}\n")

try:
    with open(iso_path, 'rb') as f:
        f.seek(target_byte_offset)
        mips_data = f.read(64)  # Read 64 bytes to see more context
        
        print("64 bytes at this location (hex):")
        for i in range(0, 64, 16):
            hex_str = ' '.join(f'{b:02x}' for b in mips_data[i:i+16])
            print(f"  +0x{i:02X}: {hex_str}")
        print()
        
        print("As 32-bit words (little-endian - MIPS format):")
        for i in range(0, min(64, len(mips_data)), 4):
            if i + 4 <= len(mips_data):
                word = struct.unpack('<I', mips_data[i:i+4])[0]
                print(f"  +0x{i:02X} (0x{OVERLAY_LOAD_ADDRESS + overlay_offset + i:08X}): 0x{word:08X}", end="")
                
                # Decode MIPS instruction patterns
                opcode = (word >> 26) & 0x3F
                rs = (word >> 21) & 0x1F
                rt = (word >> 16) & 0x1F
                imm = word & 0xFFFF
                
                if word & 0xFFFF0000 == 0x27BD0000:  # ADDIU sp, sp, -N
                    offset = struct.unpack('<h', struct.pack('<H', imm))[0]
                    print(f"  <- ADDIU sp, sp, {offset}")
                elif word & 0xFC1F0000 == 0xAFB00000:  # SW reg, offset(sp)
                    print(f"  <- SW instruction")
                elif word & 0xFC000000 == 0x3C000000:  # LUI reg, imm
                    print(f"  <- LUI instruction")
                else:
                    print()
        print()
        
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

print("Verification complete!")
