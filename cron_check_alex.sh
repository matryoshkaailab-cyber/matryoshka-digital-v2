[ -f /root/matryoshka/alex_tasks/2026-06-08_1205_audit_fixes.md ] && [ ! -f /tmp/alex_answer_sent_1205 ] && {
  SIZE=$(stat -c%s /root/matryoshka/alex_tasks/2026-06-08_1205_audit_fixes.md)
  if [ "$SIZE" -gt 100 ]; then
    touch /tmp/alex_answer_sent_1205
    TOK=$(grep "^TELEGRAM_BOT_TOKEN=" /root/.hermes/.env | head -1 | cut -d= -f2)
    curl -s -X POST "https://api.telegram.org/bot${TOK}/sendMessage" -d chat_id=1951845052 --data-urlencode "text=ALEX ANSWERED audit. File size: ${SIZE} bytes" > /tmp/c1.log 2>&1
    curl -s -X POST "https://api.telegram.org/bot${TOK}/sendDocument" -F chat_id=1951845052 -F document=@/root/matryoshka/alex_tasks/2026-06-08_1205_audit_fixes.md > /tmp/c2.log 2>&1
  fi
}
exit 0
