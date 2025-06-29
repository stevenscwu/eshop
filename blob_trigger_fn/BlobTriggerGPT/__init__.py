import logging, os, json, time
import azure.functions as func
import openai
from openai import OpenAIError

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
        openai.api_version = "2025-01-01-preview"
        openai.api_base = os.environ["OPENAI_API_BASE"]
        openai.api_key = os.environ["OPENAI_API_KEY"]
        deployment_id = os.environ["OPENAI_DEPLOYMENT_NAME"]
    except KeyError as missing:
        logging.error("Missing env var: %s", missing)
        raise

    # --- Call model ---
    start = time.time()

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))
    deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

    logging.info(f"Using deployment_name: {deployment_name}")
    logging.info(f"Using API base: {os.getenv('OPENAI_API_BASE')}")
    logging.info(f"API type: {openai.api_type}, version: {openai.api_version}")

    summary = ""
    try:
        chat_response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": data},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        summary = chat_response.choices[0].message.content
    except Exception as e:
        logging.error("OpenAI API error: %s", repr(e))
        summary = f"OpenAI API error: {e}"


    latency_ms = (time.time() - start) * 1000
    logging.info("OpenAI latency: %.0f ms", latency_ms)

    outputblob.set(summary)
