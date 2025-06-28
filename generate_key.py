import secrets
import os

env_file = "expensive_stuff.env"
key_name = "TOKEN"
new_key = secrets.token_hex(32)

# Read existing .env content
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        lines = f.readlines()
else:
    lines = []

# Replace or add the TOKEN line
updated = False
for i, line in enumerate(lines):
    if line.startswith(f"{key_name}="):
        lines[i] = f"{key_name}={new_key}\n"
        updated = True
        break

if not updated:
    lines.append(f"{key_name}={new_key}\n")

# Write back to the .env file
with open(env_file, "w") as f:
    f.writelines(lines)

print(f"✅ New {key_name} written to {env_file}:")
print(new_key)