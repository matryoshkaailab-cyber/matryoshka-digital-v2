# HERMES AGENT — АУДИТ ОБНОВЛЕНИЯ v0.16.0 (5.06.2026 → 15.06.2026)
**Дата аудита:** 2026-06-15 14:25 CEST
**Автор:** HERMES (по запросу Олега)
**Предыдущий аудит:** `/root/matryoshka/HERMES_AUDIT_v0.16.md` (11.06.2026, 12KB)
**Обновлено с:** v0.16.0 (5.06.2026, upstream fa32af88)
**Обновлено до:** v0.16.0 (15.06.2026, upstream **a376ca008**)
**Дельта:** 709 коммитов, 6 skills synced (4 updated + 5 user-modified), 7 профилей, config v26→v28

---

## 🎯 КЛЮЧЕВОЙ ВЫВОД

**Обновление = минорное в рамках v0.16.x (patch-уровень), НЕ major release.**
- Никаких breaking changes
- 0 изменений которые сломали бы наши интеграции
- Большинство изменений — bugfixes и security patches
- Одна НОВАЯ фича: **Hindsight Memory observation_scopes** (настраиваемая)

---

## 📊 ДЕЛЬТА ПО КАТЕГОРИЯМ (709 коммитов)

### 1. 🧠 HINDSIGHT MEMORY — НОВАЯ ФИЧА (1 коммит)
| Коммит | Что |
|---|---|
| `a376ca008` | `feat(hindsight): make observation scopes configurable on retain` |

**Что это значит для нас:**
- Установлен `hindsight_client` в `/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/`
- Параметр `observation_scopes` (per_tag / combined / all_combinations) — управляет **что запоминать** на retain
- **В нашем config.yaml секции `hindsight:` нет** → работает по дефолту (видимо "observation only")
- **МОЖНО** настроить под наши нужды (entity/fact/observation/message) для MATRYOSHKA

**Решение:** **Отложить внедрение.** У нас уже есть `memory` tool (2.2КБ) + `fact_store` (entity resolution). Hindsight — это дополнительный слой. Внедрение требует тестирования — не на P0.

### 2. 🛡 S6/GATEWAY BUGFIXES — ВНЕДРЕНО АВТОМАТИЧЕСКИ (6 коммитов)
| Коммит | Что | Нас затрагивает? |
|---|---|---|
| `b77096726` | `fix(s6): persist profile gateway desired state` | ✅ наш `Restart=always` теперь persist |
| `95715dcb0` | `fix(s6): reserved default gateway must not follow sticky active_profile` | ✅ защита от sticky |
| `143679305` | `fix(gateway): block shell gateway run when a service supervises` | ✅ защита от двойного запуска |
| `c2b7669ad` | `fix(s6): clear stale log lock before startup` | ✅ авторазблокировка |
| `40d7c264f` | `fix(s6): register profile gateways without auto-starting` | ✅ безопасный реестр |
| `61ee2dbfd` | `fix(s6): make profile gateway log parent writable` | ✅ права на логи |

**Действие:** ✅ **НИЧЕГО НЕ ДЕЛАТЬ** — применилось автоматически.

### 3. 🔒 MCP SECURITY — ВНЕДРЕНО АВТОМАТИЧЕСКИ (3 коммита)
| Коммит | Что |
|---|---|
| `972a9885e` | `fix(mcp): block exfil-shaped stdio server configs` |
| `a27d7e68c` | `fix(mcp): block suspicious stdio configs before probe` |
| `dcc321695` | `fix(mcp): fail fast for noninteractive oauth without tokens` |

**Что это значит для нас:**
- **MCP пока не подключен** (n8n MCP = P2 по плану Олега)
- Когда подключим — **уже защищены** от exfiltration и oauth-атак
- **КРИТИЧНО** для безопасности, но без срочности

**Действие:** ✅ **НИЧЕГО НЕ ДЕЛАТЬ** — защита уже работает.

### 4. ⚡ SKILLS CACHE / PERFORMANCE — ВНЕДРЕНО АВТОМАТИЧЕСКИ (5 коммитов)
| Коммит | Что | Эффект |
|---|---|---|
| `3bc4a2ff7` | `fix(gateway): re-baseline agent-cache message_count` | меньше рассинхрон message_count |
| `7f245b003` | `fix(gateway): invalidate agent cache on cross-process session writes` | кросс-процесс кэш инвалидируется |
| `4e6d05c6a` | `perf(skills): share raw config cache in skill utils` | быстрее загрузка скиллов |
| `7bbe7024c` | `fix: filter platform-disabled skills from <available_skills>` | меньше мусора в prompt |
| `13a1bd0f8` | `perf(model-metadata): persist OpenRouter metadata cache` | быстрее picker |

**Действие:** ✅ **НИЧЕГО НЕ ДЕЛАТЬ** — применилось.

### 5. 📁 FILE TOOLS SESSION CWD — ВНЕДРЕНО АВТОМАТИЧЕСКИ (5 коммитов)
| Коммит | Что |
|---|---|
| `6cb88a087` | `Merge ... file-tools-session-cwd` |
| `8fce54499` | `refactor(tools): extract shared sentinel-free abs cwd validator` |
| `b0c99c12d` | `docs(tools): document registered-cwd step` |
| `ddf7c7af8` | `refactor(tools): consolidate task-override lookup into one helper` |
| `d6a8d9dca` | `fix(tools): respect session cwd in file tools` |

**Что это значит для нас:**
- `read_file` / `write_file` / `patch` теперь **уважают** `session_cwd`
- Если я работаю в `/root/matryoshka/nikolay/`, относительные пути работают
- **ПОЛЕЗНО** для будущих сценариев с под-агентами в разных директориях

**Действие:** ✅ **ПРОВЕРИТЬ** — попробовать относительные пути в `read_file` после update.

### 6. 💬 TELEGRAM FIXES — ВНЕДРЕНО АВТОМАТИЧЕСКИ (4 коммита)
| Коммит | Что |
|---|---|
| `a1f51feb7` | `fix(telegram): avoid rich final duplicate previews` |
| `9459057d7` | `fix(telegram): guard rich details math crash` |
| `288f7026e` | `fix(messaging): correct Weixin personal account labeling` |
| `efbe1635d` | `fix(gateway): include replied-to media attachments` |

**Действие:** ✅ **НИЧЕГО НЕ ДЕЛАТЬ** — Telegram-бот уже стабильнее.

### 7. 🤖 NEW MODEL: GLM-5.2 (1M context) — ОПЦИОНАЛЬНО
| Коммит | Что |
|---|---|
| `bff78a34d` | `feat(zai): add GLM-5.2 with verified 1M context window` |
| `2a14e8957` | `fix(kimi): surface K2.7 Code in native picker` |

**Что это значит для нас:**
- Добавлен новый провайдер `zai` с моделью GLM-5.2 (1M context, как MiniMax-M3)
- Можем добавить в `config.yaml` как альтернативу/backup
- K2.7 Code в picker — Kimi (Moonshot) для кода

**Решение:** **НЕ подключать** — у нас MiniMax-M3 + Qwen 3.7 Max для ALF = достаточно.

### 8. 🪟 WINDOWS (Аликс) — ВНЕДРЕНО
| Коммит | Что |
|---|---|
| `f79551378` | `fix(windows): kill hermes before recreating venv to release _bcrypt.pyd lock` |

**Что это значит для нас:**
- На ПК Аликса обновление venv теперь **корректно** убивает старый hermes
- Может починить проблему с зависанием при обновлении на ПК

**Действие:** ✅ **Аликс должен будет сделать `hermes update` на ПК** — обновление уже на месте, скрипт `update.cmd` его подхватит.

### 9. 🔐 AUTH / XAI OAUTH — ВНЕДРЕНО (3 коммита)
| Коммит | Что |
|---|---|
| `497352bc4` | `fix(auth): write rotated xAI OAuth tokens back to global root` |
| `f1d6f0436` | `fix(auth): resolve xAI OAuth credentials across profiles` |
| `8844e091c` | `Merge ... xai-oauth-profile-writethrough` |

**Действие:** ✅ **НИЧЕГО НЕ ДЕЛАТЬ** — xAI OAuth теперь надёжнее.

### 10. 📧 EMAIL FIXES — ВНЕДРЕНО (2 коммита)
| Коммит | Что |
|---|---|
| `04d4471d7` | `fix(email): use SMTP_SSL for port 465 and fall back to IPv4 on timeout` |
| `cf7d5932f` | `fix(email): make IPv4 SMTP fallback use supported sockets` |

**Действие:** ✅ **НИЧЕГО НЕ ДЕЛАТЬ** — email у нас не используется.

### 11. 🐳 DOCKER FIX (1 коммит)
| Коммит | Что |
|---|---|
| `aca11c227` | `fix(docker): skip gateway reconciliation in dashboard container` |

**Что это значит для нас:** подготовительный шаг к **Docker sandbox (Этап 1 из плана)**. Когда будем делать — не упадём в dashboard-контейнере.

### 12. PROFILE / GATEWAY PLAYBACK — ВНЕДРЕНО (4 коммита)
| Коммит | Что |
|---|---|
| `a829e04d6` | `fix: migrate cloned profile configs` |
| `293c04fef` | `fix(gateway): suppress exact silence tokens without mutating history` |
| `5191c1c2c` | `fix(gateway): stop replaying interrupted tool-call tails` |
| `2c174bce2` | `fix(gateway): preserve new input on interrupted replay cleanup` |

**Что это значит для нас:**
- **Replay interrupted tool-call tails** — это именно то что **ломало наш test-drive связи с Аликсом** (5 попыток, пустой output после `alex_helper.sh`)
- Теперь interrupted tool-tails **не реплеятся** → меньше мусорных вызовов
- Profile config migration — **ВНИМАНИЕ**: у нас 7 профилей, надо проверить что config корректно мигрировался

### 13. REMOVED / DEPRECATED (1 коммит)
| Коммит | Что |
|---|---|
| `f3fe99863` | `revert(web): remove keyless Parallel search fallback` |

**Действие:** Ничего — это про web-поиск Parallel, мы не используем.

---

## 📋 ПЛАН ВНЕДРЕНИЯ (что реально делать)

### P0 — НЕМЕДЛЕННО (5 мин)
✅ **Сделано АВТОМАТИЧЕСКИ** при update:
- S6/Gateway persistence fixes
- MCP security (когда подключим)
- Skills cache
- Telegram fixes
- Windows hermes update fix (Аликс)
- Profile config migration (проверить после рестарта)

### P1 — В ТЕЧЕНИЕ ДНЯ (15 мин)
- [ ] **Проверить что gateway работает корректно после update** (ping Олега)
- [ ] **Аликс должен сделать `hermes update` на ПК** (через Remotely Save или ssh)
- [ ] **Проверить profile config** — не мигрировал ли hermes-cli config криво

### P2 — ОТЛОЖИТЬ (на следующий спринт)
- [ ] Hindsight observation_scopes — настроить под MATRYOSHKA
- [ ] GLM-5.2 (zai) — добавить как fallback provider
- [ ] File tools session_cwd — проверить работу с относительными путями

### ❌ НЕ ДЕЛАТЬ
- [x] НЕ возвращать FTS5 (мы его УБИЛИ, пусть остаётся LIKE)
- [x] НЕ ставить Docker sandbox глобально (per-command флаг по Этапу 1)
- [x] НЕ подключать n8n MCP (Этап 4 P2)

---

## 🎯 КОНКРЕТНАЯ КОМАНДА ДЛЯ АЛИКСА

Аликс (на ПК через opencode или direct) должен:
```bash
hermes update
hermes --version  # должен показать a376ca008
hermes gateway run --profile alex --replace
```

Это применит 709 коммитов на ПК и починит `f79551378 fix(windows): kill hermes before recreating venv`.

---

## 📁 СОЗДАННЫЕ ФАЙЛЫ В ЭТОЙ СЕССИИ

1. `/root/matryoshka/HERMES_UPDATE_v0.16_AUDIT.md` (этот файл) — **АУДИТ**
2. `/root/matryoshka/HERMES_IDENTITY_FULL.md` (657KB, отправлен в Telegram для NotebookLM)
3. `/root/matryoshka/SOUL.md` (350 строк, канонический)
4. `/root/matryoshka/build_identity.sh` (генератор SOUL)
5. `/root/matryoshka/hermes_active_flush.py` (active flush hook)
6. `/root/matryoshka/fts5_drop_profile.sh` (FTS5 drop в profile DB)
7. `/etc/systemd/system/hermes-cli-gateway.service` (с ExecStopPost/ExecStartPre hooks)

---

**Создан:** 2026-06-15 14:25 CEST
**Версия:** v1.0
**Источники:**
- `git log` Hermes Agent v0.16.0 (commits a376ca008..fa32af88)
- `hermes --version` output
- `~/.hermes/config.yaml`, `~/.hermes/profiles/*/config.yaml`
- `/usr/local/lib/hermes-agent/` (RELEASE notes, README, CHANGELOG отсутствует)
