#!/usr/bin/env python3
"""
STT через faster-whisper — для голосовых Telegram (.ogg).
Заменяет сломанный openai-whisper (torch без CUDA libs).

Использование:
  ./transcribe.py <audio.ogg> [model]
  ./transcribe.py /root/.hermes/profiles/alf/audio_cache/*.ogg base

По умолчанию: model=base, language=ru, vad_filter=True.
~20 сек для 30-сек голосового на CPU.
"""
import sys
from faster_whisper import WhisperModel

if len(sys.argv) < 2:
    print("Usage: transcribe.py <audio.ogg|-> [model]", file=sys.stderr)
    sys.exit(1)

audio = sys.argv[1]
model_name = sys.argv[2] if len(sys.argv) > 2 else "base"

print(f"[STT] model={model_name} file={audio}", file=sys.stderr)

model = WhisperModel(model_name, device="cpu", compute_type="int8")
segments, info = model.transcribe(
    audio,
    language="ru",
    beam_size=5,
    vad_filter=True,
)

text = " ".join(s.text for s in segments)
print(text)
print(f"[STT] lang={info.language} prob={info.language_probability:.2f}", file=sys.stderr)