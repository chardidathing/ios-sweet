#pragma once
/* keep a command mode panel refreshing from the splash buffer (no-op on video mode boards) */
void display_setup(void);
/* the mdp state seen by display_setup, drawn with the console */
void display_report(void);
