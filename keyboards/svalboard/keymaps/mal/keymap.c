// Svalboard keymap.  Generated from mouse_on_base.kbi (firmware v2025-11-01) by
// tools/kbi2keymap.py on 2026-09-06.  Edit freely; re-run the script only to
// re-import a fresh Keybard export (it overwrites this file).
//
// Finger clusters are indexed from the index finger outwards: R1 is right
// index, R4 is right pinky, L1 is left index, and so on.  Thumb clusters are
// RT (right thumb) and LT (left thumb).
//
// Build:  make left  /  make right      (from the repo root)
// Flash:  double-tap reset, then copy the .uf2 onto the RPI-RP2 drive, or
//         run  make flash-left / make flash-right  with the half in bootloader.

#include QMK_KEYBOARD_H
#include <string.h>
#include "keymap_support.h"   // SV_* keycodes, MH_AUTO_BUTTONS_LAYER

enum layer {
    BASE = 0,
    NAV_SYMBOLS = 1,
    SYS_CTRL = 2,
    BOARD_CONFIG = MH_AUTO_BUTTONS_LAYER - 1,
    MOUSE = MH_AUTO_BUTTONS_LAYER,
};

// A layer where every key falls through to the layer below.
#define LAYER_TRNS LAYOUT( \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______, \
    _______, _______, _______, _______, _______, _______)

const uint16_t PROGMEM keymaps[DYNAMIC_KEYMAP_LAYER_COUNT][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE] = LAYOUT(
        /*      Center              North               East                South               West                DoubleSouth */
        /*R1*/  KC_J,               KC_U,               KC_QUOT,            KC_M,               KC_H,               XXXXXXX,
        /*R2*/  KC_K,               KC_I,               LSFT(KC_SCLN),      KC_COMM,            KC_Y,               XXXXXXX,
        /*R3*/  KC_L,               KC_O,               MO(SYS_CTRL),       KC_DOT,             KC_N,               XXXXXXX,
        /*R4*/  KC_SCLN,            KC_P,               KC_BSLS,            KC_SLSH,            KC_RBRC,            XXXXXXX,

        /*L1*/  KC_F,               KC_R,               KC_G,               KC_V,               LSFT(KC_QUOT),      XXXXXXX,
        /*L2*/  KC_D,               KC_E,               KC_T,               KC_C,               KC_GRV,             XXXXXXX,
        /*L3*/  KC_S,               KC_W,               KC_B,               KC_X,               KC_DEL,             XXXXXXX,
        /*L4*/  KC_A,               KC_Q,               KC_LBRC,            KC_Z,               KC_TAB,             XXXXXXX,

        /*      Down                Pad                 Up                  Nail                Knuckle             DoubleDown */
        /*RT*/  KC_LSFT,            KC_SPC,             KC_ENT,             LCTL_T(KC_ESC),     KC_LALT,            XXXXXXX,
        /*LT*/  OSL(NAV_SYMBOLS),   KC_BTN1,            KC_BTN3,            LGUI_T(KC_BSPC),    KC_BTN2,            XXXXXXX
    ),

    [NAV_SYMBOLS] = LAYOUT(
        /*      Center              North               East                South               West                DoubleSouth */
        /*R1*/  KC_7,               LSFT(KC_7),         LSFT(KC_6),         KC_LEFT,            KC_6,               XXXXXXX,
        /*R2*/  KC_8,               LSFT(KC_8),         XXXXXXX,            KC_DOWN,            LSFT(KC_MINS),      XXXXXXX,
        /*R3*/  KC_9,               LSFT(KC_9),         XXXXXXX,            KC_UP,              KC_INS,             XXXXXXX,
        /*R4*/  KC_0,               LSFT(KC_0),         XXXXXXX,            KC_RIGHT,           LSFT(KC_GRV),       XXXXXXX,

        /*L1*/  KC_4,               LSFT(KC_4),         KC_5,               KC_END,             LSFT(KC_5),         XXXXXXX,
        /*L2*/  KC_3,               LSFT(KC_3),         KC_MINS,            KC_PGDN,            LSFT(KC_EQL),       XXXXXXX,
        /*L3*/  KC_2,               LSFT(KC_2),         KC_DOT,             KC_PGUP,            _______,            XXXXXXX,
        /*L4*/  KC_1,               LSFT(KC_1),         KC_EQL,             KC_HOME,            _______,            XXXXXXX,

        /*      Down                Pad                 Up                  Nail                Knuckle             DoubleDown */
        /*RT*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*LT*/  _______,            _______,            _______,            _______,            _______,            _______
    ),

    [SYS_CTRL] = LAYOUT(
        /*      Center              North               East                South               West                DoubleSouth */
        /*R1*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*R2*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*R3*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*R4*/  _______,            _______,            _______,            _______,            _______,            _______,

        /*L1*/  KC_VOLU,            KC_BRIU,            _______,            KC_MNXT,            _______,            _______,
        /*L2*/  KC_VOLD,            KC_BRID,            _______,            KC_MPRV,            _______,            _______,
        /*L3*/  KC_MUTE,            KC_PSCR,            _______,            KC_MPLY,            _______,            _______,
        /*L4*/  _______,            _______,            _______,            _______,            _______,            _______,

        /*      Down                Pad                 Up                  Nail                Knuckle             DoubleDown */
        /*RT*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*LT*/  _______,            _______,            _______,            _______,            _______,            _______
    ),

    [BOARD_CONFIG] = LAYOUT(
        /*      Center                   North                    East                     South                    West                     DoubleSouth */
        /*R1*/  _______,                 _______,                 _______,                 _______,                 _______,                 _______,
        /*R2*/  _______,                 RGB_VAI,                 _______,                 RGB_VAD,                 _______,                 _______,
        /*R3*/  _______,                 _______,                 _______,                 _______,                 _______,                 _______,
        /*R4*/  _______,                 _______,                 _______,                 _______,                 _______,                 _______,

        /*L1*/  SV_OUTPUT_STATUS,        _______,                 _______,                 _______,                 _______,                 _______,
        /*L2*/  SV_RIGHT_SCROLL_TOGGLE,  SV_RIGHT_DPI_INC,        _______,                 SV_RIGHT_DPI_DEC,        _______,                 _______,
        /*L3*/  SV_LEFT_SCROLL_TOGGLE,   SV_LEFT_DPI_INC,         _______,                 SV_LEFT_DPI_DEC,         _______,                 _______,
        /*L4*/  SV_MH_CHANGE_TIMEOUTS,   SV_AXIS_SCROLL_LOCK,     _______,                 _______,                 _______,                 _______,

        /*      Down                     Pad                      Up                       Nail                     Knuckle                  DoubleDown */
        /*RT*/  _______,                 _______,                 _______,                 _______,                 _______,                 _______,
        /*LT*/  _______,                 _______,                 _______,                 _______,                 _______,                 _______
    ),

    [MOUSE] = LAYOUT(
        /*      Center              North               East                South               West                DoubleSouth */
        /*R1*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*R2*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*R3*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*R4*/  _______,            _______,            _______,            _______,            _______,            _______,

        /*L1*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*L2*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*L3*/  _______,            _______,            _______,            _______,            SV_SNIPER_3,        _______,
        /*L4*/  _______,            _______,            _______,            _______,            _______,            _______,

        /*      Down                Pad                 Up                  Nail                Knuckle             DoubleDown */
        /*RT*/  _______,            _______,            _______,            _______,            _______,            _______,
        /*LT*/  _______,            _______,            _______,            _______,            _______,            _______
    ),

    [3 ... 13] = LAYER_TRNS,
};

// Per-layer LED colours (hue, sat, val), applied at every boot so the C file
// stays the single source of truth.  Brightness (val) is still controlled by
// the RGB_VAI/RGB_VAD keys at runtime.
static const struct layer_hsv my_layer_colors[DYNAMIC_KEYMAP_LAYER_COUNT] = {
    [ 0] = { 85, 255, 255},
    [ 1] = { 21, 255, 255},
    [ 2] = {149, 255, 255},
    [ 3] = { 11, 176, 255},
    [ 4] = { 43, 255, 255},
    [ 5] = {128, 255, 128},
    [ 6] = {  0, 255, 255},
    [ 7] = {  0, 255, 255},
    [ 8] = {234, 255, 255},
    [ 9] = {191, 255, 128},
    [10] = { 11, 176, 255},
    [11] = {106, 255, 255},
    [12] = {128, 255, 128},
    [13] = {128, 255, 255},
    [14] = { 43, 255, 255},
    [15] = {213, 255, 255},
};

layer_state_t default_layer_state_set_user(layer_state_t state) {
    sval_set_active_layer(0, false);
    return state;
}

layer_state_t layer_state_set_user(layer_state_t state) {
    sval_set_active_layer(get_highest_layer(state), false);
    return state;
}

void keyboard_post_init_user(void) {
    memcpy(global_saved_values.layer_colors, my_layer_colors, sizeof(my_layer_colors));

    // Uncomment to debug the matrix over the QMK console (qmk console).
    // debug_enable = true;
    // debug_matrix = true;
}

