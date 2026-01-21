
# AI Powered Resume Site with ATS Analytics and Two Stage Delivery
Convert a single Markdown resume into a publicly viewable, AI-enhanced HTML site with a CI/CD pipeline, Beta/Prod lanes, and ATS analytics.

## Situation
You maintain a single canonical `resume.md` source file. You want to automatically:
- Generate a polished HTML resume from markdown.
- Expose a **public beta** version for previews and an audited **production** version.
- Capture **ATS analytics** (keywords, word count, readability, missing sections) on each deployment for historical insight and continuous improvement. :contentReference[oaicite:2]{index=2}

## Objective
1. Convert `resume.md` into a professional AI-enhanced HTML site without manual editing. :contentReference[oaicite:3]{index=3}  
2. Implement dual CI/CD lanes:
   - PR → *beta* deployment.
   - Merge to *main* → *prod* promotion. :contentReference[oaicite:4]{index=4}  
3. Persist ATS analytics and deployment metadata to DynamoDB for full traceability. :contentReference[oaicite:5]{index=5}  
4. Define and manage infrastructure (S3, DynamoDB, IAM) as code via CloudFormation. :contentReference[oaicite:6]{index=6}  
5. Enforce least-privilege access and produce verifiable deployment evidence. :contentReference[oaicite:7]{index=7}

## Services Used
- **AWS S3** – Hosts static HTML resume with versioned `beta/` and `prod/` prefixes. :contentReference[oaicite:8]{index=8}  
- **AWS DynamoDB** – Two tables for tracking CI/CD deployments and ATS analytics. :contentReference[oaicite:9]{index=9}  
- **AWS IAM** – Scoped permissions for CI/CD role with GitHub OIDC. :contentReference[oaicite:10]{index=10}  
- **AWS CloudFormation** – Defines and deploys all infra as code. :contentReference[oaicite:11]{index=11}  
- **GitHub Actions** – CI/CD pipeline (PR beta, main prod). :contentReference[oaicite:12]{index=12}  
- **Python** – Markdown→HTML conversion, ATS analytics, S3 uploads, DynamoDB writes. :contentReference[oaicite:13]{index=13}  
- **Bedrock/AI** *(optional)* – Enhances HTML output and ATS scoring via AI if configured.

## Architecture
Single source `resume.md` → Python script generates HTML + ATS analytics →  
- **Beta**: deployed to S3 under `beta/` via GitHub PR workflows. :contentReference[oaicite:14]{index=14}  
- **Prod**: upon merge to `main`, promotes or re-uploads production version. :contentReference[oaicite:15]{index=15}  
Deployment metadata and ATS score info are logged to DynamoDB. :contentReference[oaicite:16]{index=16}

## Steps Completed
1. Created CloudFormation templates defining:
   - Versioned S3 bucket with `beta/` and `prod/` prefixes.
   - Two DynamoDB tables (`DeploymentTracking` and `ResumeAnalytics`). :contentReference[oaicite:17]{index=17}  
2. Finished Python pipeline script to:
   - Convert Markdown to HTML (basic or AI enhanced).
   - Upload to S3.
   - Run ATS analysis (simple or Bedrock).
   - Write structured records to DynamoDB. :contentReference[oaicite:18]{index=18}  
3. Configured GitHub Actions workflows:
   - On PR: deploy beta, log metadata.
   - On merge to main: promote to prod, log metadata. :contentReference[oaicite:19]{index=19}  
4. Scoped IAM role for GitHub OIDC with least privilege:
   - S3 put/copy.
   - DynamoDB write.
   - CloudFormation deploy. :contentReference[oaicite:20]{index=20}  
5. Implemented environment detection and error handling in the pipeline.

## Deployment Details
- **Infrastructure as Code**: CloudFormation template under `infra/template.yml`. :contentReference[oaicite:21]{index=21}  
- **CI/CD Pipeline**: `resume.yml` in `.github/workflows/`. :contentReference[oaicite:22]{index=22}  
- **Pipeline Logic**:
  - Beta on PRs → deployed to `beta/index.html`.
  - Prod on main → deployed to `prod/index.html`. :contentReference[oaicite:23]{index=23}  
- **DynamoDB Tracking**:
  - `DeploymentTracking`: commit SHA, environment, timestamp, S3 URL, model use. :contentReference[oaicite:24]{index=24}  
  - `ResumeAnalytics`: ATS score details. :contentReference[oaicite:25]{index=25}  

## How to Verify
1. Open GitHub → Create a PR → confirm Beta deployment in S3 `beta/`. :contentReference[oaicite:26]{index=26}  
2. Merge PR → validate production in `prod/`. :contentReference[oaicite:27]{index=27}  
3. Check DynamoDB tables → confirm records for both deployment and ATS analytics. :contentReference[oaicite:28]{index=28}  
4. Review GitHub Actions logs for clear timestamped evidence. :contentReference[oaicite:29]{index=29}

## Results
- Resume site is auto-generated and publicly accessible per environment. :contentReference[oaicite:30]{index=30}  
- CI/CD traceability is captured through automated deployments and analytics logs. :contentReference[oaicite:31]{index=31}  
- Dual-lane deployment ensures safe previewing before production promotion. :contentReference[oaicite:32]{index=32}

## Lessons Learned
- Infrastructure as code avoids manual UI interactions and drift. :contentReference[oaicite:33]{index=33}  
- ATS analytics provide actionable insights on resume content over time. :contentReference[oaicite:34]{index=34}  
- Two-stage delivery (beta/prod) bridges fast iteration with production safety. :contentReference[oaicite:35]{index=35}

## Project Links
- Medium article: *AI Powered Resume Site with ATS Analytics and Two Stage Delivery*  
  https://medium.com/%40jammiesmith2025/ai-powered-resume-site-with-ats-analytics-and-two-stage-delivery-3f48c51a58dd
