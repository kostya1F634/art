from web.translation import translation
from web.utils import extract_cover
import tempo
import pyperclip
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import entropy
from scipy.stats import mode
from scipy.signal import savgol_filter


class Dashboard:
    def __init__(self):
        self.td = translation(st.session_state.get("language", "en"))

    def t(self, key):
        return f"{self.td[key]}"

    def render(self):
        st.title(self.t("title"))
        st.subheader(self.t("subtitle"))
        if st.session_state.get("upload", None) is not None:
            (
                dynamic_bpm,
                onset_times,
                onset_bpm,
                intervals,
                music_y,
                music_sr,
            ) = audio_processing()
        else:
            with st.container(border=True):
                st.file_uploader(
                    self.t("choose_file"),
                    type=["wav", "mp3", "flac", "ogg", "m4a", "wma", "aiff", "aif"],
                    key="upload",
                )
            return
        with st.container(border=True):
            st.file_uploader(
                self.t("choose_file"),
                type=["wav", "mp3", "flac", "ogg", "m4a", "wma", "aiff", "aif"],
                key="upload",
            )
            st.write(self.t("audio_clicks"))
            st.audio(music_y, sample_rate=music_sr)
        twod_plot, threed_plot, nn, intervals_tab, onset_and_bpm, general = st.tabs(
            [
                self.t("twod_plot"),
                self.t("threed_plot"),
                self.t("nn"),
                self.t("intervals"),
                self.t("onset_and_bpm"),
                self.t("overview"),
            ]
        )
        with twod_plot:
            time_diffs = np.diff(onset_times)
            time_diffs = trim_middle(
                time_diffs, trim_percent=st.session_state.time_blowout / 100
            )
            score = complexity_score(dynamic_bpm, intervals[-1][1], time_diffs)
            col_average, col_onset, col_score = st.columns(3, border=True)
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
            with st.container(border=True):
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
            with st.container(border=True):
                smoothed_y = smooth_data(
                    time_diffs, window_size=st.session_state.window_size
                )
                fig = px.line(
                    x=onset_times[1:][len(onset_times[1:]) - len(smoothed_y) :],
                    y=smoothed_y,
                    title=self.t("time_intervals_between_onsets_smooth"),
                    labels={
                        "x": self.t("time") + " (s)",
                        "y": self.t("time_between_onsets") + " (s)",
                    },
                )
                fig.update_layout(
                    xaxis=dict(showgrid=True),
                    yaxis=dict(
                        showgrid=True,
                        range=[min(smoothed_y) - 0.1, max(smoothed_y) + 0.1],
                    ),
                    title=self.t("time_intervals_between_onsets_smooth"),
                )
                fig.update_traces(line=dict(color="#003399"))
                st.plotly_chart(fig)
        with threed_plot:
            with st.container(border=True):
                x = np.array(onset_times)
                y = np.array(onset_bpm)
                z = np.diff(x, prepend=x[0])

                fig = go.Figure(
                    data=[
                        go.Scatter3d(
                            x=x,
                            y=y,
                            z=z,
                            mode="lines+markers",
                            marker=dict(size=4, color=z, colorscale="Viridis"),
                            line=dict(color="royalblue", width=2),
                        )
                    ]
                )

                fig.update_layout(
                    scene=dict(
                        xaxis_title=self.t("time") + " (s)",
                        yaxis_title="BPM",
                        zaxis_title=self.t("intervals") + " (s)",
                    ),
                    title=self.t("three_plot"),
                    margin=dict(l=0, r=0, b=0, t=30),
                )
                st.plotly_chart(fig)
        with intervals_tab:
            timing_points_string = timing_points(intervals)
            with st.expander(self.t("intervals_format")):
                st.text(timing_points_string)
            if st.button(self.t("copy"), key="intervals_copy"):
                pyperclip.copy(timing_points_string)
            data = {self.t("start"): [], self.t("end"): [], "BPM": []}
            for start, end, bpm in intervals:
                data[self.t("start")] += [f"{start:.3f}".replace(".", ",")]
                data[self.t("end")] += [f"{end:.3f}".replace(".", ",")]
                data["BPM"] += [str(round(bpm, 2))]
            st.table(data)
        with onset_and_bpm:
            beat_timing_points_string = beat_timing_points(onset_times, onset_bpm)
            with st.expander(self.t("beats_format")):
                st.text(beat_timing_points_string)
            if st.button(self.t("copy"), key="beats_copy"):
                pyperclip.copy(beat_timing_points_string)
            onset_bpm_table = {f"{self.t('onset')} (s)": [], "BPM": []}
            for time, bpm in zip(onset_times, onset_bpm):
                onset_bpm_table[f"{self.t('onset')} (s)"] += [
                    str(round(time, 3)).replace(".", ",")
                ]
                onset_bpm_table["BPM"] += [str(round(bpm, 2))]
            st.table(onset_bpm_table)
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
        with nn:
            st.write("In development")


def trim_middle(x, trim_percent=0.25):
    if trim_percent <= 0.0:
        return x
    x = np.array(x, dtype=float)
    lower = np.percentile(x, 100 * trim_percent)
    upper = np.percentile(x, 100 * (1 - trim_percent))
    mask = (x >= lower) & (x <= upper)
    if np.any(mask):
        most_common = mode(x[mask], keepdims=True).mode[0]
    else:
        most_common = np.mean(x)
    x[~mask] = most_common
    return x


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
    entropy_val = bpm_entropy(bpm_values)
    score = (
        0.2 * std_time * 50
        + 0.2 * std_bpm
        + 0.2 * change_rate * 10
        + 0.15 * jitter * 10
        + 0.1 * bpm_range / 10
        + 0.1 * abs(acceleration)
        + 0.1 * local_var
        + 0.1 * entropy_val * 10
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


def bpm_entropy(bpm_values):
    hist, _ = np.histogram(bpm_values, bins=10, density=True)
    return entropy(hist)


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
    onset_bpm = trim_middle(onset_bpm, trim_percent=st.session_state.blowout / 100)
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


def smooth_data(data, window_size=5):
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")


def timing_points(intervals):
    result = []
    for interval in intervals:
        start, end, bpm = interval
        start_ms = int(start * 1000)
        beat_length = 60000 / bpm
        result.append(f"{start_ms},{beat_length},4,1,0,100,1,0")
    return "\n".join(result)


def beat_timing_points(beat_times, beat_bpm):
    result = []
    for time, bpm in zip(beat_times, beat_bpm):
        start_ms = int(time * 1000)
        beat_length = 60000 / bpm
        result.append(f"{start_ms},{beat_length},4,1,0,100,1,0")
    return "\n".join(result)
