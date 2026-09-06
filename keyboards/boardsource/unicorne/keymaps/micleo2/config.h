// Copyright 2024 QMK
// SPDX-License-Identifier: GPL-2.0-or-later

/*******************************************************************************
  88888888888 888      d8b                .d888 d8b 888               d8b
      888     888      Y8P               d88P"  Y8P 888               Y8P
      888     888                        888        888
      888     88888b.  888 .d8888b       888888 888 888  .d88b.       888 .d8888b
      888     888 "88b 888 88K           888    888 888 d8P  Y8b      888 88K
      888     888  888 888 "Y8888b.      888    888 888 88888888      888 "Y8888b.
      888     888  888 888      X88      888    888 888 Y8b.          888      X88
      888     888  888 888  88888P'      888    888 888  "Y8888       888  88888P'
                                                        888                 888
                                                        888                 888
                                                        888                 888
     .d88b.   .d88b.  88888b.   .d88b.  888d888 8888b.  888888 .d88b.   .d88888
    d88P"88b d8P  Y8b 888 "88b d8P  Y8b 888P"      "88b 888   d8P  Y8b d88" 888
    888  888 88888888 888  888 88888888 888    .d888888 888   88888888 888  888
    Y88b 888 Y8b.     888  888 Y8b.     888    888  888 Y88b. Y8b.     Y88b 888
     "Y88888  "Y8888  888  888  "Y8888  888    "Y888888  "Y888 "Y8888   "Y88888
         888
    Y8b d88P
     "Y88P"
*******************************************************************************/

#pragma once

/* Settings that used to live in the keyboard-level config.h of the rover fork.
 * Keymap config.h is included after the keyboard's, so #undef/#define wins. */

#undef STARTUP_SONG
#define STARTUP_SONG SONG(STARTUP_SOUND)

// Joystick lives on the right half; upstream inverts both axes, we rotate instead.
#undef POINTING_DEVICE_INVERT_X
#undef POINTING_DEVICE_INVERT_Y
// #define MASTER_RIGHT
#ifndef MASTER_RIGHT
#    define SPLIT_POINTING_ENABLE
#    define POINTING_DEVICE_ROTATION_90
#    define POINTING_DEVICE_RIGHT
#else
#    define POINTING_DEVICE_ROTATION_90
#endif
#define ANALOG_JOYSTICK_SPEED_REGULATOR 5

#define OLED_BRIGHTNESS 128

// Only the breathing animation, and make it the default (keyboard.json enables six).
#undef ENABLE_RGB_MATRIX_ALPHAS_MODS
#undef ENABLE_RGB_MATRIX_BAND_SAT
#undef ENABLE_RGB_MATRIX_BAND_VAL
#undef ENABLE_RGB_MATRIX_GRADIENT_LEFT_RIGHT
#undef ENABLE_RGB_MATRIX_GRADIENT_UP_DOWN
#undef RGB_MATRIX_DEFAULT_MODE
#define RGB_MATRIX_DEFAULT_MODE RGB_MATRIX_BREATHING

// tap-hold logic
#define TAPPING_TERM 170
#define PERMISSIVE_HOLD
#define PERMISSIVE_HOLD_PER_KEY
#define TAPPING_TERM_PER_KEY
#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY

#define FORCE_NKRO
