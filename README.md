![art_logo](https://github.com/user-attachments/assets/e88ee84a-7c6c-451c-89f9-63aaec99b59d)
# ART - 🎶 dynamic BPM analyzer
ART provides a web interface to analyze dynamic BPM
* 🤖 Automatic find timings (beats and BPM)
* ⬇️ Download beatmap already with timings or insert it in your beatmap
* 📈 Charts of BPM
* ⚙️ A lot of parameters of BPM distribution
* 📊 Table of time intervals with BPM

![image_app](https://github.com/user-attachments/assets/1a92dcd7-2fd7-40e8-8689-2e39293076ac)
![app_intervals_image](https://github.com/user-attachments/assets/5da21034-0784-4c47-88be-04aa8232d2a4)

## Requirements
* git
* python 3.10-3.13 (not necessary because uv install python itself, I guess)
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
