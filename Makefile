# All boards build through the qmk CLI pinned by pyproject.toml (`uv run qmk`),
# against the firmware tree each board needs (QMK_HOME per target).
#
#   make                              build everything
#   make svalboard-left               one target (also: svalboard-right, unicorne, lulu)
#   make flash-svalboard-right        build, then wait for the board in bootloader and copy
#   make flash-unicorne / flash-lulu
#   make export                       regenerate the desktop viewer's keymap JSON
#   make import KBI=keybard-exports/x.kbi   Keybard export -> svalboard keymap.c
#   make update-svalboard             rebase the Svalboard fork on upstream
#   make update-qmk                   move firmware/qmk to current upstream master
#   make setup                        fresh machine (see setup.sh)

QMK     := uv run qmk
KEYMAP  ?= micleo2
export QMK KEYMAP

SVAL_FW := $(CURDIR)/firmware/svalboard
QMK_FW  := $(CURDIR)/firmware/qmk

# Svalboard: both halves carry a pmw3389 trackball.  POINTER= for none,
# trackpoint, trackball/pmw3360, azoteq, pimoroni.
POINTER   ?= trackball/pmw3389
SVAL_LEFT  := svalboard/$(if $(POINTER),$(POINTER)/,)left
SVAL_RIGHT := svalboard/$(if $(POINTER),$(POINTER)/,)right
UNICORNE   := boardsource/unicorne
LULU       := boardsource/lulu/rp2040

KBI ?= keybard-exports/mouse_on_base.kbi

.PHONY: all svalboard-left svalboard-right unicorne lulu \
        flash-svalboard-left flash-svalboard-right flash-unicorne flash-lulu \
        export import update-svalboard update-qmk setup clean

all: svalboard-left svalboard-right unicorne lulu

svalboard-left:
	QMK_HOME=$(SVAL_FW) $(QMK) compile -kb $(SVAL_LEFT) -km $(KEYMAP) -j$$(nproc)
svalboard-right:
	QMK_HOME=$(SVAL_FW) $(QMK) compile -kb $(SVAL_RIGHT) -km $(KEYMAP) -j$$(nproc)
unicorne:
	QMK_HOME=$(QMK_FW) $(QMK) compile -kb $(UNICORNE) -km $(KEYMAP) -j$$(nproc)
lulu:
	QMK_HOME=$(QMK_FW) $(QMK) compile -kb $(LULU) -km $(KEYMAP) -j$$(nproc)

flash-svalboard-left:
	QMK_HOME=$(SVAL_FW) tools/flash.sh $(SVAL_LEFT)
flash-svalboard-right:
	QMK_HOME=$(SVAL_FW) tools/flash.sh $(SVAL_RIGHT)
flash-unicorne:
	QMK_HOME=$(QMK_FW) tools/flash.sh $(UNICORNE)
flash-lulu:
	QMK_HOME=$(QMK_FW) tools/flash.sh $(LULU)

export:
	host/keymap-export.py

import:
	python3 tools/kbi2keymap.py $(KBI) > keyboards/svalboard/keymaps/$(KEYMAP)/keymap.c

update-svalboard:
	git -C firmware/svalboard fetch upstream
	git -C firmware/svalboard rebase upstream/vial
	git -C firmware/svalboard submodule update --init --recursive
	@echo "then: git -C firmware/svalboard push --force-with-lease origin mal && git add firmware/svalboard && git commit"
update-qmk:
	git -C firmware/qmk fetch origin master
	git -C firmware/qmk checkout --detach origin/master
	git -C firmware/qmk submodule update --init --recursive
	@echo "then: make unicorne lulu && git add firmware/qmk && git commit -m 'firmware/qmk: bump to upstream'"

setup:
	./setup.sh

clean:
	rm -f *.uf2
	QMK_HOME=$(SVAL_FW) $(QMK) clean
	QMK_HOME=$(QMK_FW) $(QMK) clean
