import logging
import openai
import json
import azure.functions as func
import os

# Load Azure OpenAI environment config
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "turbo-2024-04-09"
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

def build_prompt(issues):
    example = json.dumps(issues[:10], indent=2)
    return f"""
You are a secure code reviewer with deep knowledge of software vulnerabilities.

Given the following static analysis results from SonarQube:

{example}

Please:
1. Identify the top 10 most critical issues and explain why they are important.
2. Group issues by file/module and summarize their code quality.
3. Recommend specific refactoring or remediation actions using secure coding best practices.
4. Present your output in well-structured markdown, including:
- A prioritized issue summary table
- A per-module security assessment
- Actionable recommendations
"""

@app.function_name(name="AnalyzeSonarReport")
@app.route(route="AnalyzeSonarReport", auth_level=func.AuthLevel.FUNCTION)
def analyze_sonar_report(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Parse input JSON
        data = req.get_json()
        issues = data.get("issues", [])

        # Log the received input
        logging.info(f"✅ Total issues received: {len(issues)}")
        if issues:
            logging.info(f"🔍 Sample issue: {json.dumps(issues[0], indent=2)}")

        if not isinstance(issues, list) or len(issues) == 0:
            return func.HttpResponse("❌ No valid 'issues' found in input JSON.", status_code=400)

        logging.info(f"🧠 Calling GPT-4 deployment: {deployment_name}")
        prompt = build_prompt(issues)

        # Call GPT-4 via Azure OpenAI
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        result = response["choices"][0]["message"]["content"]
        logging.info("✅ GPT-4 response received.")

        return func.HttpResponse(result, status_code=200, mimetype="text/markdown")

    except Exception as e:
        logging.exception("❌ Error during GPT-4 summarization.")
        return func.HttpResponse("Internal server error", status_code=500)
