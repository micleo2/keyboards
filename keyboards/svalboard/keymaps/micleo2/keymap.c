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
        /*R1*/  KC_J,               KC_U,               QK_REPEAT_KEY,      KC_M,               KC_H,               XXXXXXX,
        /*R2*/  KC_K,               KC_I,               LSFT(KC_SCLN),      KC_COMM,            KC_Y,               XXXXXXX,
        /*R3*/  KC_L,               KC_O,               OSL(SYS_CTRL),      KC_DOT,             KC_N,               XXXXXXX,
        /*R4*/  KC_SCLN,            KC_P,               KC_BSLS,            KC_SLSH,            KC_RBRC,            XXXXXXX,

        /*L1*/  KC_F,               KC_R,               KC_G,               KC_V,               KC_QUOT,            XXXXXXX,
        /*L2*/  KC_D,               KC_E,               KC_T,               KC_C,               KC_GRV,             XXXXXXX,
        /*L3*/  KC_S,               KC_W,               KC_B,               KC_X,               KC_DEL,             XXXXXXX,
        /*L4*/  KC_A,               KC_Q,               KC_LBRC,            KC_Z,               KC_TAB,             XXXXXXX,

        /*      Down                Pad                 Up                  Nail                Knuckle             DoubleDown */
        /*RT*/  KC_LSFT,            KC_SPC,             KC_ENT,             LCTL_T(KC_ESC),     KC_LALT,            XXXXXXX,
        /*LT*/  OSL(NAV_SYMBOLS),   KC_BTN1,            KC_BTN3,            LGUI_T(KC_BSPC),    KC_BTN2,            OSL(SYS_CTRL)
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
        /*R1*/  KC_F4,              KC_F7,              _______,            KC_F1,              _______,            _______,
        /*R2*/  KC_F5,              KC_F8,              _______,            KC_F2,              _______,            _______,
        /*R3*/  KC_F6,              KC_F9,              _______,            KC_F3,              _______,            _______,
        /*R4*/  KC_F10,             KC_F11,             _______,            KC_F12,             _______,            _______,

        /*L1*/  KC_VOLU,            KC_BRIU,            _______,            KC_MNXT,            _______,            _______,
        /*L2*/  KC_VOLD,            KC_BRID,            _______,            KC_MPRV,            _______,            _______,
        /*L3*/  KC_MUTE,            KC_PSCR,            _______,            KC_MPLY,            _______,            _______,
        /*L4*/  QK_BOOT,            SV_RIGHT_DPI_INC,   SV_LEFT_DPI_INC,    SV_RIGHT_DPI_DEC,   SV_LEFT_DPI_DEC,    _______,

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

// Per-layer LED colours (hue, sat, val), applied at every boot.  Brightness
// (val) is still controlled by the RGB_VAI/RGB_VAD keys at runtime.
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

// ---------------------------------------------------------------------------
// Tap dances: https://docs.qmk.fm/features/tap_dance
// Use them in the keymap as TD(name).

// Tap-hold tap dance ("advanced mod-tap": any keycode on tap, another on
// hold), the pattern from Example 5 of the tap dance docs.
typedef struct {
    uint16_t tap;
    uint16_t hold;
    uint16_t held;
} tap_dance_tap_hold_t;

#define ACTION_TAP_DANCE_TAP_HOLD(tap, hold)     { .fn = {NULL, tap_dance_tap_hold_finished, tap_dance_tap_hold_reset}, .user_data = (void *)&((tap_dance_tap_hold_t){tap, hold, 0}), }

static keypos_t td_last_pos;   // where the tap dance key is, for the Repeat key

// register/unregister that also works for the Repeat key, which is not a
// basic keycode and has to go through QMK's repeat key API.
static void td_key(uint16_t keycode, bool down) {
    if (keycode == QK_REPEAT_KEY) {
        keyevent_t event = MAKE_KEYEVENT(td_last_pos.row, td_last_pos.col, down);
        repeat_key_invoke(&event);
    } else if (down) {
        register_code16(keycode);
    } else {
        unregister_code16(keycode);
    }
}

void tap_dance_tap_hold_finished(tap_dance_state_t *state, void *user_data) {
    tap_dance_tap_hold_t *tap_hold = (tap_dance_tap_hold_t *)user_data;
    if (state->pressed) {
        if (state->count == 1
#ifndef PERMISSIVE_HOLD
            && !state->interrupted
#endif
        ) {
            td_key(tap_hold->hold, true);
            tap_hold->held = tap_hold->hold;
        } else {
            td_key(tap_hold->tap, true);
            tap_hold->held = tap_hold->tap;
        }
    }
}

void tap_dance_tap_hold_reset(tap_dance_state_t *state, void *user_data) {
    tap_dance_tap_hold_t *tap_hold = (tap_dance_tap_hold_t *)user_data;
    if (tap_hold->held) {
        td_key(tap_hold->held, false);
        tap_hold->held = 0;
    }
}

// Tap Dance declarations
enum {
    TD_REPEAT_KEY_LCTL,   // Keybard TD(0): tap QK_REPEAT_KEY, hold KC_LCTL, double-tap XXXXXXX, tap+hold XXXXXXX
};

// Tap Dance definitions
tap_dance_action_t tap_dance_actions[] = {
    [TD_REPEAT_KEY_LCTL] = ACTION_TAP_DANCE_TAP_HOLD(QK_REPEAT_KEY, KC_LCTL),
};

layer_state_t default_layer_state_set_user(layer_state_t state) {
    sval_set_active_layer(0, false);
    return state;
}

layer_state_t layer_state_set_user(layer_state_t state) {
    sval_set_active_layer(get_highest_layer(state), false);
    return state;
}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    // Tap-hold tap dances: send the tap keycode on release when the key was
    // tapped and released before the dance finished (Example 5 in the docs).
    tap_dance_action_t *action;
    switch (keycode) {
        case TD(TD_REPEAT_KEY_LCTL):
            td_last_pos = record->event.key;
            action = &tap_dance_actions[QK_TAP_DANCE_GET_INDEX(keycode)];
            if (!record->event.pressed && action->state.count && !action->state.finished) {
                tap_dance_tap_hold_t *tap_hold = (tap_dance_tap_hold_t *)action->user_data;
                td_key(tap_hold->tap, true);
                td_key(tap_hold->tap, false);
            }
            break;
    }

    // Custom keycodes go here.  Define your own starting from SV_SAFE_RANGE,
    // not SAFE_RANGE, so they don't collide with the Svalboard's.
    return true;
}

void keyboard_post_init_user(void) {
    memcpy(global_saved_values.layer_colors, my_layer_colors, sizeof(my_layer_colors));

    // Uncomment to debug the matrix over the QMK console (qmk console).
    // debug_enable = true;
    // debug_matrix = true;
}

