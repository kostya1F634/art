from web.translation import translation
import streamlit as st


class Sidebar:
    def __init__(self):
        self.td = translation(st.session_state.get("language", "en"))

    def t(self, key):
        return f"{self.td[key]}"

    def render(self):
        st.subheader(self.t("settings"), divider="grey")
        st.selectbox(
            self.t("select_language"),
            options=["en", "ru"],
            index=["en", "ru"].index(st.session_state.get("language", "en")),
            key="language",
        )
        if st.session_state.get("upload", None) is None:
            return
        c_tab, nn_tab = st.tabs(["Classic params", "Neural network params"])
        with c_tab:
            self.c_render()
        with nn_tab:
            self.nn_render()

    def nn_render(self):
        pass

    def c_render(self):
        st.subheader(self.t("parameters"), divider="grey")
        st.number_input(
            self.t("sample_rate"),
            value=100000,
            help=self.t("sample_rate"),
            min_value=250,
            step=10000,
            key="sample_rate",
        )
        st.number_input(
            self.t("hop_length"),
            value=1024,
            help=self.t("hop_length_help"),
            min_value=1,
            step=50,
            key="hop_length",
        )
        st.number_input(
            self.t("acw"),
            value=20.0,
            help=self.t("acwh"),
            step=1.0,
            key="ac_size",
        )
        st.number_input(
            self.t("standard_bpm"),
            value=1.0,
            help=self.t("standard_bpm_help"),
            step=0.1,
            key="standard_bpm",
        )
        st.toggle(
            self.t("two"),
            value=True,
            help=self.t("twoh"),
            key="trim",
        )
        st.subheader(self.t("music"), divider="grey")
        st.slider(
            self.t("volume"),
            value=20,
            help=self.t("volume_help"),
            key="volume",
        )
        st.number_input(
            self.t("click_frequency"),
            value=350.0,
            help=self.t("click_frequency_help"),
            step=10.0,
            key="click_freq",
        )
        st.number_input(
            self.t("click_duration"),
            value=0.1,
            help=self.t("click_duration_help"),
            key="click_duration",
        )
        st.subheader(self.t("advanced_parameters"), divider="grey")
        st.number_input(
            self.t("start_bpm"),
            value=120.0,
            help=self.t("start_bpm_help"),
            step=10.0,
            key="start_bpm",
        )
        st.number_input(
            self.t("max_bpm"),
            value=320.0,
            help=self.t("max_bpm_help"),
            step=10.0,
            key="max_bpm",
        )
        st.number_input(
            self.t("tightness"),
            value=100.0,
            help=self.t("tightness_help"),
            step=100.0,
            key="tightness",
        )
