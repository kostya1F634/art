import librosa
import numpy as np
import streamlit as st


@st.cache_data
def audio(path, sr=48000):
    return librosa.load(path, sr=sr, res_type="soxr_vhq")


@st.cache_data
def dynamic_tempo(
    audio,
    hop_length=512,
    start_bpm=120.0,
    std_bpm=1.0,
    ac_size=8.0,
    max_tempo=320.0,
    aggregate=None,
):
    y, sr = audio
    return librosa.feature.tempo(
        y=y,
        sr=sr,
        hop_length=hop_length,
        start_bpm=start_bpm,
        std_bpm=std_bpm,
        ac_size=ac_size,
        max_tempo=max_tempo,
        aggregate=aggregate,
    )


@st.cache_data
def time_tempo(audio, dynamic_tempo, hop_length=512):
    y, sr = audio
    return librosa.times_like(dynamic_tempo, sr=sr, hop_length=hop_length)


@st.cache_data
def intervals(onset_bpm, onset_times):
    intervals = []
    start = onset_times[0]
    curr_tempo = onset_bpm[0]
    for time, tempo in zip(onset_times[1:], onset_bpm[1:]):
        if round(curr_tempo, 2) != round(tempo, 2):
            intervals += [[start, curr_tempo]]
            start = time
            curr_tempo = tempo
    intervals += [[start, curr_tempo]]
    return intervals


@st.cache_data
def onset_bpm(dynamic_bpm, onset_times, time_tempo):
    onset_times = np.array(onset_times)
    indices = np.searchsorted(time_tempo, onset_times, side="right") - 1
    indices = np.clip(indices, 0, len(dynamic_bpm) - 1)
    return dynamic_bpm[indices]


@st.cache_data
def music(
    audio,
    dynamic_clicks,
    volume=20,
):
    y, sr = audio
    click_dynamic = dynamic_clicks
    volume_reduce = volume / 100
    y_reduced = y * volume_reduce
    combined_audio = y_reduced + click_dynamic
    max_amplitude = np.mean(combined_audio)
    if max_amplitude > 1.0:
        combined_audio = combined_audio / max_amplitude
    return combined_audio, sr


@st.cache_data
def dynamic_clicks(audio, dynamic_times, hop_length, click_freq, click_duration):
    y, sr = audio
    return librosa.clicks(
        times=dynamic_times,
        sr=sr,
        hop_length=hop_length,
        click_freq=click_freq,
        click_duration=click_duration,
        length=len(y),
    )


@st.cache_data
def onset_times(
    audio,
    dynamic_tempo,
    hop_length=512,
    start_bpm=120.0,
    tightness=100.0,
    trim=True,
    units="time",
):
    y, sr = audio
    return librosa.beat.beat_track(
        y=y,
        sr=sr,
        bpm=dynamic_tempo,
        hop_length=hop_length,
        start_bpm=start_bpm,
        tightness=tightness,
        trim=trim,
        units=units,
    )
