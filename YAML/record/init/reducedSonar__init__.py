import logging
import openai
import json
import azure.functions as func
import os

# Trigger redeploy from GitHub Actions

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "2023-07-01-preview"
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
        logging.info("🔁 Azure Function triggered")

        if req.method != "POST":
            return func.HttpResponse(
                "❌ Please use POST with JSON body containing 'issues'.", status_code=400
            )

        data = req.get_json()
        issues = data.get("issues", [])
        logging.info(f"✅ Total issues received: {len(issues)}")
        if issues:
            logging.info(f"🔍 Sample issue: {json.dumps(issues[0], indent=2)}")
        else:
            logging.warning("⚠️ No issues found in input JSON.")
        
        if not isinstance(issues, list) or len(issues) == 0:
            return func.HttpResponse("❌ No valid 'issues' found in input JSON.", status_code=400)

        logging.info(f"🧠 Calling GPT-4 deployment: {deployment_name}")
        prompt = build_prompt(issues)

        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert AI assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2500
        )

        logging.info(f"🧾 Full GPT-4 raw response:\n{json.dumps(response, indent=2)}")
        
        result = response["choices"][0]["message"]["content"]
        logging.info("✅ GPT-4 response received.")
        return func.HttpResponse(result, status_code=200, mimetype="text/markdown")

    except Exception as e:
        logging.exception("❌ Error during GPT-4 summarization.")
        return func.HttpResponse("Internal server error", status_code=500)#