# PROMPTS.md — erasebg deployment setup

## Context
- Local folder: C:\Projects\listify-rembg
- GitHub repo: https://github.com/wavesss/erasebg
- HF Space: https://huggingface.co/spaces/wavessshug/erasebg
- All 4 app files already exist (main.py, Dockerfile, requirements.txt, README.md)

## Task
1. Check if git is initialized, if not run `git init`
2. Check if remote origin points to github.com/wavesss/erasebg, if not set it
3. Create `.github/workflows/deploy-hf.yml` with GitHub Actions workflow
   that auto-pushes to HF Space on every push to main
   Use HF_TOKEN secret for auth
   HF Space URL: https://huggingface.co/spaces/wavessshug/erasebg
4. Stage all files and do first commit if needed
5. Push to GitHub
6. Print reminder: "Add HF_TOKEN secret in GitHub → Settings → Secrets → Actions"

## Done when
- All files pushed to github.com/wavesss/erasebg
- .github/workflows/deploy-hf.yml exists in the repo
- Instructions printed for adding the HF_TOKEN secret
