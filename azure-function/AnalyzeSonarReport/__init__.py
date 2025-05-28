import logging
import openai
import azure.functions as func
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request for GPT-4 SonarQube summary.")

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    issues = body.get("issues")
    if not issues:
        return func.HttpResponse("Missing 'issues' field.", status_code=400)

    prompt = generate_prompt(issues)

    try:
        openai.api_type = "azure"
        openai.api_key = os.getenv("AZURE_OPENAI_KEY")
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_version = "2023-07-01-preview"

        completion = openai.ChatCompletion.create(
            engine=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a security code auditor that summarizes SonarQube scan results."},
                {"role": "user", "content": prompt}
            ]
        )

        summary = completion.choices[0].message.content
        return func.HttpResponse(summary, mimetype="text/markdown")

    except Exception as e:
        logging.error(f"OpenAI API call failed: {e}")
        return func.HttpResponse("GPT summary failed.", status_code=500)

def generate_prompt(issues):
    top = issues[:10]
    issue_lines = [f"- [{i['severity']}] {i['message']} (Component: {i['component']})" for i in top]
    return "You are a cybersecurity advisor. Summarize these SonarQube issues and offer practical recommendations:\n\nIssues:\n" + "\n".join(issue_lines)
