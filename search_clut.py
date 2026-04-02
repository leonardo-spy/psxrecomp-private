import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    no0_lba = 0x7F16
    no0_size = 390540  # 0x5F58C bytes
    
    # Read entire NO0.BIN into memory
    buf = b''
    sectors = (no0_size + 2047) // 2048
    for s in range(sectors):
        f.seek((no0_lba + s) * 2352 + 24)
        buf += f.read(2048)
    buf = buf[:no0_size]
    
    # Search for CLUT patterns: 16 consecutive uint16 values where:
    # - entry[0] = 0x0000 (transparent)
    # - At least 8 entries have STP bit set (0x8000)
    # - At least 8 unique values
    print('=== Searching NO0.BIN for PS1 CLUT patterns ===')
    found = []
    for off in range(0, no0_size - 32, 2):
        words = struct.unpack_from('<16H', buf, off)
        if words[0] != 0x0000:
            continue
        stp_count = sum(1 for w in words[1:] if w & 0x8000)
        unique = len(set(words))
        if stp_count >= 8 and unique >= 8:
            found.append((off, words, unique, stp_count))
    
    print(f'Found {len(found)} candidate CLUT palettes')
    for i, (off, words, unique, stp) in enumerate(found[:20]):
        print(f'  [{i:3d}] offset 0x{off:06X} ({unique} unique, {stp} STP): {" ".join(f"{w:04X}" for w in words)}')
    
    if len(found) > 20:
        print(f'  ... and {len(found)-20} more')
    
    # Also search F_GAME.BIN style pattern (palette with grayscale progression)
    # F_GAME.BIN pal0 was: 0000 8421 84AB 8D2F 91D6 929B 994A A5CE
    # Look for 0x8421 (very common SOTN base gray) preceded by 0x0000
    print('\n=== Searching for 0x8421 pattern (common SOTN gray) ===')
    for off in range(0, no0_size - 4, 2):
        w0, w1 = struct.unpack_from('<2H', buf, off)
        if w0 == 0x0000 and w1 == 0x8421:
            words = struct.unpack_from('<16H', buf, off)
            unique = len(set(words))
            stp = sum(1 for w in words[1:] if w & 0x8000)
            print(f'  offset 0x{off:06X}: {" ".join(f"{w:04X}" for w in words)} [{unique}u {stp}s]')
    
    # Also search DRA.BIN for CLUT data (it contains default CLUTs)
    print('\n=== Checking if DRA.BIN has stage-loading CLUT data ===')
    dra_lba = 0x12B
    dra_size = 1153136
    # Read first 1024 sectors of DRA.BIN (enough to search)
    dra_buf = b''
    dra_sectors = min(564, (dra_size + 2047) // 2048)
    for s in range(dra_sectors):
        f.seek((dra_lba + s) * 2352 + 24)
        dra_buf += f.read(2048)
    dra_buf = dra_buf[:dra_size]
    
    # Search for 0x8421 pattern in DRA.BIN
    hits = 0
    for off in range(0, len(dra_buf) - 4, 2):
        w0, w1 = struct.unpack_from('<2H', dra_buf, off)
        if w0 == 0x0000 and w1 == 0x8421:
            words = struct.unpack_from('<16H', dra_buf, off)
            unique = len(set(words))
            stp = sum(1 for w in words[1:] if w & 0x8000)
            if unique >= 8 and stp >= 8:
                addr = 0x800A0000 + off
                print(f'  DRA offset 0x{off:06X} (addr 0x{addr:08X}): {" ".join(f"{w:04X}" for w in words)} [{unique}u {stp}s]')
                hits += 1
                if hits >= 5:
                    break
    if hits == 0:
        print('  No 0x8421 CLUT pattern found in DRA.BIN')
