from io import BytesIO
import essentia.standard as es
import essentia
from pydub import AudioSegment
from pydub.generators import Sine
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


@st.cache_data
def nn_intervals(beats_position, bpm_estimates, trashold=1):
    intervals = []
    for i in range(0, len(beats_position) - 1):
        local_bpm = 60 / (beats_position[i + 1] - beats_position[i])
        intervals += [[beats_position[i], local_bpm]]
    return intervals


@st.cache_data
def nn_metronom(file, ticks, volume=100):
    original = AudioSegment.from_file(file)
    volume_reduce_db = 20 * np.log10(volume / 100.0) if volume < 100 else 0
    original = original + volume_reduce_db
    click = Sine(350).to_audio_segment(duration=50).apply_gain(-3)
    metronome = AudioSegment.silent(duration=len(original))
    for t in ticks:
        position_ms = int(t * 1000)
        metronome = metronome.overlay(click, position=position_ms)
    combined = original.overlay(metronome)
    buffer = BytesIO()
    combined.export(buffer, format="wav")
    buffer.seek(0)
    return buffer
