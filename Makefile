# Thin wrapper around the qmk CLI.  The vendor tree and this overlay are
# wired together via `qmk config` (see README.md).
#
#   make left right            build both halves (plain, no pointing device)
#   make left POINTER=trackpoint
#   make right POINTER=trackball/pmw3389
#   make flash-left            put the half in bootloader first (double-tap reset)
#   make import KBI=layouts-kbi/foo.kbi   regenerate keymap.c from a Keybard export

KEYMAP  ?= mal
POINTER ?=
KB_LEFT  := svalboard/$(if $(POINTER),$(POINTER)/,)left
KB_RIGHT := svalboard/$(if $(POINTER),$(POINTER)/,)right
KBI ?= layouts-kbi/mouse_on_base.kbi

.PHONY: all left right flash-left flash-right import clean

all: left right

left:
	qmk compile -kb $(KB_LEFT) -km $(KEYMAP)

right:
	qmk compile -kb $(KB_RIGHT) -km $(KEYMAP)

flash-left:
	qmk flash -kb $(KB_LEFT) -km $(KEYMAP)

flash-right:
	qmk flash -kb $(KB_RIGHT) -km $(KEYMAP)

import:
	python3 tools/kbi2keymap.py $(KBI) > keyboards/svalboard/keymaps/$(KEYMAP)/keymap.c

clean:
	qmk clean
