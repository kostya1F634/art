import os
from translation import translation
from utils import cover_from_audio, audio_from_zip, is_archive, save_file
from timings import insert_timing_points, create_beatmap
import tempo
import streamlit as st
import numpy as np
import plotly.express as px


def render_dashboard():
    t = translation(st.session_state.get("language", "en"))
    st.title(t["title"])
    st.subheader(t["subtitle"])
    with st.container(border=True):
        upload_file = st.file_uploader(
            t["choose_file"],
            type=[
                "mp3",
                "wav",
                "ogg",
                "olz",
                "osz",
                "osu",
            ],
        )
        if st.session_state.upload_orig != upload_file:
            st.session_state.upload_orig = upload_file
            st.session_state.upload = upload_file
            st.rerun()

    if upload_file is None:
        return
    pbar = st.progress(0, t["create_tmp"])
    if is_archive(st.session_state.upload_orig):
        path_to_audio = audio_from_zip(upload_file)
        st.session_state.beatmap_upload = upload_file
        st.session_state.upload = path_to_audio
    else:
        path_to_audio = save_file(upload_file)
        st.session_state.beatmap_upload = None
        st.session_state.upload = path_to_audio
    pbar.progress(100, "")
    pbar.empty()

    if os.name != "nt":
        nn_bpm, nn_confidence, nn_beats_position, nn_hist, nn_intervals, nn_metronom = (
            nn_audio_processing()
        )
    if st.session_state.classic_on:
        (
            dynamic_bpm,
            onset_times,
            onset_bpm,
            intervals,
            music_y,
            music_sr,
        ) = audio_processing()

    with st.container(border=True):
        st.write(t["nn_metronom"])
        if os.name != "nt":
            st.audio(nn_metronom)
        if st.session_state.classic_on:
            st.write(t["audio_clicks"])
            st.audio(music_y, sample_rate=music_sr)

    nn_tab, c_tab, beatmap, general = st.tabs(
        [
            t["nn_method"],
            t["c_method"],
            t["beatmap"],
            t["overview"],
        ]
    )
    with c_tab:
        if st.session_state.classic_on:
            col_average, col_onset, col_changes = st.columns(3, border=True)
            with col_average:
                unique_bpm, counts = np.unique(dynamic_bpm, return_counts=True)
                most_common_bpm_index = np.argmax(counts)
                most_common_bpm = unique_bpm[most_common_bpm_index]
                st.metric("BPM", round(most_common_bpm, 2))
            with col_onset:
                st.metric(
                    t["first_onset"],
                    str(round(onset_times[0] * 1000)).replace(".", ","),
                )
            with col_changes:
                st.metric(t["bpm_change"], len(onset_times) - 1)
            with st.container(border=True):
                x, y = onset_times, onset_bpm
                data = {
                    "x": x,
                    "y": y,
                }
                fig = px.line(
                    data,
                    x="x",
                    y="y",
                    title=t["bpm_dynamic"],
                    labels={"x": t["time"], "y": "BPM"},
                )
                fig.update_traces(line=dict(color="#003399"))
                st.plotly_chart(fig)

            with st.expander(t["time_intervals"]):
                time_diffs = np.diff(onset_times)
                data = {
                    "x": onset_times[1:],
                    "y": time_diffs,
                }
                fig = px.line(
                    data,
                    x="x",
                    y="y",
                    title=t["time_intervals_between_onsets"],
                    labels={
                        "x": t["time"],
                        "y": t["time_between_onsets"],
                    },
                )
                fig.update_traces(line=dict(color="#003399"))
                st.plotly_chart(fig)
            with st.expander(t["timings"] + f" ({len(onset_times)})"):
                data = {t["time"]: [], "BPM": []}
                for start, bpm in zip(onset_times, onset_bpm):
                    data[t["time"]] += [f"{start:.3f}".replace(".", ",")]
                    data["BPM"] += [str(round(bpm, 2))]
                st.table(data)
        else:
            st.write(t["turn_on_classic"])
    with nn_tab:
        if os.name != "nt":
            col_nn_average, col_nn_onset, col_nn_confidence = st.columns(3, border=True)
            with col_nn_average:
                st.metric("BPM", round(nn_bpm, 2))
            with col_nn_onset:
                st.metric(
                    t["first_onset"],
                    str(round(nn_beats_position[0] * 1000)).replace(".", ","),
                )
            with col_nn_confidence:
                st.metric(t["confidence"], round(nn_confidence, 4))
            ic = interpert_confidence(nn_confidence)
            st.info(ic[1:], icon=ic[0])
            with st.container(border=True):
                x = []
                y = []
                for i, j in nn_intervals:
                    x += [i]
                    y += [j]
                data = {
                    "x": x,
                    "y": y,
                }
                fig = px.line(
                    data,
                    x="x",
                    y="y",
                    title=t["bpm_dynamic"],
                    labels={"x": t["time"], "y": "BPM"},
                )
                fig.update_traces(line=dict(color="#003399"))
                st.plotly_chart(fig)
            with st.expander(t["bpm_dist"]):
                histogram = nn_hist
                bpm_bins = list(range(len(histogram)))
                data = {
                    "BPM": bpm_bins,
                    t["weight"]: histogram,
                }
                fig = px.bar(
                    data,
                    x="BPM",
                    y=t["weight"],
                    title=t["bpm_hist"],
                    labels={"BPM": "BPM", "Weight": "Weight"},
                )
                fig.update_traces(marker_color="#003399")
                st.plotly_chart(fig)
            with st.expander(t["timings"] + f" ({len(nn_intervals)})"):
                data = {t["time"]: [], "BPM": []}
                for start, bpm in nn_intervals:
                    data[t["time"]] += [f"{start:.3f}".replace(".", ",")]
                    data["BPM"] += [str(round(bpm, 2))]
                st.table(data)
        else:
            st.write("Use linux / macOS")
    with beatmap:
        with st.container(border=True):
            if st.session_state.beatmap_upload is None:
                st.subheader(t["download_beatmap"])
                title, artist = st.columns(2)
                with title:
                    st.text_input(
                        t["beatmap_title"],
                        value="ART title",
                        key="beatmap_title",
                    )
                with artist:
                    st.text_input(
                        t["beatmap_artist"],
                        value="ART artist",
                        key="beatmap_artist",
                    )
                osu_name = f"{st.session_state.beatmap_artist} - {st.session_state.beatmap_title} (ART) [].osz"
                if st.session_state.classic_on:
                    st.download_button(
                        label=t["c_timings"],
                        data=osu_beatmap(zip(onset_times, onset_bpm)),
                        file_name=osu_name,
                        mime="application/zip",
                        key="download_new_beatmap",
                    )
                st.download_button(
                    label=t["nn_timings"],
                    data=osu_beatmap(nn_intervals),
                    file_name=osu_name,
                    mime="application/zip",
                    key="download_new_beatmap_nn",
                )
            else:
                if st.session_state.classic_on:
                    st.download_button(
                        label=t["c_timings"],
                        data=insert_choise(zip(onset_times, onset_bpm)),
                        file_name=st.session_state.beatmap_upload.name,
                        mime=st.session_state.beatmap_upload.type,
                        key="download_uploaded_beatmap",
                    )
                st.download_button(
                    label=t["nn_timings"],
                    data=insert_choise(nn_intervals),
                    file_name=st.session_state.beatmap_upload.name,
                    mime=st.session_state.beatmap_upload.type,
                    key="download_uploaded_beatmap_nn",
                )
    with general:
        col_info, col_image = st.columns([1, 2], border=True)
        with col_image:
            cover_data = cover_from_audio(st.session_state.upload_orig)
            if cover_data:
                st.image(cover_data)
            else:
                st.info(t["no_track_cover"])


def interpert_confidence(confidence):
    t = translation(st.session_state.get("language", "en"))
    if confidence < 1:
        return "🔴 " + t["very_low_confidence"]
    elif confidence <= 1.5:
        return "🟠 " + t["low_confidence"]
    elif confidence <= 3.5:
        return "🟡 " + t["good_confidence"]
    else:
        return "🟢 " + t["excellent_confidence"]


def audio_processing():
    t = translation(st.session_state.get("language", "en"))
    pbar = st.progress(0, t["decoding_audio"])
    audio = tempo.audio(st.session_state.upload, sr=st.session_state.sample_rate)
    pbar.progress(13, t["estimating_tempo"])
    dynamic_tempo = tempo.dynamic_tempo(
        audio,
        hop_length=st.session_state.hop_length,
        start_bpm=st.session_state.start_bpm,
        std_bpm=st.session_state.standard_bpm,
        ac_size=st.session_state.ac_size,
        max_tempo=st.session_state.max_bpm,
    )
    pbar.progress(26, t["detecting_beats"])
    dynamic_bpm, onset_times = tempo.onset_times(
        audio,
        dynamic_tempo,
        hop_length=st.session_state.hop_length,
        start_bpm=st.session_state.start_bpm,
        tightness=st.session_state.tightness,
        trim=st.session_state.trim,
    )
    pbar.progress(39, t["generating_timeline"])
    time_tempo = tempo.time_tempo(
        audio, dynamic_tempo=dynamic_bpm, hop_length=st.session_state.hop_length
    )
    pbar.progress(52, t["mapping_bpm_beats"])
    onset_bpm = tempo.onset_bpm(dynamic_bpm, onset_times, time_tempo)
    pbar.progress(65, t["detecting_intervals"])
    intervals = tempo.intervals(onset_bpm, onset_times)
    pbar.progress(78, t["generating_clicks"])
    dynamic_clicks = tempo.dynamic_clicks(
        audio,
        onset_times,
        hop_length=st.session_state.hop_length,
        click_freq=st.session_state.click_freq,
        click_duration=st.session_state.click_duration,
    )
    pbar.progress(91, t["mixing_audio"])
    music_y, music_sr = tempo.music(
        audio,
        dynamic_clicks,
        volume=st.session_state.volume,
    )
    pbar.progress(100, "")
    pbar.empty()
    return (
        dynamic_bpm,
        onset_times,
        onset_bpm,
        intervals,
        music_y,
        music_sr,
    )


def nn_audio_processing():
    t = translation(st.session_state.get("language", "en"))
    pbar = st.progress(0, t["beat_detection"])
    nn_bpm, nn_confidence, nn_beats_position, nn_hist = tempo.re(
        st.session_state.upload, sample_rate=st.session_state.sample_rate
    )
    pbar.progress(50, t["calc_intervals"])
    nn_intervals = tempo.nn_intervals(nn_beats_position)
    pbar.progress(70, t["calc_metronome"])
    nn_metronom = tempo.nn_metronom(
        st.session_state.upload,
        nn_beats_position,
        st.session_state.volume,
        st.session_state.click_freq,
        st.session_state.click_duration,
    )
    pbar.progress(100, "")
    pbar.empty()
    return nn_bpm, nn_confidence, nn_beats_position, nn_hist, nn_intervals, nn_metronom


def insert_choise(intervals):
    insert_timing_points(st.session_state.beatmap_upload, intervals)
    return st.session_state.beatmap_upload.getvalue()


def osu_beatmap(intervals):
    return create_beatmap(
        st.session_state.upload,
        st.session_state.beatmap_title,
        st.session_state.beatmap_artist,
        intervals,
    )
