import essentia.standard as es
import streamlit as st

# [0, 1) very low confidence, the input signal is hard for the employed candidate beat trackers
#
# [1, 1.5] low confidence
#
# (1.5, 3.5] good confidence, accuracy around 80% in AMLt measure
#
# (3.5, 5.32] excellent confidence


@st.cache_data
def nn_re_intervals(uploaded_file, trashold=0):
    tmp_path = uploaded_file
    audio = es.MonoLoader(filename=tmp_path)()
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, ticks, confidence, estimates, bpmIntervals = rhythm_extractor(audio)
    intervals = []
    # start = beats[0]
    # global_time = start
    # curr_tempo = 60 / beats[1]
    # for i in range(1, len(beats) - 1):
    #     global_time += beats[i]
    #     tmp_tempo = 60 / beats[i + 1]
    #     if abs(round(curr_tempo, 2) - round(tmp_tempo, 2)) > trashold:
    #         intervals += [[start, curr_tempo]]
    #         start = global_time
    #         curr_tempo = tmp_tempo
    # intervals += [[start, curr_tempo]]
    print(estimates)
    print(len(ticks))
    print(len(estimates))
    return bpm, ticks, confidence, estimates, bpmIntervals
