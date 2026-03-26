#include <stdint.h>

extern "C" {

const char *game_get_name(void) {
    return GAME_WINDOW_TITLE;
}

uint32_t game_get_display_entry(void) {
    return (uint32_t)GAME_DISPLAY_ENTRY;
}

uint32_t game_get_entry_addr(void) {
    return (uint32_t)GAME_ENTRY_ADDR;
}

const char *game_get_exe_filename(void) {
    return GAME_EXE_FILENAME;
}

uint32_t game_get_expected_crc32(void) {
    return (uint32_t)GAME_EXPECTED_CRC32;
}

void game_on_init(void) {
}

void game_on_frame(uint32_t frame) {
    (void)frame;
}

int game_handle_arg(const char *key, const char *val) {
    (void)key;
    (void)val;
    return 0;
}

const char *game_arg_usage(void) {
    return "";
}

}
