"""Fetch and save YouTube video transcripts to a text file.

Uses the youtube-transcript-api library to retrieve auto-generated or
manually-created captions from YouTube videos and writes them to a local file.
"""

from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

# This is the ID in the video URL
VIDEO_ID = 'sa-ASdF1234'

transcript_list = ytt_api.list(VIDEO_ID)

transcripts = [x for x in transcript_list]
transcript = transcripts[0] if len(transcripts) == 1 else None
if transcript is not None:
    my_ts = transcript.fetch()
    my_ts_l = my_ts.to_raw_data()
    with open("video_transcript.txt", "w") as f:
        f.write(' '.join([x['text'] for x in my_ts_l]))
