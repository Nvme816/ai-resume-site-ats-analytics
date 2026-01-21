
#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

import boto3


def require_env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def markdown_to_html_basic(md: str) -> str:
    html = md

    html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", html, flags=re.M)
    html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.M)

    lines = html.splitlines()
    out = []
    in_ul = False

    for line in lines:
        m = re.match(r"^\-\s+(.*)$", line)
        if m:
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{m.group(1)}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(line)

    if in_ul:
        out.append("</ul>")

    html = "\n".join(out)
    html = re.sub(r"(\r?\n){2,}", r"<br/>", html)

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Resume</title>
</head>
<body>
{html}
</body></html>"""


def simple_ats_analysis(text: str) -> dict:
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    headings = re.findall(r"^#{1,3}\s*(.+)$", text, flags=re.M)
    sections = {h.strip().lower() for h in headings}

    must_have = ["experience", "projects", "skills", "education"]
    missing_sections = [m for m in must_have if m not in sections]

    keywords = ["AWS", "IAM", "Terraform", "S3", "DynamoDB", "Python", "GitHub", "CI/CD", "CloudFormation", "SRE", "Security"]
    found = sorted({k for k in keywords if re.search(rf"\b{re.escape(k)}\b", text, flags=re.I)})

    avg_len = (sum(len(w) for w in words) / word_count) if word_count else 0.0
    readability = {"avg_word_length": round(avg_len, 2)}

    score = 50
    score += min(20, len(found) * 3)
    score += 10 if not missing_sections else 0
    score = max(0, min(100, score))

    return {
        "word_count": word_count,
        "ats_score": score,
        "keywords_detected": found,
        "readability": readability,
        "missing_sections": missing_sections,
        "role_alignment": {"Cloud Ops": 0.8, "SRE": 0.7, "Security": 0.6, "IAM": 0.6},
    }


def extract_first_json_object(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("Bedrock response did not contain a JSON object")

    return json.loads(m.group(0))


def bedrock_generate_html(md_text: str, model_id: str) -> str:
    br = boto3.client("bedrock-runtime")
    prompt = (
        "Convert this Markdown resume into clean, semantic, ATS-friendly HTML. "
        "No scripts. Minimal inline styles. Preserve headings and lists.\n\n"
        + md_text
    )
    resp = br.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": prompt}),
    )
    payload = json.loads(resp["body"].read().decode("utf-8"))
    html = payload.get("results", [{}])[0].get("outputText", "")
    html = (html or "").strip()
    if not html:
        raise ValueError("Bedrock returned empty HTML")
    return html


def bedrock_analyze_ats(md_text: str, model_id: str) -> dict:
    br = boto3.client("bedrock-runtime")
    schema_hint = {
        "type": "object",
        "properties": {
            "word_count": {"type": "number"},
            "ats_score": {"type": "number"},
            "keywords_detected": {"type": "array", "items": {"type": "string"}},
            "readability": {"type": "object"},
            "missing_sections": {"type": "array", "items": {"type": "string"}},
            "role_alignment": {"type": "object"},
        },
        "required": ["word_count", "ats_score", "keywords_detected", "readability", "missing_sections", "role_alignment"],
        "additionalProperties": False,
    }

    prompt = (
        "Analyze the following resume for ATS readiness. "
        "Return STRICT JSON matching this schema only:\n"
        + json.dumps(schema_hint)
        + "\n\nRESUME:\n"
        + md_text
    )

    resp = br.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"inputText": prompt}),
    )
    payload = json.loads(resp["body"].read().decode("utf-8"))
    raw = payload.get("results", [{}])[0].get("outputText", "")
    return extract_first_json_object(raw)


def safe_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", choices=["beta", "prod"], required=True)
    ap.add_argument("--resume", default="resume.md")
    args = ap.parse_args()

    bucket = require_env("BUCKET_NAME")
    deploy_tbl = require_env("DEPLOY_TABLE")
    analytics_tbl = require_env("ANALYTICS_TABLE")

    region = os.environ.get("AWS_REGION", "us-east-1").strip() or "us-east-1"
    model_id = os.environ.get("MODEL_ID", "").strip()
    github_sha = os.environ.get("GITHUB_SHA", "local-sha").strip()
    actor = os.environ.get("GITHUB_ACTOR", "local").strip()
    run_id = safe_int(os.environ.get("GITHUB_RUN_ID", "0"), default=0)

    s3_key_beta = os.environ.get("BETA_KEY", "beta/index.html").strip() or "beta/index.html"
    s3_key_prod = os.environ.get("PROD_KEY", "prod/index.html").strip() or "prod/index.html"

    if not os.path.exists(args.resume):
        raise FileNotFoundError(f"Resume file not found: {args.resume}")

    s3 = boto3.client("s3", region_name=region)
    ddb = boto3.client("dynamodb", region_name=region)

    md_text = read_text(args.resume)

    if model_id:
        try:
            html = bedrock_generate_html(md_text, model_id)
        except Exception as e:
            print(f"[warn] Bedrock HTML failed, using basic fallback: {e}")
            html = markdown_to_html_basic(md_text)
    else:
        html = markdown_to_html_basic(md_text)

    if model_id:
        try:
            ats = bedrock_analyze_ats(md_text, model_id)
        except Exception as e:
            print(f"[warn] Bedrock ATS failed, using simple fallback: {e}")
            ats = simple_ats_analysis(md_text)
    else:
        ats = simple_ats_analysis(md_text)

    html_bytes = html.encode("utf-8")
    html_hash = sha256_bytes(html_bytes)
    now = datetime.now(timezone.utc).isoformat()

    if args.env == "beta":
        key = s3_key_beta
    else:
        key = s3_key_prod

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=html_bytes,
        ContentType="text/html; charset=utf-8",
        CacheControl="no-store",
    )

    s3_url = f"s3://{bucket}/{key}"
    env_ts = f"{args.env}#{now}"

    ddb.put_item(
        TableName=deploy_tbl,
        Item={
            "commit_sha": {"S": github_sha},
            "env_ts": {"S": env_ts},
            "status": {"S": f"{args.env}-success"},
            "s3_url": {"S": s3_url},
            "model_id": {"S": model_id or "local-fallback"},
            "html_sha256": {"S": html_hash},
            "actor": {"S": actor},
            "run_id": {"N": str(run_id)},
        },
    )

    ddb.put_item(
        TableName=analytics_tbl,
        Item={
            "commit_sha": {"S": github_sha},
            "analysis_key": {"S": "ats#v1"},
            "word_count": {"N": str(ats.get("word_count", 0))},
            "ats_score": {"N": str(ats.get("ats_score", 0))},
            "keywords_detected": {"S": json.dumps(ats.get("keywords_detected", []))},
            "readability": {"S": json.dumps(ats.get("readability", {}))},
            "missing_sections": {"S": json.dumps(ats.get("missing_sections", []))},
            "role_alignment": {"S": json.dumps(ats.get("role_alignment", {}))},
        },
    )

    print(f"[ok] Deployed {args.env}: {s3_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
