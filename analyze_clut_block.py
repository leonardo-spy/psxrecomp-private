import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    # Read NO0.BIN into memory
    no0_lba = 0x7F16
    no0_size = 390540
    buf = b''
    for s in range((no0_size + 2047) // 2048):
        f.seek((no0_lba + s) * 2352 + 24)
        buf += f.read(2048)
    buf = buf[:no0_size]
    
    # Check the region around 0x016F7C - dump 8KB to see if there's a full CLUT block
    start = 0x016F7C
    print(f'=== NO0.BIN CLUT region starting at 0x{start:X} ===')
    for i in range(256):
        off = start + i * 32
        if off + 32 > no0_size:
            print(f'  (reached end of file at palette {i})')
            break
        words = struct.unpack_from('<16H', buf, off)
        unique = len(set(words))
        stp = sum(1 for w in words[1:] if w & 0x8000)
        has_8421 = 1 if 0x8421 in words else 0
        # Determine if this looks like valid CLUT
        is_valid = unique >= 6 and stp >= 6
        marker = '*' if is_valid else ' '
        if i < 32 or is_valid:
            print(f'  {marker} Pal {i:3d} (0x{off:06X}): {" ".join(f"{w:04X}" for w in words[:8])} ... [{unique}u {stp}s]')
    
    # Now let's look at what's contiguous before 0x016F7C
    print(f'\n=== Checking before 0x016F7C for CLUT start ===')
    for i in range(16):
        off = start - (16-i) * 32
        if off < 0:
            continue
        words = struct.unpack_from('<16H', buf, off)
        unique = len(set(words))
        stp = sum(1 for w in words[1:] if w & 0x8000)
        is_valid = unique >= 6 and stp >= 6
        marker = '*' if is_valid else ' '
        print(f'  {marker} off 0x{off:06X}: {" ".join(f"{w:04X}" for w in words[:8])} ... [{unique}u {stp}s]')
    
    # Check F_GAME.BIN CLUT block details - all 256 palettes
    print(f'\n=== F_GAME.BIN CLUT - how many valid palettes? ===')
    f_game_clut = b''
    for si in range(4):
        f.seek((0x61CE + 128 + si) * 2352 + 24)
        f_game_clut += f.read(2048)
    
    valid_count = 0
    for i in range(256):
        words = struct.unpack_from('<16H', f_game_clut, i * 32)
        unique = len(set(words))
        stp = sum(1 for w in words[1:] if w & 0x8000)
        if unique >= 6 and stp >= 6:
            valid_count += 1
    print(f'  Valid palettes in F_GAME.BIN CLUTs: {valid_count}/256')
    
    # Show F_GAME.BIN palette #2 (what the game uses for CLUT 544,240)
    words = struct.unpack_from('<16H', f_game_clut, 2 * 32)
    print(f'  F_GAME pal #2: {" ".join(f"{w:04X}" for w in words)}')
    words = struct.unpack_from('<16H', f_game_clut, 0 * 32)
    print(f'  F_GAME pal #0: {" ".join(f"{w:04X}" for w in words)}')
