import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    # Read NO0.BIN header (overlay 0, at LBA 0x7F16)
    no0_lba = 0x7F16
    f.seek(no0_lba * 2352 + 24)
    header = f.read(256)
    
    print('=== NO0.BIN Full Overlay Header ===')
    # SOTN decomp Overlay struct:
    fields = [
        (0x00, 'Update'),
        (0x04, 'HitDetection'),
        (0x08, 'UpdateRoomPosition'),
        (0x0C, 'InitRoomEntities'),
        (0x10, 'spriteBanks'),
        (0x14, 'cluts'),
        (0x18, 'layouts'),
        (0x1C, 'tileDefinitions'),
        (0x20, 'sprites'),
        (0x24, 'entityGfxs'),
        (0x28, 'tileBankIds[4]'),
        (0x2C, 'entityLayouts'),
        (0x30, 'tileLayoutIds[4]'),
        (0x34, 'roomsX'),
        (0x38, 'roomsY'),
        (0x3C, 'clutBanks'),
    ]
    
    base_addr = 0x80180000
    for off, name in fields:
        val = struct.unpack_from('<I', header, off)[0]
        if 'ids' in name.lower():
            b = header[off:off+4]
            print(f'  +0x{off:02X} {name:25s} = [{b[0]}, {b[1]}, {b[2]}, {b[3]}]')
        else:
            file_off = val - base_addr if val >= base_addr else None
            extra = f' (file offset 0x{file_off:X})' if file_off is not None and file_off >= 0 else ''
            print(f'  +0x{off:02X} {name:25s} = 0x{val:08X}{extra}')
    
    # Follow clutBanks pointer
    clut_banks_ptr = struct.unpack_from('<I', header, 0x3C)[0]
    clut_banks_off = clut_banks_ptr - base_addr
    print(f'\n=== clutBanks at file offset 0x{clut_banks_off:X} ===')
    
    # Read clutBanks data (it's a pointer table)
    sec_in_file = clut_banks_off // 2048
    byte_in_sec = clut_banks_off % 2048
    f.seek((no0_lba + sec_in_file) * 2352 + 24 + byte_in_sec)
    cb_data = f.read(128)
    cb_words = struct.unpack_from('<32I', cb_data)
    print(f'  First 16 words:')
    for i in range(16):
        val = cb_words[i]
        extra = ''
        if base_addr <= val < base_addr + 0x100000:
            extra = f' (file off 0x{val-base_addr:X})'
        print(f'    [{i:2d}] 0x{val:08X}{extra}')
    
    # Follow cluts pointer
    cluts_ptr = struct.unpack_from('<I', header, 0x14)[0]
    cluts_off = cluts_ptr - base_addr
    print(f'\n=== cluts at file offset 0x{cluts_off:X} ===')
    sec_in_file = cluts_off // 2048
    byte_in_sec = cluts_off % 2048
    f.seek((no0_lba + sec_in_file) * 2352 + 24 + byte_in_sec)
    cl_data = f.read(128)
    cl_words = struct.unpack_from('<32I', cl_data)
    print(f'  First 16 words:')
    for i in range(16):
        val = cl_words[i]
        extra = ''
        if base_addr <= val < base_addr + 0x100000:
            extra = f' (file off 0x{val-base_addr:X})'
        print(f'    [{i:2d}] 0x{val:08X}{extra}')
    
    # Follow first clutBanks entry to see actual CLUT data
    first_cb = cb_words[0]
    if base_addr <= first_cb < base_addr + 0x100000:
        first_off = first_cb - base_addr
        print(f'\n=== First clutBank entry data at file offset 0x{first_off:X} ===')
        sec_in_file = first_off // 2048
        byte_in_sec = first_off % 2048
        f.seek((no0_lba + sec_in_file) * 2352 + 24 + byte_in_sec)
        data = f.read(128)
        words16 = struct.unpack_from('<64H', data)
        # Print as 4 rows of 16 (4 palettes)
        for row in range(4):
            start = row * 16
            vals = words16[start:start+16]
            non_zero = sum(1 for v in vals if v != 0)
            print(f'  Pal {row}: {" ".join(f"{v:04X}" for v in vals)} [{non_zero} nz]')
    
    # Also follow the first cluts entry
    first_cl = cl_words[0]
    if base_addr <= first_cl < base_addr + 0x100000:
        first_off = first_cl - base_addr
        print(f'\n=== First cluts entry data at file offset 0x{first_off:X} ===')
        sec_in_file = first_off // 2048
        byte_in_sec = first_off % 2048
        f.seek((no0_lba + sec_in_file) * 2352 + 24 + byte_in_sec)
        data = f.read(128)
        words16 = struct.unpack_from('<64H', data)
        for row in range(4):
            start = row * 16
            vals = words16[start:start+16]
            non_zero = sum(1 for v in vals if v != 0)
            print(f'  Pal {row}: {" ".join(f"{v:04X}" for v in vals)} [{non_zero} nz]')
