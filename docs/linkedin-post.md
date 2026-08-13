# LinkedIn post — private local transcription utility

Published LinkedIn post copy and accompanying images for the `mp4-to-transcript` project.

## Images

- [Tūī video-to-text graphic](../assets/mp4-to-transcript-linkedin-tui-video.png) — final image used for the post.
- [Tūī transcript graphic](../assets/mp4-to-transcript-linkedin-tui.png) — earlier version.
- [Private transcription workflow](../assets/mp4-to-transcript-linkedin.png) — earlier version.

## Post copy

I needed to transcribe nine videos all over 30 mins long.

Rather than pay the US$10 from an online service I used the whisper model and with my codex friend we built a small, private, CPU-only MP4 transcription service (Using the whisper model) for turning video into transcripts on my T480 AI lab machine using Docker.

The transcripts are to be used as knowledge for a RAG system.

It produces Markdown, VTT, SRT, JSON segments, and an audit record, while keeping videos off cloud services i.e. free ish.

Its just a utility I can spin up when I need to do this sort of work in the future.

From a Customer Success perspective, this small experiment shows that when we stumble across a problem with a workflow we can create a simple solution to keep us moving.

Not everything has to be Enterprise level quality.

Time taken: 180 minutes  
Reuseable: Yes  
Open source: https://lnkd.in/gVhPN5Bh

#AIEngineering #Whisper #Privacy #OpenSource #LocalAI #customersuccess #Fractional #HeadofCustomersuccess
