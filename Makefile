# Thin wrapper around the qmk CLI.  The vendor tree and this overlay are
# wired together via `qmk config` (see README.md).
#
#   make left right            build both halves (trackball pmw3389 by default)
#   make left POINTER=            plain build, no pointing device
#   make left POINTER=trackpoint
#   make right POINTER=trackball/pmw3389
#   make flash-left            build + wait for bootloader + copy (see tools/flash.sh)
#   make flash                 both halves, one after the other
#   make import KBI=layouts/keybard/foo.kbi   regenerate keymap.c from a Keybard export
#   make update                  fetch upstream Svalboard firmware and rebase the fork's branch

# The qmk CLI runs from the uv-managed env (pyproject.toml); the vendor tree's
# Python helpers need 3.12.
QMK     := uv run qmk
export QMK
KEYMAP  ?= mal
POINTER ?= trackball/pmw3389
KB_LEFT  := svalboard/$(if $(POINTER),$(POINTER)/,)left
KB_RIGHT := svalboard/$(if $(POINTER),$(POINTER)/,)right
KBI ?= layouts/keybard/mouse_on_base.kbi

.PHONY: all left right flash flash-left flash-right import update clean

all: left right

left:
	$(QMK) compile -kb $(KB_LEFT) -km $(KEYMAP) -j$$(nproc)

right:
	$(QMK) compile -kb $(KB_RIGHT) -km $(KEYMAP) -j$$(nproc)

flash-left:
	KEYMAP=$(KEYMAP) tools/flash.sh left $(POINTER)

flash-right:
	KEYMAP=$(KEYMAP) tools/flash.sh right $(POINTER)

flash: flash-left flash-right

import:
	python3 tools/kbi2keymap.py $(KBI) > keyboards/svalboard/keymaps/$(KEYMAP)/keymap.c

clean:
	$(QMK) clean

update:
	git -C firmware fetch upstream
	git -C firmware rebase upstream/vial
	git -C firmware submodule update --init --recursive
	@echo "now: git -C firmware push --force-with-lease origin mal  &&  git add firmware && git commit"
