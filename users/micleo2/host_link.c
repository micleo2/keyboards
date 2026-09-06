// Copyright 2026 micleo2
// SPDX-License-Identifier: GPL-2.0-or-later

// Raw HID link to the desktop shell (quickshell/retro/services/Qmk.qml via
// services/qmk/qmk-bridge.py). One file for every board: symlinked into
// each keymap and built with `SRC += host_link.c` (plus `RAW_ENABLE = yes`
// on a board without VIA).
//
// The board pushes a STATE packet whenever anything the shell shows has
// changed (layers, RGB config, caps word) and a KEY packet for every key
// press and release, but only while a host is listening: pushing into a
// port nobody reads can cost a 100 ms USB timeout per packet. HELLO opens
// the link and the bridge repeats it every couple of seconds as a
// keep-alive; five seconds without one and the link goes quiet again.
//
// RGB is whichever of RGB matrix or rgblight the board has. The host
// drives it through the _noeeprom setters, and the result is committed to
// EEPROM a moment after the last change, so a slider drag is one write.
//
// On a VIA/Vial board VIA owns raw_hid_receive and routes unknown command
// ids to the keyboard; this file hooks in as raw_hid_receive_user (the
// Svalboard's svalboard.c calls it first) and VIA echoes the command
// packet back afterwards, which the bridge ignores. The command ids sit in
// 0x40-0x6F, clear of VIA (0x01-0x1F), the Svalboard (0xEE) and Vial (0xFE).
//
// Every packet is 32 bytes (RAW_EPSIZE), first byte the command or event.
//
//   host -> board
//     0x41 HELLO                 start pushing; replies STATE
//     0x42 STATE                 reply STATE
//     0x50 RGB_VAL   v           brightness 0..max
//     0x51 RGB_TOGGLE
//     0x52 RGB_ENABLE on
//     0x53 RGB_MODE_STEP dir     1 next, 0xff previous
//     0x54 RGB_MODE  mode
//     0x55 RGB_HSV   h s v
//     0x60 LAYER_TOGGLE layer
//     0x61 LAYER_CLEAR           back to the default layer
//     0x6f BYE                   stop pushing
//
//   board -> host
//     0x80 STATE
//       [1]     protocol version (2)
//       [2..5]  layer_state, little endian
//       [6..9]  default_layer_state, little endian
//       [10]    highest active layer
//       [11]    layer count
//       [12]    rgb enabled
//       [13]    rgb mode
//       [14]    hue   [15] sat   [16] val
//       [17]    maximum brightness
//       [18]    rgb mode count
//       [19]    caps word active
//       [20]    detected host OS (os_variant_t)
//     0x81 KEY
//       [1] row  [2] col  [3] pressed  [4..5] keycode, little endian

#include QMK_KEYBOARD_H
#include "raw_hid.h"
#include "keymap_introspection.h"
#include "host_link.h"

#ifdef OS_DETECTION_ENABLE
#    include "os_detection.h"
#endif

enum host_link_command {
    CMD_HELLO         = 0x41,
    CMD_STATE         = 0x42,
    CMD_RGB_VAL       = 0x50,
    CMD_RGB_TOGGLE    = 0x51,
    CMD_RGB_ENABLE    = 0x52,
    CMD_RGB_MODE_STEP = 0x53,
    CMD_RGB_MODE      = 0x54,
    CMD_RGB_HSV       = 0x55,
    CMD_LAYER_TOGGLE  = 0x60,
    CMD_LAYER_CLEAR   = 0x61,
    CMD_BYE           = 0x6f,
};

enum host_link_event {
    EV_STATE = 0x80,
    EV_KEY   = 0x81,
};

#define HOST_LINK_VERSION 2
// RAW_EPSIZE, which the keymap cannot see.
#define HOST_LINK_PACKET 32
// How long the link stays open after the last HELLO.
#define HOST_LINK_KEEPALIVE_MS 5000
// How long after the host's last RGB change the result is written to EEPROM.
#define HOST_LINK_EEPROM_DELAY_MS 1500

// ---------------------------------------------------------------------------
// The RGB backend: RGB matrix, rgblight, or nothing.

#if defined(RGB_MATRIX_ENABLE)
#    define HOST_LINK_RGB 1
static uint8_t rgb_on(void) {
    return rgb_matrix_is_enabled();
}
static uint8_t rgb_mode(void) {
    return rgb_matrix_get_mode();
}
static hsv_t rgb_hsv(void) {
    return rgb_matrix_get_hsv();
}
static uint8_t rgb_max(void) {
    return RGB_MATRIX_MAXIMUM_BRIGHTNESS;
}
static uint8_t rgb_mode_count(void) {
    return RGB_MATRIX_EFFECT_MAX - 1;
}
static void rgb_set_hsv(uint8_t h, uint8_t s, uint8_t v) {
    rgb_matrix_sethsv_noeeprom(h, s, v);
}
static void rgb_toggle(void) {
    rgb_matrix_toggle_noeeprom();
}
static void rgb_enable(bool on) {
    if (on)
        rgb_matrix_enable_noeeprom();
    else
        rgb_matrix_disable_noeeprom();
}
static void rgb_step(bool forward) {
    if (forward)
        rgb_matrix_step_noeeprom();
    else
        rgb_matrix_step_reverse_noeeprom();
}
static void rgb_set_mode(uint8_t mode) {
    if (mode >= 1 && mode < RGB_MATRIX_EFFECT_MAX) rgb_matrix_mode_noeeprom(mode);
}
static void rgb_flush(void) {
    eeconfig_force_flush_rgb_matrix();
}
#elif defined(RGBLIGHT_ENABLE)
#    define HOST_LINK_RGB 1
static uint8_t rgb_on(void) {
    return rgblight_is_enabled();
}
static uint8_t rgb_mode(void) {
    return rgblight_get_mode();
}
static hsv_t rgb_hsv(void) {
    return rgblight_get_hsv();
}
static uint8_t rgb_max(void) {
    return RGBLIGHT_LIMIT_VAL;
}
static uint8_t rgb_mode_count(void) {
    return RGBLIGHT_MODES;
}
static void rgb_set_hsv(uint8_t h, uint8_t s, uint8_t v) {
    rgblight_sethsv_noeeprom(h, s, v);
}
static void rgb_toggle(void) {
    rgblight_toggle_noeeprom();
}
static void rgb_enable(bool on) {
    if (on)
        rgblight_enable_noeeprom();
    else
        rgblight_disable_noeeprom();
}
static void rgb_step(bool forward) {
    if (forward)
        rgblight_step_noeeprom();
    else
        rgblight_step_reverse_noeeprom();
}
static void rgb_set_mode(uint8_t mode) {
    if (mode >= 1 && mode <= RGBLIGHT_MODES) rgblight_mode_noeeprom(mode);
}
static void rgb_flush(void) {
    eeconfig_update_rgblight_current();
}
#else
#    define HOST_LINK_RGB 0
#endif

// ---------------------------------------------------------------------------

static bool     connected     = false;
static uint32_t last_hello    = 0;
static bool     rgb_dirty     = false;
static uint32_t rgb_dirty_at  = 0;
static bool     state_pending = false;

// What the last STATE said, to notice a change from the housekeeping loop.
typedef struct {
    layer_state_t layers;
    layer_state_t default_layers;
    uint8_t       rgb_enable;
    uint8_t       rgb_mode;
    uint8_t       h, s, v;
    bool          caps_word;
} snapshot_t;

static snapshot_t last;

static bool link_is_master(void) {
#ifdef SPLIT_KEYBOARD
    return is_keyboard_master();
#else
    return true;
#endif
}

static void write_u32(uint8_t *at, uint32_t value) {
    at[0] = value & 0xff;
    at[1] = (value >> 8) & 0xff;
    at[2] = (value >> 16) & 0xff;
    at[3] = (value >> 24) & 0xff;
}

static snapshot_t take_snapshot(void) {
    snapshot_t s = {
        .layers         = layer_state,
        .default_layers = default_layer_state,
    };
#if HOST_LINK_RGB
    hsv_t hsv    = rgb_hsv();
    s.rgb_enable = rgb_on();
    s.rgb_mode   = rgb_mode();
    s.h          = hsv.h;
    s.s          = hsv.s;
    s.v          = hsv.v;
#endif
#ifdef CAPS_WORD_ENABLE
    s.caps_word = is_caps_word_on();
#endif
    return s;
}

static bool snapshot_differs(const snapshot_t *a, const snapshot_t *b) {
    return a->layers != b->layers || a->default_layers != b->default_layers || a->rgb_enable != b->rgb_enable || a->rgb_mode != b->rgb_mode || a->h != b->h || a->s != b->s || a->v != b->v || a->caps_word != b->caps_word;
}

static void push(uint8_t *packet) {
    if (!connected) return;
    raw_hid_send(packet, HOST_LINK_PACKET);
}

static void send_state(void) {
    uint8_t packet[HOST_LINK_PACKET] = {0};
    last                             = take_snapshot();

    packet[0] = EV_STATE;
    packet[1] = HOST_LINK_VERSION;
    write_u32(&packet[2], (uint32_t)last.layers);
    write_u32(&packet[6], (uint32_t)last.default_layers);
    packet[10] = get_highest_layer(last.layers | last.default_layers);
    packet[11] = keymap_layer_count();
#if HOST_LINK_RGB
    packet[12] = last.rgb_enable;
    packet[13] = last.rgb_mode;
    packet[14] = last.h;
    packet[15] = last.s;
    packet[16] = last.v;
    packet[17] = rgb_max();
    packet[18] = rgb_mode_count();
#endif
    packet[19] = last.caps_word;
#ifdef OS_DETECTION_ENABLE
    packet[20] = (uint8_t)detected_host_os();
#endif
    state_pending = false;
    push(packet);
}

#if HOST_LINK_RGB
static void rgb_touched(void) {
    rgb_dirty    = true;
    rgb_dirty_at = timer_read32();
}

static uint8_t clamp_val(uint8_t v) {
    return v > rgb_max() ? rgb_max() : v;
}
#endif

// True when the packet was one of ours.
static bool handle(uint8_t *data, uint8_t length) {
    if (length < 2) return false;
    switch (data[0]) {
        case CMD_HELLO:
            last_hello = timer_read32();
            if (!connected) state_pending = true;
            connected = true;
            return true;
        case CMD_STATE:
            state_pending = true;
            return true;
        case CMD_BYE:
            connected = false;
            return true;
#if HOST_LINK_RGB
        case CMD_RGB_VAL: {
            hsv_t hsv = rgb_hsv();
            rgb_set_hsv(hsv.h, hsv.s, clamp_val(data[1]));
            if (!rgb_on() && data[1] > 0) rgb_enable(true);
            rgb_touched();
            return true;
        }
        case CMD_RGB_TOGGLE:
            rgb_toggle();
            rgb_touched();
            return true;
        case CMD_RGB_ENABLE:
            rgb_enable(data[1] != 0);
            rgb_touched();
            return true;
        case CMD_RGB_MODE_STEP:
            rgb_step(data[1] != 0xff);
            rgb_touched();
            return true;
        case CMD_RGB_MODE:
            rgb_set_mode(data[1]);
            rgb_touched();
            return true;
        case CMD_RGB_HSV:
            if (length >= 4) {
                rgb_set_hsv(data[1], data[2], clamp_val(data[3]));
                rgb_touched();
            }
            return true;
#endif
        case CMD_LAYER_TOGGLE:
            if (data[1] < keymap_layer_count()) layer_invert(data[1]);
            return true;
        case CMD_LAYER_CLEAR:
            layer_clear();
            return true;
        default:
            return false;
    }
}

#ifdef VIA_ENABLE
// VIA routes command ids it does not know to the keyboard, and the
// Svalboard's raw_hid_receive_kb tries this first (see svalboard.c).
bool raw_hid_receive_user(uint8_t *data, uint8_t length) {
    return handle(data, length);
}
#else
void raw_hid_receive(uint8_t *data, uint8_t length) {
    handle(data, length);
}
#endif

// Every press and release, before the keymap gets to see it, so the shell
// can light the physical key whatever the keycode turns into.
bool pre_process_record_user(uint16_t keycode, keyrecord_t *record) {
#ifdef COMBO_ENABLE
    if (record->event.type == COMBO_EVENT) return true;
#endif
    if (connected) {
        uint8_t packet[HOST_LINK_PACKET] = {0};
        packet[0]                        = EV_KEY;
        packet[1]                        = record->event.key.row;
        packet[2]                        = record->event.key.col;
        packet[3]                        = record->event.pressed;
        packet[4]                        = keycode & 0xff;
        packet[5]                        = (keycode >> 8) & 0xff;
        push(packet);
    }
    return true;
}

void housekeeping_task_user(void) {
    if (!link_is_master()) return;

#if HOST_LINK_RGB
    if (rgb_dirty && timer_elapsed32(rgb_dirty_at) > HOST_LINK_EEPROM_DELAY_MS) {
        rgb_dirty = false;
        rgb_flush();
    }
#endif

    if (connected && timer_elapsed32(last_hello) > HOST_LINK_KEEPALIVE_MS) connected = false;
    if (!connected) return;
    if (state_pending) {
        send_state();
        return;
    }
    snapshot_t now = take_snapshot();
    if (snapshot_differs(&now, &last)) send_state();
}

bool host_link_connected(void) {
    return connected;
}
