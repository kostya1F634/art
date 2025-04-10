# ART - 🎶 dynamic BPM analyzer
ART provides a web interface to analyze dynamic BPM
* 📈 Charts of BPM
* ⚙️ A lot of parameters of BPM distribution
* 📝 Table of time intervals with BPM
* 📊 Table of time onsets with BPM
  
![image_app](https://github.com/user-attachments/assets/1a92dcd7-2fd7-40e8-8689-2e39293076ac)

## Requirements
* git
* python 3.13, 3.12, 3.11 (other versions most likely work but are not tested)
* uv
* make (Linux)
## Installation and Usage
### Linux
```shell
git clone https://github.com/kostya1F634/art.git
cd art
uv sync
make
```
### Windows
```shell
git clone https://github.com/kostya1F634/art.git
cd art
uv sync
uv run streamlit run .\art\app.py
```
### Remarks
* The first run may be slow due to caching or something else from librosa and streamlit
