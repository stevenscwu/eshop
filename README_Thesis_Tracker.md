## ✅ Thesis Milestone Tracker: SonarQube + GPT-4 Integration

### 📁 1. Setup & Repository Preparation
- [x] Clean original GitHub repo, keep GitHub Actions secrets
- [x] Replace repo content with eShopOnWeb base code
- [x] Ensure solution builds and runs locally
- [x] Push working codebase to GitHub

### 🔍 2. Phase 1: Static Code Analysis Integration
- [x] Setup self-hosted SonarQube
- [x] Run SonarQube scan on backend (ASP.NET Core)
- [x] Export SonarQube scan results as JSON (`sonar_issues.json`)
- [x] Configure ESLint for Angular frontend
- [x] Run ESLint via GitHub Actions and export JSON (`frontend_lint.json`)
- [x] Merge SonarQube + ESLint results into a unified JSON

### 🤖 3. Phase 2: GPT-4 Integration
- [x] Setup Azure Function to host GPT-4 analysis
- [x] Design GPT-4 prompt for vulnerability triage
- [x] Ensure secure environment variable handling
- [x] Invoke GPT-4 from pipeline and generate `summary.md`
- [ ] Review `summary.md` for quality and accuracy
- [ ] Add manual approval step before deployment

### 🚀 4. Phase 3: Deployment
- [x] Add conditional deployment step to GitHub Actions
- [ ] Ensure deployment only occurs if GPT-4 report is cleared
- [ ] Test full push-to-deploy workflow with scan + review + deploy

### 🧪 5. Evaluation & Thesis Update
- [ ] Record examples of scan results + GPT-4 analysis
- [ ] Evaluate GPT-4’s impact: false positive reduction, guidance quality
- [ ] Update Chapter 5: Experiment Results
- [ ] Update Chapter 6: Lessons Learned + Future Work
- [ ] Proofread and submit final thesis draft
