#!/usr/bin/env python3
"""Export QMK keymaps as the JSON the retro shell's keymap viewer draws.

One JSON per board, driven by a config in boards/<name>.json:

    {
      "name": "svalboard", "title": "Svalboard",
      "qmk_home": "firmware/qmk",                 the firmware tree (relative to this repo)
      "overlay": ".",                             optional userspace overlay
      "keyboard": "svalboard/left", "keymap": "mal", "layout": "LAYOUT",
      "geometry": "kle" | "info",                 geometry.json KLE (Vial format), or qmk info
      "usb": {"vid": "0x303A", "pid": "0x4044"},
      "defines": {"MH_AUTO_BUTTONS_LAYER": 15},   for enum expressions
      "layers": {"NAV_SYMBOLS": ["NAV", "Nav / Symbols"]},   short name, title
      "legends": {"SV_SNIPER_3": "SNP3"}          per-keycode legends
    }

Runs `qmk c2json --no-cpp` for the keycodes, reads the keymap's own
`#define` aliases, the layer enum, the layer designators and the layer
colour table, and writes:

    {
      "name": "svalboard", "title": "Svalboard", "keyboard": ..., "usb": {...},
      "width": 26.0, "height": 7.0,
      "layers": [
        {"index": 0, "name": "BASE", "title": "Base", "color": "#55ff00",
         "keys": [{"x": 1, "y": 0.5, "w": 1, "h": 1, "matrix": [4, 3],
                   "tap": "Q", "hold": "", "trns": false, "none": false,
                   "entry": false}, ...]},
        ...
      ]
    }

`index` is the layer's number on the board, which is what the raw HID link
reports; layers that are transparent everywhere are left out, so the list
can have gaps. Keys that do nothing on any layer are left out too.

`tap` is what the key does when pressed, `hold` what it does when held (a
layer or a modifier) or, for toggles and one-shots, how it does it. A
transparent key carries the legend of the key it falls through to, with
`trns` set so the viewer can ghost it. `entry` marks the keymap's ___E___:
the key that was held to enter the layer.

An index.json listing every exported board is kept beside the outputs.

Usage:
    keymap-export.py [--board NAME ...] [--out-dir DIR]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parent.parent
# Where the retro shell reads the viewer data (Settings.qml's stateDir + /keymap).
DEFAULT_OUT = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "quickshell" / "retro" / "keymap"

# Legends for keycodes whose name is not their legend. Anything missing here
# renders as its name with the KC_ prefix dropped, cut to four cells.
LEGENDS = {
    "KC_NO": "",
    "KC_TRNS": "",
    "KC_ESC": "ESC",
    "KC_ENT": "ENT",
    "KC_ENTER": "ENT",
    "KC_SPC": "SPC",
    "KC_SPACE": "SPC",
    "KC_TAB": "TAB",
    "KC_BSPC": "BSPC",
    "KC_DEL": "DEL",
    "KC_DELETE": "DEL",
    "KC_HOME": "HOME",
    "KC_END": "END",
    "KC_PGUP": "PGUP",
    "KC_PGDN": "PGDN",
    "KC_LEFT": "←",
    "KC_RGHT": "→",
    "KC_RIGHT": "→",
    "KC_UP": "↑",
    "KC_DOWN": "↓",
    "KC_LSFT": "SFT",
    "KC_RSFT": "SFT",
    "KC_LCTL": "CTL",
    "KC_RCTL": "CTL",
    "KC_LALT": "ALT",
    "KC_RALT": "ALT",
    "KC_LGUI": "GUI",
    "KC_RGUI": "GUI",
    "KC_CAPS": "CAPS",
    "KC_PSCR": "PSCR",
    "KC_INS": "INS",
    "KC_APP": "MENU",
    "KC_MUTE": "MUTE",
    "KC_VOLU": "VOL+",
    "KC_VOLD": "VOL-",
    "KC_MPLY": "PLAY",
    "KC_MNXT": "NEXT",
    "KC_MPRV": "PREV",
    "KC_MSTP": "STOP",
    "KC_BRIU": "BRI+",
    "KC_BRID": "BRI-",
    "KC_MINS": "-",
    "KC_MINUS": "-",
    "KC_EQL": "=",
    "KC_EQUAL": "=",
    "KC_LBRC": "[",
    "KC_RBRC": "]",
    "KC_BSLS": "\\",
    "KC_SCLN": ";",
    "KC_QUOT": "'",
    "KC_GRV": "`",
    "KC_GRAVE": "`",
    "KC_COMM": ",",
    "KC_COMMA": ",",
    "KC_DOT": ".",
    "KC_SLSH": "/",
    "KC_SLASH": "/",
    "KC_TILD": "~",
    "KC_EXLM": "!",
    "KC_AT": "@",
    "KC_HASH": "#",
    "KC_DLR": "$",
    "KC_PERC": "%",
    "KC_CIRC": "^",
    "KC_AMPR": "&",
    "KC_ASTR": "*",
    "KC_LPRN": "(",
    "KC_RPRN": ")",
    "KC_UNDS": "_",
    "KC_PLUS": "+",
    "KC_LCBR": "{",
    "KC_RCBR": "}",
    "KC_PIPE": "|",
    "KC_COLN": ":",
    "KC_DQUO": '"',
    "KC_DQT": '"',
    "KC_LT": "<",
    "KC_GT": ">",
    "KC_QUES": "?",
    "KC_LABK": "<",
    "KC_RABK": ">",
    "KC_BTN1": "MB1",
    "KC_BTN2": "MB2",
    "KC_BTN3": "MB3",
    "KC_WH_U": "WH↑",
    "KC_WH_D": "WH↓",
    "QK_BOOT": "BOOT",
    "QK_RBT": "RBT",
    "EE_CLR": "EECL",
    "QK_REP": "REPT",
    "QK_AREP": "AREP",
    "CW_TOGG": "CAPW",
    "QK_LLCK": "LLCK",
    "OS_LSFT": "SFT",
    "OS_RSFT": "SFT",
    "OS_LCTL": "CTL",
    "OS_RCTL": "CTL",
    "OS_LALT": "ALT",
    "OS_RALT": "ALT",
    "OS_LGUI": "GUI",
    "OS_RGUI": "GUI",
    "RGB_TOG": "RGB",
    "RGB_MOD": "RGB>",
    "RGB_VAI": "BRI+",
    "RGB_VAD": "BRI-",
    "RGB_HUI": "HUE+",
    "RGB_HUD": "HUE-",
    "RGB_SAI": "SAT+",
    "RGB_SAD": "SAT-",
}

# What Shift makes of a basic key, so S(KC_7) reads "&" rather than "7"
# over "S".
SHIFTED = {
    "1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&",
    "8": "*", "9": "(", "0": ")", "-": "_", "=": "+", "[": "{", "]": "}",
    "\\": "|", ";": ":", "'": '"', "`": "~", ",": "<", ".": ">", "/": "?",
}

# Short modifier names for chords.
MOD_NAMES = {
    "C": "C", "LCTL": "C", "RCTL": "C", "CTL": "C",
    "S": "S", "LSFT": "S", "RSFT": "S", "SFT": "S",
    "A": "A", "LALT": "A", "RALT": "A", "ALT": "A", "ALGR": "A",
    "G": "G", "LGUI": "G", "RGUI": "G", "GUI": "G", "LCMD": "G", "RCMD": "G",
    "LWIN": "G", "RWIN": "G",
    "MEH": "MEH", "HYPR": "HYP",
    "LCA": "CA", "LSA": "SA", "RSA": "SA", "RCS": "CS", "LCG": "CG", "RCG": "CG",
    "LAG": "AG", "RAG": "AG", "SGUI": "SG", "SCMD": "SG", "SWIN": "SG",
}

# Mod-tap macros: NAME_T(kc) holds NAME.
MOD_TAP = {
    "CTL_T": "CTL", "LCTL_T": "CTL", "RCTL_T": "CTL",
    "SFT_T": "SFT", "LSFT_T": "SFT", "RSFT_T": "SFT",
    "ALT_T": "ALT", "LALT_T": "ALT", "RALT_T": "ALT", "ALGR_T": "ALT",
    "GUI_T": "GUI", "LGUI_T": "GUI", "RGUI_T": "GUI", "LCMD_T": "GUI",
    "RCMD_T": "GUI", "LWIN_T": "GUI", "RWIN_T": "GUI",
    "MEH_T": "MEH", "HYPR_T": "HYP", "ALL_T": "HYP",
    "LCA_T": "C+A", "LSA_T": "S+A", "RSA_T": "S+A", "RCS_T": "C+S",
    "LCG_T": "C+G", "RCG_T": "C+G", "LAG_T": "A+G", "RAG_T": "A+G",
    "SGUI_T": "S+G", "SCMD_T": "S+G", "SWIN_T": "S+G", "C_S_T": "C+S",
}

OSM_NAMES = {
    "MOD_LSFT": "SFT", "MOD_RSFT": "SFT", "MOD_LCTL": "CTL", "MOD_RCTL": "CTL",
    "MOD_LALT": "ALT", "MOD_RALT": "ALT", "MOD_LGUI": "GUI", "MOD_RGUI": "GUI",
}

# QMK's named colours (quantum/color.h). The keymap's own #defines of the
# same shape are read on top of these.
RGB_NAMES = {
    "RGB_AZURE": "#99f5ff", "RGB_BLACK": "#000000", "RGB_BLUE": "#0000ff",
    "RGB_CHARTREUSE": "#80ff00", "RGB_CORAL": "#ff7c4d", "RGB_CYAN": "#00ffff",
    "RGB_GOLD": "#ffd900", "RGB_GOLDENROD": "#d9a521", "RGB_GREEN": "#00ff00",
    "RGB_MAGENTA": "#ff00ff", "RGB_ORANGE": "#ff8000", "RGB_PINK": "#ff80bf",
    "RGB_PURPLE": "#7a00ff", "RGB_RED": "#ff0000", "RGB_SPRINGGREEN": "#00ff80",
    "RGB_TEAL": "#008080", "RGB_TURQUOISE": "#476e6a", "RGB_WHITE": "#ffffff",
    "RGB_YELLOW": "#ffff00", "RGB_OFF": "#000000",
}

TRANSPARENT = {"_______", "KC_TRNS", "KC_TRANSPARENT"}
ENTRY = "___E___"
NONE = {"XXXXXXX", "KC_NO"}


def expand_home(path):
    """~ expanded; a relative path is relative to this repo (firmware/qmk, .)."""
    p = Path(os.path.expanduser(str(path)))
    return p if p.is_absolute() else (REPO / p).resolve()


def run(cmd, cwd, qmk_home):
    env = dict(os.environ, QMK_HOME=str(qmk_home))
    # An overlay that pins its own qmk CLI (uv project with a .venv, like the
    # svalboard repo, whose firmware tree needs Python 3.12) wins over PATH.
    venv_bin = Path(cwd) / ".venv" / "bin"
    if (venv_bin / "qmk").exists():
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(f"command failed: {' '.join(cmd)}")
    return result.stdout


def find_keymap_dir(roots, keyboard, keymap):
    """keyboards/<kb>/keymaps/<km> in any root, walking up the keyboard's
    parents (svalboard/left's keymaps live under svalboard/)."""
    parts = keyboard.split("/")
    for root in roots:
        for depth in range(len(parts), 0, -1):
            candidate = root / "keyboards" / "/".join(parts[:depth]) / "keymaps" / keymap
            if (candidate / "keymap.c").exists():
                return candidate
    sys.exit(f"no keymap.c for {keyboard}:{keymap} under {[str(r) for r in roots]}")


def read_defines(source):
    """Single-line `#define NAME value` pairs from the keymap, in order."""
    defines = {}
    for line in source.splitlines():
        m = re.match(r"\s*#\s*define\s+([A-Za-z_]\w*)\s+(.+?)\s*$", line)
        if m and "(" not in m.group(1):
            defines[m.group(1)] = re.sub(r"//.*$", "", m.group(2)).strip()
    return defines


def eval_int(expr, known):
    """A small integer expression over known names, or None."""
    text = expr.strip()
    for name, value in sorted(known.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(r"\b" + re.escape(name) + r"\b", str(value), text)
    if re.fullmatch(r"[\d\s()+\-*/]+", text):
        try:
            return int(eval(text, {"__builtins__": {}}, {}))  # noqa: S307 - digits and operators only
        except Exception:  # noqa: BLE001
            return None
    return None


def read_layers(source, known):
    """The `enum layers { ... }` block: {enum name: {value, title}}, with
    values from `= expr` where given and counting up otherwise."""
    m = re.search(r"enum\s+layers?\s*\{(.*?)\}", source, re.S)
    if not m:
        sys.exit("no `enum layer(s)` block in the keymap")
    layers = {}
    value = 0
    for line in m.group(1).splitlines():
        line = line.strip()
        entry = re.match(r"([A-Za-z_]\w*)\s*(?:=\s*([^,/]+?))?\s*,?\s*(?://\s*(.*))?$", line)
        if not entry or not entry.group(1):
            continue
        name = entry.group(1)
        if entry.group(2):
            parsed = eval_int(entry.group(2), known)
            if parsed is None:
                sys.stderr.write(f"warning: cannot evaluate layer {name} = {entry.group(2)}\n")
                parsed = value
            value = parsed
        if name.startswith("NUM_") or name.endswith("_COUNT"):
            continue
        layers[name] = {"value": value, "title": (entry.group(3) or "").strip()}
        known[name] = value
        value += 1
    return layers


def read_designators(source):
    """Layer designators of the keymaps[] initialiser, in order: the
    `[NAME] = LAYOUT...(` heads, so c2json's n-th layer can be named."""
    m = re.search(r"keymaps\s*\[[^;]*?\]\s*=\s*\{(.*)", source, re.S)
    if not m:
        return []
    return re.findall(r"\[\s*([A-Za-z_]\w*|\d+)\s*\]\s*=\s*LAYOUT\w*\s*\(", m.group(1))


def hsv_to_hex(h, s, v):
    """QMK's 0..255 HSV to a hex colour."""
    h, s, v = h / 255.0, s / 255.0, v / 255.0
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def read_layer_colors(source, defines, known):
    """Layer colours keyed by layer number: `[_GRP] = { RGB_WHITE }` in an
    RGB table, or `[ 1] = { 21, 255, 255}` in an HSV one."""
    colors = dict(RGB_NAMES)
    for name, value in defines.items():
        parts = re.findall(r"0x([0-9a-fA-F]{2})", value)
        if name.startswith("RGB_") and len(parts) == 3:
            colors[name] = "#" + "".join(p.lower() for p in parts)
    for name, value in defines.items():
        if value in colors:
            colors[name] = colors[value]
    out = {}
    for table in re.finditer(r"(layer_color_map|layer_colors)\s*\[[^=]*?\]\s*=\s*\{(.*?)\};", source, re.S):
        hsv = "hsv" in source[max(0, table.start() - 200):table.start()]
        for layer, value in re.findall(r"\[\s*([^\]]+?)\s*\]\s*=\s*\{\s*([^}]*?)\s*\}", table.group(2)):
            index = eval_int(layer, known)
            if index is None:
                continue
            value = value.strip()
            if value in colors:
                out[index] = colors[value]
                continue
            nums = [int(x, 0) for x in re.findall(r"0x[0-9a-fA-F]+|\d+", value)]
            if len(nums) == 3:
                out[index] = hsv_to_hex(*nums) if hsv else "#%02x%02x%02x" % tuple(nums)
    return out


def default_short(name):
    """`NAV_SYMBOLS` -> `NAVS`, `_NAV` -> `NAV`."""
    return name.lstrip("_").replace("_", "").upper()[:4]


def default_title(name):
    return name.lstrip("_").replace("_", " ").title()


def split_args(text):
    """Top-level comma split of a macro's argument list."""
    args, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


class Legends:
    def __init__(self, defines, layer_names, extra):
        self.defines = defines
        # enum name or number -> short layer name
        self.layer_names = layer_names
        self.extra = extra

    def expand(self, code, depth=0):
        code = code.strip()
        if depth < 16 and code in self.defines and self.defines[code] != code:
            return self.expand(self.defines[code], depth + 1)
        return code

    def layer_name(self, arg):
        arg = self.expand(arg)
        if arg in self.layer_names:
            return self.layer_names[arg]
        return default_short(arg)

    def basic(self, code):
        """Legend for a plain keycode."""
        code = self.expand(code)
        if code in self.extra:
            return self.extra[code]
        if code in LEGENDS:
            return LEGENDS[code]
        m = re.match(r"KC_([A-Z0-9_]+)$", code)
        if m:
            name = m.group(1)
            if name.startswith("KP_"):
                return "kp" + name[3:]
            return name[:4]
        return code[:4]

    def key(self, code):
        """{tap, hold} for any keycode expression."""
        code = self.expand(code)
        m = re.match(r"([A-Za-z_]\w*)\s*\((.*)\)$", code, re.S)
        if not m:
            return {"tap": self.basic(code), "hold": ""}
        name, args = m.group(1), split_args(m.group(2))
        if name == "LT" and len(args) == 2:
            inner = self.key(args[1])
            return {"tap": inner["tap"], "hold": self.layer_name(args[0])}
        if name == "MT" and len(args) == 2:
            inner = self.key(args[1])
            return {"tap": inner["tap"], "hold": OSM_NAMES.get(args[0], args[0].replace("MOD_", "")[:4])}
        if name in MOD_TAP and len(args) == 1:
            inner = self.key(args[0])
            return {"tap": inner["tap"], "hold": MOD_TAP[name]}
        if name in ("MO", "TT") and len(args) == 1:
            return {"tap": self.layer_name(args[0]), "hold": "hold"}
        if name == "TG" and len(args) == 1:
            return {"tap": self.layer_name(args[0]), "hold": "togl"}
        if name == "TO" and len(args) == 1:
            return {"tap": self.layer_name(args[0]), "hold": "goto"}
        if name == "OSL" and len(args) == 1:
            return {"tap": self.layer_name(args[0]), "hold": "1sht"}
        if name == "DF" and len(args) == 1:
            return {"tap": self.layer_name(args[0]), "hold": "dflt"}
        if name == "OSM" and len(args) == 1:
            return {"tap": OSM_NAMES.get(args[0], args[0].replace("MOD_", "")[:4]), "hold": "1sht"}
        if name in MOD_NAMES and len(args) == 1:
            inner = self.key(args[0])
            mods = [MOD_NAMES[name]] + inner.get("mods", [])
            # Shift alone on a key with a shifted legend is that legend.
            if mods == ["S"] and inner["tap"] in SHIFTED and not inner["hold"]:
                return {"tap": SHIFTED[inner["tap"]], "hold": ""}
            hold = "+".join(mods)
            if inner["hold"] and not inner.get("mods"):
                hold = hold + " " + inner["hold"]
            return {"tap": inner["tap"], "hold": hold[:4], "mods": mods}
        if name in ("UC", "UM", "UP", "X"):
            return {"tap": "UNI", "hold": ""}
        return {"tap": name[:4], "hold": ""}


def kle_geometry(vial_json, matrix_index):
    """Key positions from a KLE layout in Vial's json format, as {LAYOUT index: {x, y,
    w, h}}. Labels are "row,col"; decals and keys not in the layout are
    skipped."""
    rows = json.loads(vial_json.read_text())["layouts"]["keymap"]
    out = {}
    y = 0.0
    for row in rows:
        x = 0.0
        w = h = 1.0
        decal = False
        for item in row:
            if isinstance(item, dict):
                x += float(item.get("x", 0))
                y += float(item.get("y", 0))
                w = float(item.get("w", 1))
                h = float(item.get("h", 1))
                decal = bool(item.get("d", False))
                continue
            label = str(item).split("\n")[0].strip()
            m = re.match(r"(\d+)\s*,\s*(\d+)$", label)
            if m and not decal:
                key = (int(m.group(1)), int(m.group(2)))
                if key in matrix_index:
                    out[matrix_index[key]] = {"x": x, "y": y, "w": w, "h": h}
            x += w
            w = h = 1.0
            decal = False
        y += 1
    return out


def export(board, out_dir):
    qmk_home = expand_home(board["qmk_home"])
    roots = []
    if board.get("overlay"):
        roots.append(expand_home(board["overlay"]))
    roots.append(qmk_home)
    keyboard, keymap = board["keyboard"], board["keymap"]
    keymap_dir = find_keymap_dir(roots, keyboard, keymap)
    source = (keymap_dir / "keymap.c").read_text()
    cwd = roots[0]

    codes = json.loads(run(["qmk", "c2json", "--no-cpp", "-kb", keyboard, "-km", keymap, str(keymap_dir / "keymap.c")], cwd, qmk_home))
    info = json.loads(run(["qmk", "info", "-kb", keyboard, "-km", keymap, "-f", "json"], cwd, qmk_home))
    layout_name = board.get("layout") or codes.get("layout")
    if layout_name not in info["layouts"]:
        sys.exit(f"{keyboard} has no layout {layout_name} (has {list(info['layouts'])})")
    layout = info["layouts"][layout_name]["layout"]
    matrix_index = {tuple(k["matrix"]): i for i, k in enumerate(layout)}

    if board.get("geometry", "info") == "kle":
        geometry = kle_geometry(keymap_dir / "geometry.json", matrix_index)
    else:
        geometry = {i: {"x": k["x"], "y": k["y"], "w": k.get("w", 1), "h": k.get("h", 1)} for i, k in enumerate(layout)}

    defines = read_defines(source)
    known = dict(board.get("defines", {}))
    for name, value in defines.items():
        parsed = eval_int(value, known)
        if parsed is not None:
            known[name] = parsed
    layers = read_layers(source, known)
    colors = read_layer_colors(source, defines, known)

    # Short names and titles: the config first, then the enum comment, then
    # the enum name.
    overrides = board.get("layers", {})
    by_value = {}
    for enum_name, meta in layers.items():
        short, title = overrides.get(enum_name, [None, None])
        by_value[meta["value"]] = {
            "enum": enum_name,
            "name": short or default_short(enum_name),
            "title": title or meta["title"] or default_title(enum_name),
        }
    layer_names = {}
    for enum_name, meta in layers.items():
        layer_names[enum_name] = by_value[meta["value"]]["name"]
        layer_names[str(meta["value"])] = by_value[meta["value"]]["name"]
    for alias, target in defines.items():
        if target in layer_names:
            layer_names[alias] = layer_names[target]
    legends = Legends(defines, layer_names, board.get("legends", {}))

    # Which board layer each c2json layer is.
    designators = read_designators(source)
    indices = []
    for i in range(len(codes["layers"])):
        if i < len(designators):
            value = eval_int(designators[i], known)
            indices.append(value if value is not None else i)
        else:
            indices.append(i)

    for i, layer_codes in enumerate(codes["layers"]):
        if len(layer_codes) != len(layout):
            sys.exit(f"layer {i}: {len(layer_codes)} keycodes for {len(layout)} keys in {layout_name}")

    # Resolve legends per layer, then fill transparent keys from the base
    # layer so the viewer can draw what the key actually does, ghosted.
    resolved = []
    for layer_codes in codes["layers"]:
        keys = []
        for code in layer_codes:
            code = code.strip()
            expanded = legends.expand(code)
            if code == ENTRY:
                keys.append({"tap": "", "hold": "", "trns": True, "none": False, "entry": True})
            elif expanded in TRANSPARENT:
                keys.append({"tap": "", "hold": "", "trns": True, "none": False, "entry": False})
            elif expanded in NONE:
                keys.append({"tap": "", "hold": "", "trns": False, "none": True, "entry": False})
            else:
                legend = legends.key(code)
                keys.append({"tap": legend["tap"], "hold": legend["hold"], "trns": False, "none": False, "entry": False})
        resolved.append(keys)
    base = resolved[0] if resolved else []
    for keys in resolved[1:]:
        for k, key in enumerate(keys):
            if key["trns"] and not base[k]["none"]:
                key["tap"] = base[k]["tap"]
                key["hold"] = base[k]["hold"]

    # Keys that do nothing on any layer are not on the board worth drawing
    # (the Svalboard's optional double-south keys, say).
    used = [any(not keys[k]["none"] and not (keys[k]["trns"] and base[k]["none"]) for keys in resolved) for k in range(len(layout))]

    out_layers = []
    for i, keys in enumerate(resolved):
        index = indices[i]
        # Layers that are transparent everywhere are filler.
        if i > 0 and all(key["trns"] or key["none"] for key in keys):
            continue
        meta = by_value.get(index, {"enum": str(index), "name": default_short(str(index)), "title": str(index)})
        placed = []
        for k, key in enumerate(keys):
            if not used[k] or k not in geometry:
                continue
            g = geometry[k]
            placed.append({
                "x": g["x"], "y": g["y"], "w": g["w"], "h": g["h"],
                "matrix": list(layout[k]["matrix"]),
                **key,
            })
        out_layers.append({
            "index": index,
            "name": meta["name"],
            "title": meta["title"],
            "color": colors.get(index, ""),
            "keys": placed,
        })

    shown = [g for k, g in geometry.items() if used[k]]
    min_x = min(g["x"] for g in shown)
    min_y = min(g["y"] for g in shown)
    for layer in out_layers:
        for key in layer["keys"]:
            key["x"] = round(key["x"] - min_x, 3)
            key["y"] = round(key["y"] - min_y, 3)
    width = round(max(g["x"] + g["w"] for g in shown) - min_x, 3)
    height = round(max(g["y"] + g["h"] for g in shown) - min_y, 3)

    result = {
        "name": board["name"],
        "title": board.get("title", board["name"]),
        "keyboard": keyboard,
        "keymap": keymap,
        "layout": layout_name,
        "usb": board.get("usb", {}),
        "width": width,
        "height": height,
        "layers": out_layers,
    }
    out = out_dir / f"{board['name']}.json"
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(f"{board['name']}: {len(out_layers)} layers, {len(shown)} keys, {width}x{height} -> {out}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--board", action="append", help="board config name under boards/ (default: all)")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    names = args.board or sorted(p.stem for p in (HERE / "boards").glob("*.json"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    index_path = out_dir / "index.json"
    index = {"boards": []}
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text())
        except ValueError:
            pass
    listed = {b["name"]: b for b in index.get("boards", [])}
    for name in names:
        config = json.loads((HERE / "boards" / f"{name}.json").read_text())
        result = export(config, out_dir)
        listed[name] = {"name": name, "title": result["title"], "usb": result["usb"]}
    index_path.write_text(json.dumps({"boards": [listed[n] for n in sorted(listed)]}, indent=1) + "\n")


if __name__ == "__main__":
    main()
