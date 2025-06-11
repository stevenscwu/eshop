from pathlib import Path

# Generate the patched content for split_sonar_report.py
patched_code = '''\
import json
import os
import math

# Dynamic paths based on script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_TEMPLATE_FILE = os.path.join(BASE_DIR, "../../base-prompt.txt")
INPUT_FILE = os.path.join(BASE_DIR, "../../report/20250611/sonar-report-20250611-072220.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../chunked-reports")
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
    filename = os.path.join(OUTPUT_DIR, f"chunk_{i+1:03}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(chunk_input, f, indent=2, ensure_ascii=False)

print(f"✅ Split {len(issues)} issues into {total_chunks} chunks in '{OUTPUT_DIR}/'")
'''

# Save to file for user download
output_path = "/mnt/data/split_sonar_report.py"
Path(output_path).write_text(patched_code, encoding="utf-8")


