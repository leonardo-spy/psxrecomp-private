import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    def read_dir(lba, size, prefix=''):
        buf = b''
        sectors_needed = (size + 2047) // 2048
        for s in range(sectors_needed):
            f.seek((lba + s) * 2352 + 24)
            buf += f.read(2048)
        data = buf[:size]
        pos = 0
        entries = []
        while pos < len(data):
            rec_len = data[pos]
            if rec_len == 0:
                pos = ((pos // 2048) + 1) * 2048
                if pos >= len(data):
                    break
                continue
            file_lba = struct.unpack_from('<I', data, pos + 2)[0]
            file_size = struct.unpack_from('<I', data, pos + 10)[0]
            flags = data[pos + 25]
            name_len = data[pos + 32]
            name = data[pos + 33:pos + 33 + name_len].decode('ascii', errors='replace')
            if name not in ('\x00', '\x01'):
                is_dir = bool(flags & 0x02)
                if ';' in name:
                    name = name.split(';')[0]
                full = prefix + name
                entries.append((full, file_lba, file_size, is_dir))
            pos += rec_len
        return entries

    # Stages of interest - Prologue (NO3), and some others
    stage_dirs = {
        'ST/NO3': 0x008296,  # Prologue
        'ST/NO0': 0x007E5C,  # Entrance (overlay 0)
        'ST/SEL': 0x0074B5,  # Select screen
    }
    
    for stage_name, stage_lba in stage_dirs.items():
        print(f'\n=== {stage_name} (LBA=0x{stage_lba:06X}) ===')
        entries = read_dir(stage_lba, 2048, prefix=stage_name + '/')
        for name, lba, size, is_dir in sorted(entries):
            secs = size // 2048
            tag = 'DIR' if is_dir else '   '
            print(f'  {tag} {name:35s} LBA=0x{lba:06X} size={size:>10d} secs={secs:>4d}')
    
    # Also check NO0's clut/sec3 matching with our overlay table
    # Our overlay 0: clut_sec=0x7E5D, sec3=0x7EDD
    print('\n=== Key LBA check ===')
    print(f'Overlay 0 clut_sec=0x7E5D, sec3=0x7EDD')
    print(f'ST/NO0 dir LBA=0x7E5C')
    print(f'clut_sec 0x7E5D = NO0 dir + 1 sector')
    
    # Check what file in NO0 starts at LBA 0x7E5D
    entries = read_dir(0x007E5C, 2048, prefix='ST/NO0/')
    for name, lba, size, is_dir in sorted(entries):
        secs = (size + 2047) // 2048
        end_lba = lba + secs - 1
        print(f'  {name:35s} LBA=0x{lba:06X}-0x{end_lba:06X} size={size:>10d} secs={secs:>4d}')
        if lba <= 0x7E5D <= end_lba:
            print(f'    *** clut_sec 0x7E5D is within this file! offset={(0x7E5D-lba)*2048}')
        if lba <= 0x7EDD <= end_lba:
            print(f'    *** sec3 0x7EDD is within this file! offset={(0x7EDD-lba)*2048}')
    
    # Check NO3 (Prologue) similarly
    # Our overlay 3: clut_sec=0x7849 (from plan context)
    print('\n=== NO3 files ===')
    entries = read_dir(0x008296, 2048, prefix='ST/NO3/')
    for name, lba, size, is_dir in sorted(entries):
        secs = (size + 2047) // 2048
        end_lba = lba + secs - 1
        print(f'  {name:35s} LBA=0x{lba:06X}-0x{end_lba:06X} size={size:>10d} secs={secs:>4d}')
