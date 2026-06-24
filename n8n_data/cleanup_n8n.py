import subprocess, json

result = subprocess.run(
    ["docker", "exec", "n8n", "n8n", "export:workflow", "--all"],
    capture_output=True, text=True, timeout=15
)
workflows = json.loads(result.stdout)
print(f"Total: {len(workflows)}")
for w in workflows:
    print(f"ID={w['id']} Name={w['name']} Active={w['active']} Nodes={len(w['nodes'])}")
    # Delete test workflow
    if w['name'] == 'test_workflow_2':
        print(f"  -> Deleting test workflow {w['id']}")
