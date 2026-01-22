
# AI Powered Resume Site with ATS Analytics and Two Stage Delivery
Convert a single Markdown resume into a publicly viewable, AI-enhanced HTML site with a CI/CD pipeline, Beta/Prod lanes, and ATS analytics.

## Situation
You maintain a single canonical `resume.md` source file. You want to automatically:
- Generate a polished HTML resume from markdown.
- Expose a **public beta** version for previews and an audited **production** version.
- Capture **ATS analytics** (keywords, word count, readability, missing sections) on each deployment for historical insight and continuous improvement.

## Objective
1. Convert `resume.md` into a professional AI-enhanced HTML site without manual editing. 
2. Implement dual CI/CD lanes:
   - PR > *beta* deployment.
   - Merge to *main* > *prod* promotion. :contentReference[oaicite:4]{index=4}  
3. Persist ATS analytics and deployment metadata to DynamoDB for full traceability. 
4. Define and manage infrastructure (S3, DynamoDB, IAM) as code via CloudFormation. 
5. Enforce least-privilege access and produce verifiable deployment evidence. 

## Services Used
- **AWS S3** – Hosts static HTML resume with versioned `beta/` and `prod/` prefixes. 
- **AWS DynamoDB** – Two tables for tracking CI/CD deployments and ATS analytics.   
- **AWS IAM** – Scoped permissions for CI/CD role with GitHub OIDC. 
- **AWS CloudFormation** – Defines and deploys all infra as code.   
- **GitHub Actions** – CI/CD pipeline (PR beta, main prod).   
- **Python** – Markdown→HTML conversion, ATS analytics, S3 uploads, DynamoDB writes.   
- **Bedrock/AI** *(optional)* – Enhances HTML output and ATS scoring via AI if configured.

## Architecture
Single source `resume.md` → Python script generates HTML + ATS analytics  
- **Beta**: deployed to S3 under `beta/` via GitHub PR workflows.   
- **Prod**: upon merge to `main`, promotes or re-uploads production version.   
Deployment metadata and ATS score info are logged to DynamoDB. 

## Steps Completed
1. Created CloudFormation templates defining:
   - Versioned S3 bucket with `beta/` and `prod/` prefixes.
   - Two DynamoDB tables (`DeploymentTracking` and `ResumeAnalytics`).
2. Finished Python pipeline script to:
   - Convert Markdown to HTML (basic or AI enhanced).
   - Upload to S3.
   - Run ATS analysis (simple or Bedrock).
   - Write structured records to DynamoDB. 
3. Configured GitHub Actions workflows:
   - On PR: deploy beta, log metadata.
   - On merge to main: promote to prod, log metadata.   
4. Scoped IAM role for GitHub OIDC with least privilege:
   - S3 put/copy.
   - DynamoDB write.
   - CloudFormation deploy. 
5. Implemented environment detection and error handling in the pipeline.

## Deployment Details
- **Infrastructure as Code**: CloudFormation template under `infra/template.yml`.   
- **CI/CD Pipeline**: `resume.yml` in `.github/workflows/`.   
- **Pipeline Logic**:
  - Beta on PRs → deployed to `beta/index.html`.
  - Prod on main → deployed to `prod/index.html`.   
- **DynamoDB Tracking**:
  - `DeploymentTracking`: commit SHA, environment, timestamp, S3 URL, model use. 
  - `ResumeAnalytics`: ATS score details.  

## How to Verify
1. Open GitHub → Create a PR → confirm Beta deployment in S3 `beta/`. 
2. Merge PR → validate production in `prod/`.   
3. Check DynamoDB tables → confirm records for both deployment and ATS analytics. 
4. Review GitHub Actions logs for clear timestamped evidence. 

## Results
- Resume site is auto-generated and publicly accessible per environment.  
- CI/CD traceability is captured through automated deployments and analytics logs.  
- Dual-lane deployment ensures safe previewing before production promotion. 

## Lessons Learned
- Infrastructure as code avoids manual UI interactions and drift.   
- ATS analytics provide actionable insights on resume content over time. 
- Two-stage delivery (beta/prod) bridges fast iteration with production safety.

## Project Links
- Medium article: *AI Powered Resume Site with ATS Analytics and Two Stage Delivery*  
  https://medium.com/%40jammiesmith2025/ai-powered-resume-site-with-ats-analytics-and-two-stage-delivery-3f48c51a58dd
