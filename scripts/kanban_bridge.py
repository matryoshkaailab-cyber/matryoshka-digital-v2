#!/usr/bin/env python3
"""kanban_bridge.py — Kanban ↔ ALEX мост для HERMES
Запускается HERMES (или cron) для конвертации alex-задач из kanban в .hermes_task.json
"""
import sqlite3, json, os, sys
KANBAN_DB = "/root/.hermes/kanban.db"
TASK_FILE = "/root/matryoshka/.hermes_task.json"
RESULT_FILE = "/root/matryoshka/.hermes_result.json"

def get_pending_alex_tasks():
    conn = sqlite3.connect(KANBAN_DB)
    cur = conn.execute(
        "SELECT id, title, body FROM tasks WHERE assignee='alex' AND status='ready'"
    )
    tasks = [{"id": r[0], "title": r[1], "body": r[2]} for r in cur.fetchall()]
    conn.close()
    return tasks

def push_to_file_task(task):
    payload = {
        "task_id": task["id"],
        "type": "kanban",
        "status": "pending",
        "from": "HERMES-kanban",
        "to": "ALEX",
        "via": "kanban_bridge",
        "description": task["title"],
        "task": {"text": task["body"], "command": task["title"]},
        "timeout": 300
    }
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Pushed {task['id']} to {TASK_FILE}")
    return True

def check_result():
    if not os.path.exists(RESULT_FILE):
        return None
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None
    if data.get("status") == "done" and data.get("task_id"):
        return data
    return None

def write_result_to_kanban(result_data):
    tid = result_data.get("task_id", "")
    res = result_data.get("result", {})
    ok = res.get("ok", False)
    output = res.get("output", "")[:5000]
    conn = sqlite3.connect(KANBAN_DB)
    conn.execute(
        "UPDATE tasks SET status=?, result=?, completed_at=?, claim_lock=NULL WHERE id=?",
        ("done" if ok else "failed",
         json.dumps({"output": output, "ok": ok, "agent": "ALEX"}),
         int(__import__("time").time()), tid)
    )
    conn.execute(
        "INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?,?,?,?)",
        (tid, "result_from_alex", json.dumps({"ok": ok, "output_len": len(output)}),
         int(__import__("time").time()))
    )
    conn.commit()
    conn.close()
    # Reset result file
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump({"task_id": None, "status": "idle", "result": None}, f)
    print(f"Written {tid} to kanban.db, reset result file")
    return True

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "sync"

    if mode == "push":
        tasks = get_pending_alex_tasks()
        if tasks:
            for t in tasks:
                push_to_file_task(t)
                break
            print(f"OK: {len(tasks)} pending task(s) pushed to file queue")
        else:
            print("OK: no pending alex tasks")
    elif mode == "pull":
        result = check_result()
        if result:
            write_result_to_kanban(result)
            print(f"OK: result written to kanban for {result['task_id']}")
        else:
            print("OK: no new results")
    elif mode == "sync":
        tasks = get_pending_alex_tasks()
        for t in tasks:
            push_to_file_task(t)
        result = check_result()
        if result:
            write_result_to_kanban(result)
        print(f"OK: sync done ({len(tasks)} pushed, {'1' if result else '0'} pulled)")
    else:
        print(f"Usage: {sys.argv[0]} [push|pull|sync]")
        sys.exit(1)
