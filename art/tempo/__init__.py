import os

from .tempo import (
    audio,
    dynamic_tempo,
    time_tempo,
    music,
    dynamic_clicks,
    intervals,
    onset_bpm,
    onset_times,
)

if os.name != "nt":
    from .nn_tempo import re, nn_metronom, nn_intervals
