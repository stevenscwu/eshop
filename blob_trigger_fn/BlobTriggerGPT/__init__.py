import logging, os, json, time
import azure.functions as func
from openai import AzureOpenAI

def main(inputblob: func.InputStream, outputblob: func.Out[str]):
    logging.info("Processing blob: %s (%s bytes)", inputblob.name, inputblob.length)

    data = inputblob.read().decode("utf-8")
    if len(data) > 1_000_000:  # 1 MB guard – adjust as needed
        logging.warning("Too large input file; aborting.")
        return

    prompt = (
        "You are a security engineer. Your job is to review a SonarQube static analysis report (in JSON format), "
        "which contains a list of issues of varying severity, type, and location in the code. "
        "The purpose is to help developers and managers quickly understand the security and code quality risks, "
        "and prioritize what needs to be fixed.\n\n"
        "Given the following SonarQube JSON report, perform these tasks:\n"
        "1. Top Critical Issues:\n"
        "   - List the top 10 most severe issues, showing severity, file and line number, rule/key, "
        "short description, and *why* this issue is critical and what could happen if not fixed.\n"
        "2. Summary by Severity:\n"
        "   - Provide a count of issues by severity (e.g., BLOCKER, CRITICAL, MAJOR, MINOR, INFO).\n"
        "3. Issue Type Breakdown:\n"
        "   - Summarize how many issues are bugs, vulnerabilities, and code smells.\n"
        "4. Key Patterns/Hotspots:\n"
        "   - Point out any files, modules, or code sections with a concentration of severe issues or repeated patterns.\n"
        "5. Actionable Next Steps:\n"
        "   - Give 3–5 clear, prioritized recommendations for the development team, focusing first on eliminating "
        "critical/blocker security and reliability issues.\n"
        "If the report is very large, highlight areas that may be overwhelming and suggest ways to triage. "
        "Produce your output as markdown, using tables or bullet points as needed for clarity. Be concise, but do not omit important security or reliability risks.\n\n"
        f"Here is the SonarQube JSON report:\n{data}"
    )

    # --- OpenAI credentials (env vars) ---
    try:
        api_base = os.environ["OPENAI_API_BASE"]
        api_key = os.environ["OPENAI_API_KEY"]
        deployment_name = os.environ["OPENAI_DEPLOYMENT_NAME"]
        api_version = os.environ.get("OPENAI_API_VERSION", "2024-12-01-preview")
    except KeyError as missing:
        logging.error("Missing env var: %s", missing)
        raise

    # --- Create AzureOpenAI client ---
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=api_base,
        api_version=api_version,
    )

    logging.info(f"Using deployment_name: {deployment_name}")
    logging.info(f"Using API base: {api_base}")
    logging.info(f"API version: {api_version}")

    # --- Call model ---
    summary = ""
    start = time.time()
    try:
        chat_response = client.chat.completions.create(
            model=deployment_name,  # <- this is the Azure "deployment name"!
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": data},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        summary = chat_response.choices[0].message.content
        # print("Token usage:", chat_response.usage)
        logging.info("Token usage: %s", chat_response.usage)

    except Exception as e:
        logging.error("OpenAI API error: %s", repr(e))
        summary = f"OpenAI API error: {e}"

    latency_ms = (time.time() - start) * 1000
    logging.info("OpenAI latency: %.0f ms", latency_ms)

    outputblob.set(summary)
