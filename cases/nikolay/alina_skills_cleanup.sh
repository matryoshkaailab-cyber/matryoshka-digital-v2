#!/bin/bash
# ALINA pre-start hook — удаляет лишние skills при старте gateway
ALINA_SKILLS="/root/.hermes/profiles/alina/skills"
KEEP=(
    "card-rules" "hermes-image-workflow" "matryoshka-connection"
    "never-lose-context" "voice-transcription" "xkin-cards"
    "xkin-cards-tested-2026-06-16"
    ".bundled_manifest"
)
for entry in "$ALINA_SKILLS"/*; do
    [ -e "$entry" ] || continue
    name=$(basename "$entry")
    skip=0
    for k in "${KEEP[@]}"; do
        if [ "$name" = "$k" ]; then
            skip=1
            break
        fi
    done
    if [ $skip -eq 0 ]; then
        rm -rf "$entry" 2>/dev/null
    fi
done
