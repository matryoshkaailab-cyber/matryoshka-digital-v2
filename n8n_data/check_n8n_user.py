import subprocess
import json

# Check database
result = subprocess.run(
    ["docker", "exec", "n8n", "sqlite3", "/home/node/.n8n/database.sqlite",
     "SELECT id, email, firstName, lastName, role FROM user;"],
    capture_output=True, text=True, timeout=10
)
print("Users:", result.stdout.strip() or "none")
print("Err:", result.stderr.strip()[:200] if result.stderr else "")

# Check if database exists
result2 = subprocess.run(
    ["docker", "exec", "n8n", "sh", "-c", "ls -la /home/node/.n8n/database.sqlite 2>/dev/null && echo EXISTS || echo NO_DB"],
    capture_output=True, text=True, timeout=10
)
print("DB file:", result2.stdout.strip())

# List all files in .n8n
result3 = subprocess.run(
    ["docker", "exec", "n8n", "ls", "-la", "/home/node/.n8n/"],
    capture_output=True, text=True, timeout=10
)
print("Files:", result3.stdout.strip()[:500])
