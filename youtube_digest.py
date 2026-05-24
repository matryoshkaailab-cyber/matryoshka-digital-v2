#!/usr/bin/env python3
"""
Daily YouTube Digest for MATRYOSHKA DIGITAL
Sends new video summaries to Telegram
"""

import subprocess
import re
import json
from datetime import datetime

CHANNEL_IDS = {
    "UCc-FovAyBAQDw2Y7PQ_v0Zw": "Julian Goldie SEO",
    "UCESLZhusAkFfsNsApnjF_Cg": "Lex Fridman",
    "UCbfYPyITQ-7l1X3Zy3K0A4A": "Two Minute Papers",
    "UCXUPKJOwMxn0jY7Y6fXkb0g": "Andrej Karpathy"
}

STATE_FILE = "/root/matryoshka/.youtube_state.json"

def get_latest_videos(channel_id, channel_name, max_results=3):
    """Get latest videos from channel"""
    result = subprocess.run(
        ['curl', '-s', f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'],
        capture_output=True, text=True, timeout=10
    )
    
    titles = re.findall(r'<media:title>([^<]+)</media:title>', result.stdout)
    video_ids = re.findall(r'<yt:videoId>([^<]+)</yt:videoId>', result.stdout)
    dates = re.findall(r'<published>([^<]+)</published>', result.stdout)
    
    videos = []
    for i in range(min(max_results, len(titles))):
        if i < len(video_ids):
            videos.append({
                'title': titles[i],
                'video_id': video_ids[i],
                'published': dates[i][:10] if i < len(dates) else None
            })
    
    return videos

def load_state():
    """Load processed video IDs"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    """Save processed video IDs"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def send_telegram(message):
    """Send message to Telegram"""
    token = "8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I"
    chat_id = "1951845052"  # Oleg
    
    subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://api.telegram.org/bot{token}/sendMessage',
        '-d', f'chat_id={chat_id}',
        '-d', f'text={message}'
    ], capture_output=True)

def main():
    state = load_state()
    new_videos = []
    
    for channel_id, channel_name in CHANNEL_IDS.items():
        videos = get_latest_videos(channel_id, channel_name)
        
        if channel_id not in state:
            state[channel_id] = []
        
        for video in videos:
            if video['video_id'] not in state[channel_id]:
                new_videos.append({
                    'channel': channel_name,
                    'title': video['title'],
                    'video_id': video['video_id'],
                    'published': video['published']
                })
                state[channel_id].append(video['video_id'])
    
    save_state(state)
    
    if new_videos:
        message = "📺 *YouTube Digest*\n\n"
        message += f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        for v in new_videos[:5]:
            message += f"▶️ *{v['channel']}*\n"
            message += f"   {v['title']}\n"
            message += f"   https://youtube.com/watch?v={v['video_id']}\n\n"
        
        send_telegram(message)
        print(f"Sent {len(new_videos)} new videos to Telegram")
    else:
        print("No new videos")

if __name__ == '__main__':
    main()
