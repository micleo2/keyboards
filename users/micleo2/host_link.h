// Copyright 2026 micleo2
// SPDX-License-Identifier: GPL-2.0-or-later

// Raw HID link to the desktop shell; see host_link.c for the protocol.
#pragma once

#include <stdbool.h>
#include <stdint.h>

// True while a host has said HELLO recently.
bool host_link_connected(void);

#ifdef VIA_ENABLE
// Handles a raw HID packet that VIA did not recognise. Returns true when
// it was one of ours. The keyboard's raw_hid_receive_kb calls this first.
bool raw_hid_receive_user(uint8_t *data, uint8_t length);
#endif
