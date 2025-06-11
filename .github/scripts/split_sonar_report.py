import json
import os
import math
import sys

# Accept input/output arguments
if len(sys.argv) != 3:
    print("Usage: python split_sonar_report.py <input_json> <output_dir>")
    sys.exit(1)

input_path = sys.argv[1]
output_dir = sys.argv[2]
prompt_template_file = os.path.join(os.path.dirname(__file__), "../base-prompt.txt")

# Load prompt template
with open(prompt_template_file, "r", encoding="utf-8") as f:
    base_prompt = f.read()

# Load SonarQube report
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    issues = data.get("issues", [])

# Create output directory if needed
os.makedirs(output_dir, exist_ok=True)

# Split into chunks
chunk_size = 10
total_chunks = math.ceil(len(issues) / chunk_size)
for i in range(total_chunks):
    chunk = issues[i * chunk_size: (i + 1) * chunk_size]
    prompt = base_prompt.replace("{CHUNK_NUM}", str(i + 1)).replace("{TOTAL_CHUNKS}", str(total_chunks))
    chunk_input = {
        "prompt": prompt,
        "issues": chunk
    }
    output_file = os.path.join(output_dir, f"chunk_{i+1:03}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunk_input, f, indent=2, ensure_ascii=False)

print(f"✅ Split {len(issues)} issues into {total_chunks} chunks in '{output_dir}'")
