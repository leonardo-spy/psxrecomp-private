import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    no0_lba = 0x7F16
    base_addr = 0x80180000
    
    def read_overlay_bytes(file_offset, count):
        """Read bytes from within the overlay file at given offset"""
        sec_in_file = file_offset // 2048
        byte_in_sec = file_offset % 2048
        result = b''
        while len(result) < count:
            remaining_in_sec = 2048 - byte_in_sec
            to_read = min(remaining_in_sec, count - len(result))
            f.seek((no0_lba + sec_in_file) * 2352 + 24 + byte_in_sec)
            result += f.read(to_read)
            sec_in_file += 1
            byte_in_sec = 0
        return result[:count]
    
    # Read clutBanks array (we know entries 0-15)
    cb_array = read_overlay_bytes(0x38AB4, 128)
    cb_ptrs = struct.unpack_from('<32I', cb_array)
    
    # Read and analyze each non-null clutBank entry
    for i in range(16):
        ptr = cb_ptrs[i]
        if ptr == 0:
            print(f'clutBank[{i:2d}] = NULL')
            continue
        
        off = ptr - base_addr
        # Determine size by looking at next entry
        next_off = None
        for j in range(i+1, 17):
            if j < 16 and cb_ptrs[j] != 0:
                next_off = cb_ptrs[j] - base_addr
                break
        size = (next_off - off) if next_off else 128
        
        data = read_overlay_bytes(off, min(size, 256))
        
        # Check if this looks like CLUT data (array of 16-bit PS1 color values)
        # or if it's a sub-structure with pointers
        words32 = struct.unpack_from(f'<{min(len(data)//4, 8)}I', data)
        words16 = struct.unpack_from(f'<{min(len(data)//2, 48)}H', data)
        
        # Detect format: if first few words are in 0x80xxxxxx range, it's pointers
        is_ptrs = sum(1 for w in words32[:4] if 0x80180000 <= w < 0x801E0000) >= 2
        
        if is_ptrs:
            print(f'clutBank[{i:2d}] @ 0x{off:X} ({size} bytes) - POINTER TABLE:')
            for j in range(min(len(words32), 8)):
                v = words32[j]
                foff = v - base_addr if 0x80180000 <= v < 0x801E0000 else None
                extra = f' (file 0x{foff:X})' if foff is not None else ''
                print(f'    [{j}] 0x{v:08X}{extra}')
            # Follow first pointer that's valid
            first_valid = None
            for w in words32[:4]:
                if 0x80180000 <= w < 0x801E0000:
                    first_valid = w - base_addr
                    break
            if first_valid:
                sub_data = read_overlay_bytes(first_valid, 64)
                sub16 = struct.unpack_from('<32H', sub_data)
                non_zero = sum(1 for v in sub16[:16] if v != 0)
                print(f'    -> Data at first ptr: {" ".join(f"{v:04X}" for v in sub16[:16])} [{non_zero} nz]')
        else:
            non_zero = sum(1 for v in words16[:16] if v != 0)
            print(f'clutBank[{i:2d}] @ 0x{off:X} ({size} bytes) - RAW DATA:')
            # Print as palette rows
            for row in range(min(size // 32, 4)):
                start = row * 16
                vals = words16[start:start+16]
                nz = sum(1 for v in vals if v != 0)
                print(f'    Row {row}: {" ".join(f"{v:04X}" for v in vals)} [{nz} nz]')
    
    print('\n=== Checking tile CLUT data locations ===')
    # In SOTN, the stage tile CLUTs are loaded via LoadFileSimToMem SIM_1
    # which copies from SIM_PTR (0x80280000). The SIM data for each room 
    # might be at a different location. Let me check overlay data structures.
    
    # Look at roomsX and roomsY to understand room layout
    rooms_x_off = 0x40614
    rooms_y_off = 0x3876C
    
    rx_data = read_overlay_bytes(rooms_x_off, 64)
    ry_data = read_overlay_bytes(rooms_y_off, 64)
    rx = struct.unpack_from('<16I', rx_data)
    ry = struct.unpack_from('<16I', ry_data)
    
    print(f'\nroomsX (from 0x{rooms_x_off:X}):')
    for i in range(8):
        print(f'  [{i}] 0x{rx[i]:08X}')
    
    print(f'\nroomsY (from 0x{rooms_y_off:X}):')
    for i in range(8):
        print(f'  [{i}] 0x{ry[i]:08X}')
