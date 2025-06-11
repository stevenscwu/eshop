import json
import os
import math

# Constants
INPUT_FILE = "sonar-report-pretty.json"
OUTPUT_DIR = "chunked-reports"
PROMPT_TEMPLATE_FILE = "base-prompt.txt"
CHUNK_SIZE = 10  # Number of issues per chunk

# Load prompt template
with open(PROMPT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
    base_prompt = f.read()

# Load SonarQube report
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)
    issues = data.get("issues", [])

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Split into chunks
total_chunks = math.ceil(len(issues) / CHUNK_SIZE)
for i in range(total_chunks):
    chunk = issues[i * CHUNK_SIZE: (i + 1) * CHUNK_SIZE]
    prompt = base_prompt.replace("{CHUNK_NUM}", str(i + 1)).replace("{TOTAL_CHUNKS}", str(total_chunks))
    chunk_input = {
        "prompt": prompt,
        "issues": chunk
    }
    filename = f"{OUTPUT_DIR}/chunk_{i+1:03}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chunk_input, f, indent=2, ensure_ascii=False)

print(f"✅ Split {len(issues)} issues into {total_chunks} chunks in '{OUTPUT_DIR}/'")
