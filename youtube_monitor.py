#!/usr/bin/env python3
"""
YouTube Channel Monitor for MATRYOSHKA DIGITAL
Monitors AI/SEO/Marketing channels and extracts insights
"""

import subprocess
import re
import json
from datetime import datetime

# Channels to monitor
CHANNELS = {
    "julian_goldie": {
        "name": "Julian Goldie SEO",
        "url": "https://www.youtube.com/@JulianGoldieSEO",
        "channel_id": "UCc-FovAyBAQDw2Y7PQ_v0Zw"
    },
    "lex_fridman": {
        "name": "Lex Fridman", 
        "url": "https://www.youtube.com/@LexFridman",
        "channel_id": "UCESLZhusAkFfsNsApnjF_Cg"
    },
    "andrej_karpathy": {
        "name": "Andrej Karpathy",
        "url": "https://www.youtube.com/@AndrejKarpathy",
        "channel_id": "UCXUPKJOwMxn0 jY7Y6fXkb0g"
    },
    "two_minute_papers": {
        "name": "Two Minute Papers",
        "url": "https://www.youtube.com/@TwoMinutePapers",
        "channel_id": "UCbfYPyITQ-7l1X3Zy3K0A4A"
    }
}

def get_rss_feed(channel_id):
    """Fetch RSS feed for a channel"""
    result = subprocess.run(
        ['curl', '-s', f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'],
        capture_output=True, text=True, timeout=10
    )
    
    titles = re.findall(r'<media:title>([^<]+)</media:title>', result.stdout)
    video_ids = re.findall(r'<yt:videoId>([^<]+)</yt:videoId>', result.stdout)
    dates = re.findall(r'<published>([^<]+)</published>', result.stdout)
    
    videos = []
    for i in range(min(5, len(titles))):
        videos.append({
            'title': titles[i],
            'video_id': video_ids[i] if i < len(video_ids) else None,
            'published': dates[i][:10] if i < len(dates) else None
        })
    
    return videos

def get_transcript(video_id):
    """Get transcript of a video"""
    try:
        result = subprocess.run(
            ['/usr/bin/python3', '-c', f'''
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch("{video_id}")
text = ""
for t in transcript:
    text += t.text + " "
print(text)
'''],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout if result.returncode == 0 else None
    except:
        return None

def check_new_videos():
    """Check for new videos and return summary"""
    results = {}
    
    for key, channel in CHANNELS.items():
        videos = get_rss_feed(channel['channel_id'])
        results[key] = {
            'name': channel['name'],
            'videos': videos
        }
    
    return results

if __name__ == '__main__':
    print("📺 YouTube Monitor - MATRYOSHKA DIGITAL")
    print("="*50)
    
    data = check_new_videos()
    
    for key, channel in data.items():
        print(f"\n📌 {channel['name']}")
        print("-"*40)
        for i, video in enumerate(channel['videos'][:3]):
            print(f"  {i+1}. {video['title']}")
            print(f"     {video['published']} | {video['video_id']}")
    
    print("\n✅ Monitor check complete")
