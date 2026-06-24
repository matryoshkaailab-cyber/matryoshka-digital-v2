#!/bin/bash
# ALINA Skills Loop Watchdog — чистит каждые 30 сек, 5 минут
ALINA_SKILLS="/root/.hermes/profiles/alina/skills"
KEEP="card-rules hermes-image-workflow matryoshka-connection never-lose-context voice-transcription xkin-cards xkin-cards-tested-2026-06-16 .bundled_manifest"
END=$((SECONDS+300))
while [ $SECONDS -lt $END ]; do
    for entry in "$ALINA_SKILLS"/*; do
        [ -e "$entry" ] || continue
        name=$(basename "$entry")
        skip=0
        for k in $KEEP; do
            [ "$name" = "$k" ] && skip=1 && break
        done
        [ $skip -eq 0 ] && rm -rf "$entry" 2>/dev/null
    done
    sleep 30
done
