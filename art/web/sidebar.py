from web.translation import translation
import streamlit as st


class Sidebar:
    def __init__(self):
        self.td = translation(st.session_state.get("language", "en"))

    def t(self, key):
        return f"{self.td[key]}"

    def render(self):
        st.sidebar.subheader(self.t("settings"), divider="grey")
        st.sidebar.selectbox(
            self.t("select_language"),
            options=["en", "ru"],
            index=["en", "ru"].index(st.session_state.get("language", "en")),
            key="language",
        )
        st.sidebar.toggle(
            'Turn on "Classic method"',
            value=False,
            help='Turn on "Classic method"',
            key="classic_on",
        )
        st.sidebar.number_input(
            self.t("sample_rate"),
            value=44100,
            help=self.t("sample_rate"),
            min_value=44100,
            step=10000,
            key="sample_rate",
        )
        if (
            st.session_state.get("upload", None) is None
            or not st.session_state.classic_on
        ):
            return

        st.sidebar.subheader(self.t("parameters"), divider="grey")
        st.sidebar.number_input(
            self.t("hop_length"),
            value=1024,
            help=self.t("hop_length_help"),
            min_value=1,
            step=50,
            key="hop_length",
        )
        st.sidebar.number_input(
            self.t("acw"),
            value=20.0,
            help=self.t("acwh"),
            step=1.0,
            key="ac_size",
        )
        st.sidebar.number_input(
            self.t("standard_bpm"),
            value=1.0,
            help=self.t("standard_bpm_help"),
            step=0.1,
            key="standard_bpm",
        )
        st.sidebar.toggle(
            self.t("two"),
            value=True,
            help=self.t("twoh"),
            key="trim",
        )
        st.sidebar.subheader(self.t("music"), divider="grey")
        st.sidebar.slider(
            self.t("volume"),
            value=20,
            help=self.t("volume_help"),
            key="volume",
        )
        st.sidebar.number_input(
            self.t("click_frequency"),
            value=350.0,
            help=self.t("click_frequency_help"),
            step=10.0,
            key="click_freq",
        )
        st.sidebar.number_input(
            self.t("click_duration"),
            value=0.1,
            help=self.t("click_duration_help"),
            key="click_duration",
        )
        st.sidebar.subheader(self.t("advanced_parameters"), divider="grey")
        st.sidebar.number_input(
            self.t("start_bpm"),
            value=120.0,
            help=self.t("start_bpm_help"),
            step=10.0,
            key="start_bpm",
        )
        st.sidebar.number_input(
            self.t("max_bpm"),
            value=320.0,
            help=self.t("max_bpm_help"),
            step=10.0,
            key="max_bpm",
        )
        st.sidebar.number_input(
            self.t("tightness"),
            value=100.0,
            help=self.t("tightness_help"),
            step=100.0,
            key="tightness",
        )
