import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    # F_GAME.BIN at LBA 0x61CE, 132 sectors = 128 tiles + 4 CLUTs
    f_game_lba = 0x61CE
    print('=== F_GAME.BIN CLUT data (last 4 sectors) ===')
    clut_buf = b''
    for si in range(4):
        f.seek((f_game_lba + 128 + si) * 2352 + 24)
        clut_buf += f.read(2048)
    
    words = struct.unpack(f'<{len(clut_buf)//2}H', clut_buf)
    for p in range(16):  # First 16 palettes
        start = p * 16
        pal = words[start:start+16]
        non_zero = sum(1 for w in pal if w != 0)
        print(f'  Pal {p:3d} ({512+p*16},240): {" ".join(f"{w:04X}" for w in pal)} [{non_zero} non-zero]')
    
    unique = len(set(words[:512]))
    print(f'\n  Unique entries in first 512: {unique}')
    ffff_count = sum(1 for w in words if w == 0xFFFF)
    zero_count = sum(1 for w in words if w == 0x0000)
    print(f'  0xFFFF: {ffff_count}/4096, 0x0000: {zero_count}/4096')
    
    # Now check: where are the CLUTs for stage NO0?
    # The NO0.BIN overlay (390540 bytes) might contain embedded CLUT data
    print('\n=== NO0.BIN overlay analysis ===')
    no0_lba = 0x7F16
    no0_size = 390540
    # Read first 64 bytes (header)
    f.seek(no0_lba * 2352 + 24)
    header = f.read(64)
    print(f'NO0.BIN header: {header[:32].hex()}')
    print(f'  As words: {" ".join(f"{struct.unpack_from("<I", header, i)[0]:08X}" for i in range(0, 32, 4))}')
    
    # Look at the overlay structure: first 3 words are often function pointers
    for i in range(0, min(32, len(header)), 4):
        val = struct.unpack_from('<I', header, i)[0]
        print(f'  offset {i:3d}: 0x{val:08X}')
    
    # The SIM data might be at a specific offset within the overlay
    # In SOTN, STAGE_PRG_PTR+0x40000 = 0x801C0000 is where CLUTs are stored
    # If overlay is at 0x80180000, offset 0x40000 = 262144 bytes from start
    # That's well within NO0.BIN's 390540 bytes!
    
    # Read data at offset 0x40000 (262144) in the overlay
    clut_offset = 0x40000
    sec_in_file = clut_offset // 2048  # = 128
    byte_in_sec = clut_offset % 2048   # = 0
    print(f'\n=== Data at NO0.BIN offset 0x{clut_offset:X} (sector {sec_in_file} in file) ===')
    
    overlay_clut_buf = b''
    for si in range(4):
        f.seek((no0_lba + sec_in_file + si) * 2352 + 24)
        overlay_clut_buf += f.read(2048)
    
    ovl_words = struct.unpack(f'<{len(overlay_clut_buf)//2}H', overlay_clut_buf)
    for p in range(16):
        start = p * 16
        pal = ovl_words[start:start+16]
        non_zero = sum(1 for w in pal if w != 0)
        print(f'  Pal {p:3d}: {" ".join(f"{w:04X}" for w in pal)} [{non_zero} non-zero]')
    
    unique = len(set(ovl_words[:512]))
    print(f'  Unique entries in first 512: {unique}')
    
    # Also check if F_NO0.BIN has CLUTs embedded (it shouldn't, but check)
    print('\n=== F_NO0.BIN analysis ===')
    f_no0_lba = 0x7E5D
    # Read last sector of F_NO0.BIN
    f.seek((f_no0_lba + 127) * 2352 + 24)
    last_sec = f.read(32)
    print(f'Last sector first 32 bytes: {last_sec.hex()}')
    # Check if there are sectors AFTER F_NO0.BIN before SD_ZKNO0.VH
    # F_NO0.BIN ends at LBA 0x7E5D+128=0x7EDD, which is exactly where SD_ZKNO0.VH starts
    # So there's NO gap for CLUT data after the tile file
    print(f'F_NO0.BIN ends at LBA 0x{f_no0_lba+128:X}, SD_ZKNO0.VH at 0x7EDD')
