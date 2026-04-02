import struct

disc = 'CastlevaniaRecomp/isos/Castlevania - Symphony of the Night (USA) (Track 1).bin'
with open(disc, 'rb') as f:
    # Read ISO PVD (sector 16)
    f.seek(16 * 2352 + 24)
    pvd = f.read(2048)
    root_lba = struct.unpack_from('<I', pvd, 158)[0]
    root_len = struct.unpack_from('<I', pvd, 166)[0]
    print(f'Root dir at LBA {root_lba}, size {root_len}')

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

    all_entries = read_dir(root_lba, root_len)
    for name, lba, size, is_dir in sorted(all_entries):
        tag = 'DIR' if is_dir else '   '
        print(f'  {tag} {name:30s} LBA=0x{lba:06X} size={size:>10d} secs={size//2048}')
        if is_dir:
            sub = read_dir(lba, size, prefix=name + '/')
            for sn, sl, ss, sd in sorted(sub):
                stag = 'DIR' if sd else '   '
                print(f'       {stag} {sn:30s} LBA=0x{sl:06X} size={ss:>10d} secs={ss//2048}')
