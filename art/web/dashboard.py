import sys
from web.translation import translation
from web.utils import extract_cover, is_archive, extract_audio_from_zip
from timings import insert_timing_points, create_beatmap
import tempo
import pyperclip
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


class Dashboard:
    def __init__(self):
        self.td = translation(st.session_state.get("language", "en"))

    def t(self, key):
        return f"{self.td[key]}"

    def render(self):
        st.title(self.t("title"))
        st.subheader(self.t("subtitle"))
        with st.container(border=True):
            upload_file = st.file_uploader(
                self.t("choose_file"),
                type=[
                    "wav",
                    "mp3",
                    "flac",
                    "ogg",
                    "m4a",
                    "wma",
                    "aiff",
                    "aif",
                    "olz",
                    "osz",
                    "osu",
                ],
            )
            if st.session_state.upload != upload_file:
                st.session_state.upload = upload_file
                st.rerun()
        if st.session_state.get("upload", None) is not None:
            if is_archive(st.session_state.upload):
                path_to_audio = extract_audio_from_zip(st.session_state.upload)
                st.session_state.beatmap_upload = st.session_state.upload
                st.session_state.upload = path_to_audio
            else:
                st.session_state.beatmap_upload = None
            (
                dynamic_bpm,
                onset_times,
                onset_bpm,
                intervals,
                music_y,
                music_sr,
            ) = audio_processing()
        else:
            return
        with st.container(border=True):
            st.write(self.t("audio_clicks"))
            st.audio(music_y, sample_rate=music_sr)
        classic, nn, beatmap, general = st.tabs(
            [
                self.t("c_method"),
                self.t("nn_method"),
                self.t("beatmap"),
                self.t("overview"),
            ]
        )
        with classic:
            time_diffs = np.diff(onset_times)
            score = complexity_score(dynamic_bpm, intervals[-1][1], time_diffs)
            col_average, col_onset, col_score, col_changes = st.columns(4, border=True)
            with col_average:
                st.metric(f"{self.t('average')} BPM", round(np.mean(dynamic_bpm), 2))
            with col_onset:
                st.metric(
                    self.t("first_onset"),
                    str(round(onset_times[0], 3)).replace(".", ","),
                )
            with col_score:
                st.metric(
                    self.t("complexity_score") + " " + interpret_score(score)[0], score
                )
            with col_changes:
                st.metric(self.t("bpm_change"), len(intervals) - 1)
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
                    title=self.t("bpm_dynamic"),
                    labels={"x": self.t("time") + " (s)", "y": "BPM"},
                )
                fig.update_traces(line=dict(color="#003399"))
                st.plotly_chart(fig)
            with st.expander(self.t("time_intervals")):
                data = {
                    "x": onset_times[1:],
                    "y": time_diffs,
                }
                fig = px.line(
                    data,
                    x="x",
                    y="y",
                    title=self.t("time_intervals_between_onsets"),
                    labels={
                        "x": self.t("time") + " (s)",
                        "y": self.t("time_between_onsets") + " (s)",
                    },
                )
                fig.update_traces(line=dict(color="#003399"))
                st.plotly_chart(fig)
            with st.expander(self.t("timings") + f" ({len(intervals)})"):
                data = {self.t("time"): [], "BPM": []}
                for start, bpm in intervals:
                    data[self.t("time")] += [f"{start:.3f}".replace(".", ",")]
                    data["BPM"] += [str(round(bpm, 2))]
                st.table(data)
        with nn:
            if sys.platform.startswith("win"):
                st.write("Available only on linux/macOS")
            else:
                trashold = 0
                nn_avg_bpm, nn_re_intervals = tempo.nn_re_intervals(
                    st.session_state.upload, trashold=trashold
                )
                confidence, nn_btmf_intervals = tempo.nn_btmf_intervals(
                    st.session_state.upload, trashold=trashold
                )
                nn_btmf_data = {self.t("time"): [], "BPM": []}
                for start, bpm in nn_btmf_intervals:
                    nn_btmf_data[self.t("time")] += [f"{start:.3f}".replace(".", ",")]
                    nn_btmf_data["BPM"] += [str(round(bpm, 2))]
                nn_re_data = {self.t("time"): [], "BPM": []}
                for start, bpm in nn_re_intervals:
                    nn_re_data[self.t("time")] += [f"{start:.3f}".replace(".", ",")]
                    nn_re_data["BPM"] += [str(round(bpm, 2))]
                st.write(confidence)
                st.write(nn_avg_bpm)
                btmf, re = st.columns(2)
                with btmf:
                    st.table(nn_btmf_data)
                with re:
                    st.table(nn_re_data)
        with beatmap:
            with st.container(border=True):
                if st.session_state.beatmap_upload is None:
                    st.subheader(self.t("download_beatmap"))
                    title, artist = st.columns(2)
                    with title:
                        st.text_input(
                            self.t("beatmap_title"),
                            value="ART title",
                            key="beatmap_title",
                        )
                    with artist:
                        st.text_input(
                            self.t("beatmap_artist"),
                            value="ART artist",
                            key="beatmap_artist",
                        )
                if st.session_state.beatmap_upload is None:
                    osu_name = f"{st.session_state.beatmap_artist} - {st.session_state.beatmap_title} (ART) [].osz"
                    st.download_button(
                        label=self.t("c_timings"),
                        data=osu_beatmap("c", intervals),
                        file_name=osu_name,
                        mime="application/zip",
                        key="download_new_beatmap",
                    )
                else:
                    st.download_button(
                        label=self.t("c_timings"),
                        data=insert_choise("c", intervals),
                        file_name=st.session_state.beatmap_upload.name,
                        mime=st.session_state.beatmap_upload.type,
                        key="download_uploaded_beatmap",
                    )
                if st.button(self.t("nn_timings"), key="nn_download"):
                    pass
        with general:
            col_info, col_image = st.columns(2, border=True)
            with col_info:
                std_dev = np.std(dynamic_bpm)
                if std_dev < 2:
                    rhythmic_variance = self.t("low")
                elif std_dev < 10:
                    rhythmic_variance = self.t("moderate")
                else:
                    rhythmic_variance = self.t("high")
                min_bpm = round(np.min(dynamic_bpm), 2)
                max_bpm = round(np.max(dynamic_bpm), 2)
                description = interpret_score(score)
                st.metric(self.t("complexity_score"), score)
                st.write(description)
                st.divider()
                st.write(f"{self.t('average')} BPM: {round(np.mean(dynamic_bpm), 2)}")
                st.divider()
                st.write(f"{self.t('bpm_range')}: {min_bpm} -> {max_bpm}")
                st.divider()
                st.write(f"{self.t('rhythmic_variance')}: {rhythmic_variance}")
            with col_image:
                cover_data = extract_cover(st.session_state.upload)
                if cover_data:
                    st.image(cover_data)
                else:
                    st.info(self.t("no_track_cover"))


def complexity_score(bpm_values, duration_sec, time_diffs):
    bpm_values = np.array(bpm_values)
    time_diffs = np.array(time_diffs)
    std_time = np.std(time_diffs)
    std_bpm = np.std(bpm_values)
    tempo_changes = np.sum(np.abs(np.diff(bpm_values)) > 3)
    change_rate = tempo_changes / duration_sec
    jitter = np.sum(np.diff(np.sign(np.diff(bpm_values))) != 0) / len(bpm_values)
    bpm_range = np.max(bpm_values) - np.min(bpm_values)
    acceleration = (bpm_values[-1] - bpm_values[0]) / duration_sec
    local_var = local_variability(bpm_values)
    score = (
        0.2 * std_time * 50
        + 0.2 * std_bpm
        + 0.2 * change_rate * 10
        + 0.15 * jitter * 10
        + 0.1 * bpm_range / 10
        + 0.1 * abs(acceleration)
        + 0.1 * local_var
    )
    return round(score, 2)


def local_variability(bpm_values, window_size=5):
    segments = len(bpm_values) // window_size
    local_std = [
        np.std(bpm_values[i * window_size : (i + 1) * window_size])
        for i in range(segments)
        if len(bpm_values[i * window_size : (i + 1) * window_size]) > 1
    ]
    return np.mean(local_std) if local_std else 0


def interpret_score(score):
    td = translation(st.session_state.get("language", "en"))
    if score < 3:
        return "🟢 " + td["very_simple"]
    elif score < 5:
        return "🟢🟡 " + td["simple_groove"]
    elif score < 7:
        return "🟡 " + td["moderately_complex"]
    elif score < 9:
        return "🟠 " + td["complex"]
    elif score < 11:
        return "🔴 " + td["highly_complex"]
    else:
        return "🔴🔴 " + td["ultra_complex"]


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
        click_freq=st.session_state.click_freq,
        click_duration=st.session_state.click_duration,
    )
    pbar.progress(100, "")
    return (
        dynamic_bpm,
        onset_times,
        onset_bpm,
        intervals,
        music_y,
        music_sr,
    )


def insert_choise(source, intervals):
    if source == "c":
        insert_timing_points(st.session_state.beatmap_upload, intervals)
        return st.session_state.beatmap_upload.getvalue()
    elif source == "nn":
        pass


def osu_beatmap(source, intervals):
    if source == "c":
        return create_beatmap(
            st.session_state.upload,
            st.session_state.beatmap_title,
            st.session_state.beatmap_artist,
            intervals,
        )
    elif source == "nn":
        pass
