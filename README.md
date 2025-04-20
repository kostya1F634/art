![art_logo](https://github.com/user-attachments/assets/e88ee84a-7c6c-451c-89f9-63aaec99b59d)
# ART - 🎶 dynamic BPM analyzer
ART provides a web interface to analyze dynamic BPM and export beatmaps with it
* 🤖 Automatic find timings (beats and BPM) with "Classic" and "Neural network" methods
* ⬇️ Download beatmap already with timings or insert it in your beatmap
* 📥 Add timings in your beatmap
* 📈 Charts of BPM

![app_main_page_image](https://github.com/user-attachments/assets/71d25870-0f41-4e1c-8810-8f2f77e949b3)

## Requirements
* ffmpeg (linux and neural network)
* git
* uv
* make (not necessary)
## Installation and Usage
### Linux
```shell
git clone https://github.com/kostya1F634/art.git
cd art
uv sync
# Usage
make
# or
uv run streamlit run art/app.py
```
### Windows
```shell
git clone https://github.com/kostya1F634/art.git
cd art
uv sync
# Usage
uv run streamlit run .\art\app.py
```
### Important
* this should be done before placing the objects
* upload audio, adjust the parameters
* dowload beatmap in "Beatmap" tab
* load to OSU!
* mapping
### Remarks
* The first run may be slow due to caching or something else from librosa and streamlit
