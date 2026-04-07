#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>

enum {
    PSX_KROM_CELL_W = 16,
    PSX_KROM_CELL_H = 16,
    PSX_KROM_RAW_H = 15,
    PSX_KROM_RAW_SIZE = PSX_KROM_RAW_H * 2,
    PSX_KROM_CACHE_CAP = 512,
};

typedef struct {
    uint16_t ch;
    uint8_t bitmap[PSX_KROM_RAW_SIZE];
    int used;
} PSXKromGlyphCache;

static struct {
    int initialized;
    HDC dc;
    HBITMAP dib;
    HGDIOBJ old_bitmap;
    HFONT font;
    HGDIOBJ old_font;
    uint32_t* pixels;
    PSXKromGlyphCache cache[PSX_KROM_CACHE_CAP];
    uint32_t next_slot;
} g_psx_krom;

static void psx_krom_init(void) {
    BITMAPINFO bmi;

    if (g_psx_krom.initialized) {
        return;
    }

    memset(&bmi, 0, sizeof(bmi));
    bmi.bmiHeader.biSize = sizeof(bmi.bmiHeader);
    bmi.bmiHeader.biWidth = PSX_KROM_CELL_W;
    bmi.bmiHeader.biHeight = -(LONG)PSX_KROM_CELL_H;
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    bmi.bmiHeader.biCompression = BI_RGB;

    g_psx_krom.dc = CreateCompatibleDC(NULL);
    if (!g_psx_krom.dc) {
        return;
    }

    g_psx_krom.dib = CreateDIBSection(g_psx_krom.dc, &bmi, DIB_RGB_COLORS,
                                      (void**)&g_psx_krom.pixels, NULL, 0);
    if (!g_psx_krom.dib || !g_psx_krom.pixels) {
        return;
    }

    g_psx_krom.old_bitmap = SelectObject(g_psx_krom.dc, g_psx_krom.dib);
    g_psx_krom.font = CreateFontW(
        -16, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
        SHIFTJIS_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
        NONANTIALIASED_QUALITY, FIXED_PITCH | FF_MODERN, L"MS Gothic");
    if (!g_psx_krom.font) {
        g_psx_krom.font = (HFONT)GetStockObject(SYSTEM_FIXED_FONT);
    }
    g_psx_krom.old_font = SelectObject(g_psx_krom.dc, g_psx_krom.font);
    SetTextColor(g_psx_krom.dc, RGB(255, 255, 255));
    SetBkColor(g_psx_krom.dc, RGB(0, 0, 0));
    SetBkMode(g_psx_krom.dc, OPAQUE);
    SetTextAlign(g_psx_krom.dc, TA_LEFT | TA_TOP | TA_NOUPDATECP);
    g_psx_krom.initialized = 1;
}

static int psx_krom_shiftjis_to_utf16(uint16_t ch, wchar_t* out_ch) {
    char sjis[2];
    int count;

    sjis[0] = (char)(ch >> 8);
    sjis[1] = (char)(ch & 0xFFu);
    count = MultiByteToWideChar(932, MB_ERR_INVALID_CHARS, sjis, 2, out_ch, 1);
    if (count == 1) {
        return 1;
    }
    return 0;
}

static int psx_krom_render_glyph(uint16_t ch, uint8_t out_bitmap[PSX_KROM_RAW_SIZE]) {
    wchar_t glyph = 0;

    psx_krom_init();
    if (!g_psx_krom.initialized) {
        return 0;
    }
    if (!psx_krom_shiftjis_to_utf16(ch, &glyph)) {
        return 0;
    }

    memset(g_psx_krom.pixels, 0, PSX_KROM_CELL_W * PSX_KROM_CELL_H * sizeof(uint32_t));
    TextOutW(g_psx_krom.dc, 0, -1, &glyph, 1);

    for (int y = 0; y < PSX_KROM_RAW_H; ++y) {
        uint8_t row_hi = 0;
        uint8_t row_lo = 0;
        for (int x = 0; x < PSX_KROM_CELL_W; ++x) {
            uint32_t pixel = g_psx_krom.pixels[y * PSX_KROM_CELL_W + x];
            if ((pixel & 0x00FFFFFFu) == 0u) {
                continue;
            }
            if (x < 8) {
                row_hi |= (uint8_t)(1u << x);
            } else {
                row_lo |= (uint8_t)(1u << (x - 8));
            }
        }
        out_bitmap[y * 2 + 0] = row_hi;
        out_bitmap[y * 2 + 1] = row_lo;
    }

    return 1;
}

const uint8_t* psx_krom2raw_lookup(uint16_t ch) {
    uint32_t slot;

    for (slot = 0; slot < PSX_KROM_CACHE_CAP; ++slot) {
        if (g_psx_krom.cache[slot].used && g_psx_krom.cache[slot].ch == ch) {
            return g_psx_krom.cache[slot].bitmap;
        }
    }

    slot = g_psx_krom.next_slot++ % PSX_KROM_CACHE_CAP;
    if (!psx_krom_render_glyph(ch, g_psx_krom.cache[slot].bitmap)) {
        return NULL;
    }

    g_psx_krom.cache[slot].ch = ch;
    g_psx_krom.cache[slot].used = 1;
    return g_psx_krom.cache[slot].bitmap;
}

int psx_font_render_4bpp(uint16_t ch, uint16_t kind, uint8_t out_bitmap[96]) {
    wchar_t glyph = 0;
    int min_x = PSX_KROM_CELL_W;
    int max_x = -1;
    int origin_x = 0;
    (void)kind;

    psx_krom_init();
    if (!g_psx_krom.initialized) {
        return 0;
    }
    if (!psx_krom_shiftjis_to_utf16(ch, &glyph)) {
        return 0;
    }

    memset(out_bitmap, 0, 96);
    memset(g_psx_krom.pixels, 0, PSX_KROM_CELL_W * PSX_KROM_CELL_H * sizeof(uint32_t));
    TextOutW(g_psx_krom.dc, 0, -1, &glyph, 1);

    for (int y = 0; y < PSX_KROM_CELL_H; ++y) {
        for (int x = 0; x < PSX_KROM_CELL_W; ++x) {
            uint32_t pixel = g_psx_krom.pixels[y * PSX_KROM_CELL_W + x];
            if ((pixel & 0x00FFFFFFu) == 0u) {
                continue;
            }
            if (x < min_x) min_x = x;
            if (x > max_x) max_x = x;
        }
    }

    if (max_x < min_x) {
        return 0;
    }
    origin_x = min_x;
    if (origin_x > PSX_KROM_CELL_W - 12) {
        origin_x = PSX_KROM_CELL_W - 12;
    }
    if (origin_x < 0) {
        origin_x = 0;
    }

    for (int y = 0; y < PSX_KROM_CELL_H; ++y) {
        for (int x = 0; x < 12; x += 2) {
            int src_x0 = origin_x + x;
            int src_x1 = origin_x + x + 1;
            uint8_t px0 = 0;
            uint8_t px1 = 0;

            if (src_x0 < PSX_KROM_CELL_W) {
                uint32_t pixel0 = g_psx_krom.pixels[y * PSX_KROM_CELL_W + src_x0];
                if ((pixel0 & 0x00FFFFFFu) != 0u) {
                    px0 = 8;
                }
            }
            if (src_x1 < PSX_KROM_CELL_W) {
                uint32_t pixel1 = g_psx_krom.pixels[y * PSX_KROM_CELL_W + src_x1];
                if ((pixel1 & 0x00FFFFFFu) != 0u) {
                    px1 = 8;
                }
            }

            out_bitmap[y * 6 + (x / 2)] = (uint8_t)(px0 | (uint8_t)(px1 << 4));
        }
    }

    return 1;
}
