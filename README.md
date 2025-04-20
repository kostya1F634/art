![art_logo](https://github.com/user-attachments/assets/e88ee84a-7c6c-451c-89f9-63aaec99b59d)
# ART - 🎶 dynamic BPM analyzer
ART provides a web interface to analyze dynamic BPM and export beatmaps with it
* 🤖 Automatic find timings (beats and BPM) with "Classic" and "Neural network" methods
* ⬇️ Download beatmap already with timings or insert it in your beatmap
* 📥 Add timings in your beatmap
* 📈 Charts of BPM

![nn_app_image](https://github.com/user-attachments/assets/571314b9-325a-4a9f-ac81-241c1c54a934)
![art_main_page_image](https://github.com/user-attachments/assets/4ea27e86-4c06-4ec3-9ca4-0d1286221496)
![art_download_beatmap_image](https://github.com/user-attachments/assets/a4834968-cb7f-4a25-b80d-74bb69d214e1)

## Requirements
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
* open map in external editing
* paste the copied TimingPoints into the appropriate section
* mapping
### Remarks
* The first run may be slow due to caching or something else from librosa and streamlit
