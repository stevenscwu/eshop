import logging, os, json, time
import azure.functions as func
import openai

def main(inputblob: func.InputStream, outputblob: func.Out[str]):
    logging.info("Processing blob: %s (%s bytes)", inputblob.name, inputblob.length)

    data = inputblob.read().decode("utf-8")
    if len(data) > 1_000_000:  # 1 MB guard – adjust as needed
        logging.warning("Input file too large; aborting.")
        return

    prompt = (
        "You are a secure code reviewer with deep knowledge of software vulnerabilities. "
        "Given the following static analysis results from SonarQube (backend) and ESLint (frontend), perform the following tasks:\n\n"
        "1. Identify the top 10 most severe issues and explain why they are critical.\n"
        "2. Group issues by file/module and summarize their overall security and code quality state.\n"
        "3. Recommend specific refactoring or remediation actions for the top issues using secure coding best practices.\n"
        "4. Present your output in well-structured markdown, including:\n"
        "   - A prioritized issue summary table\n"
        "   - A per-module security assessment\n"
        "   - Actionable recommendations\n\n"
        f"Analysis results:\n{data}"
    )

    # --- OpenAI credentials ---
    try:
        openai.api_type = "azure"
        openai.api_version = "2024-11-20"
        openai.api_base = os.environ["OPENAI_API_BASE"]
        openai.api_key = os.environ["OPENAI_API_KEY"]
        deployment_id = os.environ["OPENAI_DEPLOYMENT_NAME"]
    except KeyError as missing:
        logging.error("Missing env var: %s", missing)
        raise

    # --- Call model ---
    start = time.time()
    try:
        response = openai.ChatCompletion.create(
            deployment_id=deployment_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )
    except openai.error.OpenAIError as e:
        logging.exception("OpenAI call failed: %s", e)
        raise

    latency_ms = (time.time() - start) * 1000
    logging.info("OpenAI latency: %.0f ms", latency_ms)

    summary = response.choices[0].message.content
    outputblob.set(summary)
