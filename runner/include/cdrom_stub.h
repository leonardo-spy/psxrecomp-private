#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Open a PS1 BIN/CUE image.  Pass path to the .cue file.
 * Returns 1 on success, 0 on failure. */
int psx_cdrom_init(const char* cue_path);

/* Read one 2048-byte user-data sector at the given LBA into buffer.
 * Returns 1 on success, 0 on failure. */
int psx_cdrom_read_sector(uint32_t lba, uint8_t* buffer);

/* Find a file in the ISO 9660 filesystem by name.
 * Returns 1 on success (populates start_lba and file_size), 0 if not found. */
int psx_cdrom_find_file(const char* name, uint32_t* start_lba, uint32_t* file_size);

#ifdef __cplusplus
}
#endif
