/* the board header is picked by build.sh (BOARD=sweet|pdx203 -> -DBOARD_x) */
#pragma once
#if defined(BOARD_PDX203)
#include "boards/pdx203.h"
#else
#include "boards/sweet.h"
#endif
