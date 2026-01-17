# YouTube Transcript Downloader

Fetch transcripts from YouTube videos and save them to a text file.

## Installation

```bash
# Using pip
pip install -r requirements.txt

# Using uv
uv pip install -r requirements.txt
```

## Usage

1. Edit `example.py` and set `VIDEO_ID` to your YouTube video ID (the part after `v=` in the URL)
2. Run `python example.py` (or with uv, `uv run python example.py`)
3. The transcript will be saved to `video_transcript.txt`
