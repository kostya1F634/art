import essentia.standard as es
import streamlit as st
import numpy as np


# [0, 1) very low confidence, the input signal is hard for the employed candidate beat trackers
# [1, 1.5] low confidence
# (1.5, 3.5] good confidence, accuracy around 80% in AMLt measure
# (3.5, 5.32] excellent confidence


@st.cache_data
def re(file, sample_rate=44100):
    audio = es.MonoLoader(filename=file, sampleRate=sample_rate)()
    rhythm_descriptor = es.RhythmDescriptors()
    (
        beats_position,
        confidence,
        bpm,
        bpm_estimates,
        bpm_intervals,
        first_peak_bpm,
        first_peak_spread,
        first_peak_weight,
        second_peak_bpm,
        second_peak_spread,
        second_peak_weight,
        histogram,
    ) = rhythm_descriptor(audio)
    return bpm, confidence, beats_position, bpm_estimates, bpm_intervals, histogram
