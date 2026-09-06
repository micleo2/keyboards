#!/usr/bin/env python3
"""Convert a Keybard .kbi export into a QMK keymap.c for the Svalboard.

Usage:
    tools/kbi2keymap.py layouts-kbi/mouse_on_base.kbi > keyboards/svalboard/keymaps/mal/keymap.c

The generated file is meant to be edited by hand afterwards; re-run this only
if you want to re-import a fresh Keybard export (it overwrites everything).

Keycodes, layer colours and tap dances are converted.  Tap dances become
plain QMK tap_dance_actions[] entries (https://docs.qmk.fm/features/tap_dance):
tap/double-tap ones as ACTION_TAP_DANCE_DOUBLE, tap/hold ones as the docs'
tap-hold pattern.  The script aborts if the export contains macros, combos
or key overrides, since those would be silently lost otherwise.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROWS, COLS = 10, 6

# LAYOUT() argument order, taken from keyboards/svalboard/info.json.
# Finger clusters: centre, north, east, south, west, double-south.
FINGER_COLS = [2, 3, 1, 0, 4, 5]
FINGER_HDR = ["Center", "North", "East", "South", "West", "DoubleSouth"]
# Thumb clusters: down, pad, up, nail, knuckle, double-down.
THUMB_COLS = [2, 3, 4, 1, 0, 5]
THUMB_HDR = ["Down", "Pad", "Up", "Nail", "Knuckle", "DoubleDown"]
# (label, matrix row)
CLUSTERS = [("R1", 6), ("R2", 7), ("R3", 8), ("R4", 9),
            ("L1", 1), ("L2", 2), ("L3", 3), ("L4", 4)]
THUMBS = [("RT", 5), ("LT", 0)]

# Keybard emits some pre-QMK-0.19 names; map them to current short aliases.
RENAME = {
    "KC_TRNS": "_______", "KC_TRANSPARENT": "_______", "KC_NO": "XXXXXXX",
    "KC_BSPACE": "KC_BSPC", "KC_LBRACKET": "KC_LBRC", "KC_RBRACKET": "KC_RBRC",
    "KC_SCOLON": "KC_SCLN", "KC_LSHIFT": "KC_LSFT", "KC_RSHIFT": "KC_RSFT",
    "KC_PSCREEN": "KC_PSCR", "KC_PGDOWN": "KC_PGDN", "KC_BSLASH": "KC_BSLS",
    "KC_ESCAPE": "KC_ESC", "KC_DELETE": "KC_DEL", "KC_QUOTE": "KC_QUOT",
    "KC_GRAVE": "KC_GRV", "KC_COMMA": "KC_COMM", "KC_SLASH": "KC_SLSH",
    "KC_SPACE": "KC_SPC", "KC_ENTER": "KC_ENT", "KC_INSERT": "KC_INS",
    "KC_CAPSLOCK": "KC_CAPS", "KC_SCROLLLOCK": "KC_SCRL", "KC_NUMLOCK": "KC_NUM",
    "KC_MINUS": "KC_MINS", "KC_EQUAL": "KC_EQL", "KC_SEMICOLON": "KC_SCLN",
    "KC_APPLICATION": "KC_APP", "KC_LCTRL": "KC_LCTL", "KC_RCTRL": "KC_RCTL",
    "RESET": "QK_BOOT", "QK_BOOTLOADER": "QK_BOOT",
}
LAYER_FN = re.compile(r"\b(MO|TG|TO|TT|OSL|DF|PDF|LM|LT)\((\d+)")
USER_KC = re.compile(r"\bUSER(\d\d)\b")


def ident(name, fallback):
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()
    if not s:
        return fallback
    if s[0].isdigit():
        s = "L_" + s
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kbi", type=Path)
    ap.add_argument("--keymap-support", type=Path,
                    default=Path(__file__).resolve().parent.parent
                    / "firmware/keyboards/svalboard/keymaps/keymap_support.h",
                    help="header whose my_keycodes enum resolves Keybard's USERnn")
    args = ap.parse_args()

    kbi = json.loads(args.kbi.read_text())
    # USER00.. are the SV_* codes in the order of enum my_keycodes (QK_KB_0 upwards).
    enum_src = re.search(r"enum my_keycodes \{(.*?)\};", args.keymap_support.read_text(), re.S).group(1)
    custom = [m for m in re.findall(r"^\s*(SV_\w+)\s*(?:=\s*QK_KB_0)?\s*,", enum_src, re.M) if m != "SV_SAFE_RANGE"]

    assert kbi["rows"] == ROWS and kbi["cols"] == COLS, "unexpected matrix size"
    nlayers = kbi["layers"]

    # Refuse to drop things we don't convert.
    problems = []
    if any(m.get("actions") for m in kbi.get("macros", [])):
        problems.append("macros")
    if any(any(k not in ("KC_NO", 0, "") for k in c) for c in kbi.get("combos", [])):
        problems.append("combos")
    if any(str(o).find("KC_NO") < 0 for o in kbi.get("key_overrides", [])):
        problems.append("key overrides")
    if problems:
        sys.exit("export contains %s, which this script does not convert" % ", ".join(problems))

    names = kbi.get("cosmetic", {}).get("layer", {})
    used = [i for i, l in enumerate(kbi["keymap"])
            if set(l) - {"KC_NO", "KC_TRNS", "KC_TRANSPARENT"}]

    layer_name = {}
    for i in used:
        layer_name[i] = ident(names.get(str(i), ""), "LAYER%d" % i)
    if nlayers - 1 in used and str(nlayers - 1) not in names:
        layer_name[nlayers - 1] = "MOUSE"
    if nlayers - 2 in used and str(nlayers - 2) not in names:
        layer_name[nlayers - 2] = "BOARD_CONFIG"

    KC_TOKEN = re.compile(r"\bKC_[A-Z0-9_]+\b")

    def kc(code):
        code = RENAME.get(code, code)
        code = KC_TOKEN.sub(lambda m: RENAME.get(m.group(0), m.group(0)), code)
        code = USER_KC.sub(lambda m: custom[int(m.group(1))], code)
        code = LAYER_FN.sub(lambda m: "%s(%s" % (m.group(1), layer_name.get(int(m.group(2)), m.group(2))), code)
        return code
    _kc_plain = kc

    def row(flat, r, cols):
        return [td_ref(kc(flat[r * COLS + c])) for c in cols]

    def fmt_layer(flat):
        w = max(20, max(len(kc(c)) for c in flat) + 3)
        out = []
        out.append("        /*      " + "".join(h.ljust(w) for h in FINGER_HDR).rstrip() + " */")
        for label, r in CLUSTERS:
            cells = row(flat, r, FINGER_COLS)
            out.append("        /*%s*/  " % label + "".join((c + ",").ljust(w) for c in cells).rstrip())
            if label == "R4":
                out.append("")
        out.append("")
        out.append("        /*      " + "".join(h.ljust(w) for h in THUMB_HDR).rstrip() + " */")
        for label, r in THUMBS:
            cells = row(flat, r, THUMB_COLS)
            line = "        /*%s*/  " % label + "".join((c + ",").ljust(w) for c in cells).rstrip()
            out.append(line)
        out[-1] = out[-1].rstrip(",")
        return "\n".join(out)

    enum_lines = []
    for i in used:
        if i == nlayers - 1:
            val = "MH_AUTO_BUTTONS_LAYER"
        elif i == nlayers - 2:
            val = "MH_AUTO_BUTTONS_LAYER - 1"
        else:
            val = str(i)
        enum_lines.append("    %s = %s," % (layer_name[i], val))

    # Contiguous ranges of unused layers get a transparent LAYOUT so that
    # accidentally activating one doesn't kill every key.
    unused = [i for i in range(nlayers) if i not in used]
    ranges = []
    for i in unused:
        if ranges and ranges[-1][1] == i - 1:
            ranges[-1][1] = i
        else:
            ranges.append([i, i])

    tds = [t for t in kbi.get("tapdances", [])
           if any(t[k] != "KC_NO" for k in ("tap", "hold", "doubletap", "taphold"))]
    def short(code):
        return re.sub(r"^(KC|QK)_", "", code).replace("(", "_").replace(")", "")

    td_names, td_enum, td_actions, td_cases = {}, [], [], []
    for t in tds:
        tap, hold, dtap, thold = (kc(t[k]) for k in ("tap", "hold", "doubletap", "taphold"))
        note = "Keybard TD(%d): tap %s, hold %s, double-tap %s, tap+hold %s" % (t["tdid"], tap, hold, dtap, thold)
        if hold == "XXXXXXX" and thold == "XXXXXXX":
            name = "TD_%s_%s" % (short(tap), short(dtap if dtap != "XXXXXXX" else tap))
            action = "ACTION_TAP_DANCE_DOUBLE(%s, %s)" % (tap, dtap if dtap != "XXXXXXX" else tap)
        else:
            name = "TD_%s_%s" % (short(tap), short(hold if hold != "XXXXXXX" else thold))
            action = "ACTION_TAP_DANCE_TAP_HOLD(%s, %s)" % (tap, hold if hold != "XXXXXXX" else thold)
            td_cases.append("        case TD(%s):" % name)
            if dtap != "XXXXXXX" or (hold != "XXXXXXX" and thold != "XXXXXXX"):
                note += "  (double-tap/tap+hold not carried over; see the docs' Example 4)"
        td_names[t["tdid"]] = name
        td_enum.append("    %s,   // %s" % (name, note))
        td_actions.append("    [%s] = %s," % (name, action))
    # TD(n) in the keymap -> TD(name)
    def td_ref(code):
        return re.sub(r"\bTD\((\d+)\)", lambda m: "TD(%s)" % td_names.get(int(m.group(1)), m.group(1)), code)

    colors = kbi.get("layer_colors") or []
    color_lines = ["    [%2d] = {%3d, %3d, %3d}," % (i, c["hue"], c["sat"], c["val"])
                   for i, c in enumerate(colors)]

    layers_src = []
    for i in used:
        layers_src.append("    [%s] = LAYOUT(\n%s\n    )," % (layer_name[i], fmt_layer(kbi["keymap"][i])))
    for a, b in ranges:
        idx = "%d ... %d" % (a, b) if a != b else "%d" % a
        layers_src.append("    [%s] = LAYER_TRNS," % idx)

    print(TEMPLATE.format(
        src=args.kbi.name, today=date.today().isoformat(),
        firmware=kbi.get("sval_firmware", "?"),
        enum="\n".join(enum_lines),
        layers="\n\n".join(layers_src),
        colors="\n".join(color_lines),
        td_enum="\n".join(td_enum) if td_enum else "    // TD_EXAMPLE,",
        td_actions="\n".join(td_actions) if td_actions else "    // [TD_EXAMPLE] = ACTION_TAP_DANCE_DOUBLE(KC_ESC, KC_CAPS),",
        td_cases="\n".join(td_cases) if td_cases else "        // case TD(TD_EXAMPLE):",
    ))


TEMPLATE = '''\
// Svalboard keymap.  Generated from {src} (firmware {firmware}) by
// tools/kbi2keymap.py on {today}.  Edit freely; re-run the script only to
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

enum layer {{
{enum}
}};

// A layer where every key falls through to the layer below.
#define LAYER_TRNS LAYOUT( \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______, \\
    _______, _______, _______, _______, _______, _______)

const uint16_t PROGMEM keymaps[DYNAMIC_KEYMAP_LAYER_COUNT][MATRIX_ROWS][MATRIX_COLS] = {{
{layers}
}};

// Per-layer LED colours (hue, sat, val), applied at every boot.  Brightness
// (val) is still controlled by the RGB_VAI/RGB_VAD keys at runtime.
static const struct layer_hsv my_layer_colors[DYNAMIC_KEYMAP_LAYER_COUNT] = {{
{colors}
}};

// ---------------------------------------------------------------------------
// Tap dances: https://docs.qmk.fm/features/tap_dance
// Use them in the keymap as TD(name).

// Tap-hold tap dance ("advanced mod-tap": any keycode on tap, another on
// hold), the pattern from Example 5 of the tap dance docs.
typedef struct {{
    uint16_t tap;
    uint16_t hold;
    uint16_t held;
}} tap_dance_tap_hold_t;

#define ACTION_TAP_DANCE_TAP_HOLD(tap, hold) \
    {{ .fn = {{NULL, tap_dance_tap_hold_finished, tap_dance_tap_hold_reset}}, .user_data = (void *)&((tap_dance_tap_hold_t){{tap, hold, 0}}), }}

static keypos_t td_last_pos;   // where the tap dance key is, for the Repeat key

// register/unregister that also works for the Repeat key, which is not a
// basic keycode and has to go through QMK's repeat key API.
static void td_key(uint16_t keycode, bool down) {{
    if (keycode == QK_REPEAT_KEY) {{
        keyevent_t event = MAKE_KEYEVENT(td_last_pos.row, td_last_pos.col, down);
        repeat_key_invoke(&event);
    }} else if (down) {{
        register_code16(keycode);
    }} else {{
        unregister_code16(keycode);
    }}
}}

void tap_dance_tap_hold_finished(tap_dance_state_t *state, void *user_data) {{
    tap_dance_tap_hold_t *tap_hold = (tap_dance_tap_hold_t *)user_data;
    if (state->pressed) {{
        if (state->count == 1
#ifndef PERMISSIVE_HOLD
            && !state->interrupted
#endif
        ) {{
            td_key(tap_hold->hold, true);
            tap_hold->held = tap_hold->hold;
        }} else {{
            td_key(tap_hold->tap, true);
            tap_hold->held = tap_hold->tap;
        }}
    }}
}}

void tap_dance_tap_hold_reset(tap_dance_state_t *state, void *user_data) {{
    tap_dance_tap_hold_t *tap_hold = (tap_dance_tap_hold_t *)user_data;
    if (tap_hold->held) {{
        td_key(tap_hold->held, false);
        tap_hold->held = 0;
    }}
}}

// Tap Dance declarations
enum {{
{td_enum}
}};

// Tap Dance definitions
tap_dance_action_t tap_dance_actions[] = {{
{td_actions}
}};

layer_state_t default_layer_state_set_user(layer_state_t state) {{
    sval_set_active_layer(0, false);
    return state;
}}

layer_state_t layer_state_set_user(layer_state_t state) {{
    sval_set_active_layer(get_highest_layer(state), false);
    return state;
}}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {{
    // Tap-hold tap dances: send the tap keycode on release when the key was
    // tapped and released before the dance finished (Example 5 in the docs).
    tap_dance_action_t *action;
    switch (keycode) {{
{td_cases}
            td_last_pos = record->event.key;
            action = &tap_dance_actions[QK_TAP_DANCE_GET_INDEX(keycode)];
            if (!record->event.pressed && action->state.count && !action->state.finished) {{
                tap_dance_tap_hold_t *tap_hold = (tap_dance_tap_hold_t *)action->user_data;
                td_key(tap_hold->tap, true);
                td_key(tap_hold->tap, false);
            }}
            break;
    }}

    // Custom keycodes go here.  Define your own starting from SV_SAFE_RANGE,
    // not SAFE_RANGE, so they don't collide with the Svalboard's.
    return true;
}}

void keyboard_post_init_user(void) {{
    memcpy(global_saved_values.layer_colors, my_layer_colors, sizeof(my_layer_colors));

    // Uncomment to debug the matrix over the QMK console (qmk console).
    // debug_enable = true;
    // debug_matrix = true;
}}
'''

if __name__ == "__main__":
    main()
