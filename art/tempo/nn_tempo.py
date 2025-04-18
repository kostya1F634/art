import essentia.standard as es
import streamlit as st


@st.cache_data
def nn_re_intervals(uploaded_file, trashold=0):
    tmp_path = uploaded_file
    audio = es.MonoLoader(filename=tmp_path)()
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, _, _, _, beats = rhythm_extractor(audio)
    intervals = []
    start = beats[0]
    global_time = start
    curr_tempo = 60 / beats[1]
    for i in range(1, len(beats) - 1):
        global_time += beats[i]
        tmp_tempo = 60 / beats[i + 1]
        if abs(round(curr_tempo, 2) - round(tmp_tempo, 2)) > trashold:
            intervals += [[start, curr_tempo]]
            start = global_time
            curr_tempo = tmp_tempo
    intervals += [[start, curr_tempo]]
    return bpm, intervals


@st.cache_data
def nn_btmf_intervals(uploaded_file, trashold=0):
    tmp_path = uploaded_file
    audio = es.MonoLoader(filename=tmp_path)()
    bt = es.BeatTrackerMultiFeature()
    beats, confidence = bt(audio)
    intervals = []
    start = beats[0]
    curr_tempo = 60 / (beats[1] - beats[0])
    for i in range(1, len(beats) - 2):
        tmp_tempo = 60 / (beats[i + 1] - beats[i])
        if abs(round(curr_tempo, 2) - round(tmp_tempo, 2)) > trashold:
            intervals += [[start, curr_tempo]]
            start = beats[i]
            curr_tempo = tmp_tempo
    intervals += [[start, curr_tempo]]
    return confidence, intervals
