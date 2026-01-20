# Manual Steps Required - GitHub Reference Lock

**Date:** January 20, 2026  
**Status:** Ready for execution  
**Time Required:** ~30 minutes

---

## STEP 1: Commit and Push Latest Changes

```bash
cd ~/Desktop/bdr-insurance-platform

# Stage all new files
git add .

# Commit
git commit -m "GitHub Reference Lock & HF Alignment - Final freeze"

# Push to GitHub with tag
git push origin main
git push origin reference-v1.0
```

---

## STEP 2: Create GitHub Profile Repository

1. Go to: https://github.com/new
2. Repository name: **PyBADR** (must match your username exactly)
3. Description: "Decision Intelligence Architecture Profile"
4. Public repository
5. **Do NOT** initialize with README (we'll add it manually)
6. Click "Create repository"

7. Copy the profile README:
```bash
cd ~/Desktop/bdr-insurance-platform
cp GITHUB_PROFILE_README.md ~/Desktop/PyBADR-profile-repo/README.md
```

8. Initialize and push:
```bash
cd ~/Desktop
mkdir PyBADR-profile-repo
cd PyBADR-profile-repo
cp ~/Desktop/bdr-insurance-platform/GITHUB_PROFILE_README.md README.md

git init
git add README.md
git commit -m "Add profile README - Reference Architecture"
git branch -M main
git remote add origin https://github.com/PyBADR/PyBADR.git
git push -u origin main
```

---

## STEP 3: Archive Non-Reference Repositories

For each of these repositories, archive them:

1. **Customer-Behavioural-Analysis-and-prediction**
2. **Risk-Modelling**
3. **Power-BI-Dashboard**
4. **Product-recommendation**
5. **Getting-and-Cleaning-Data-Project**
6. **HR_Analysis**

**How to archive:**
1. Go to repository (e.g., https://github.com/PyBADR/Customer-Behavioural-Analysis-and-prediction)
2. Click "Settings" tab
3. Scroll to bottom "Danger Zone"
4. Click "Archive this repository"
5. Type repository name to confirm
6. Click "I understand, archive this repository"

**Repeat for all 6 repositories above.**

---

## STEP 4: Create Reference Repositories (if needed)

### Option A: Create new repositories

If you want separate repos for contracts, harness, and adapters:

1. **bdr-decision-contracts**
   - Description: "Authority, responsibility, and ownership contracts"
   - Public
   - Initialize with README
   - Add: "Reference documentation for decision governance contracts"

2. **bdr-evaluation-harness**
   - Description: "Release gating, regression detection, and audit metrics"
   - Public
   - Initialize with README
   - Add: "Reference implementation of evaluation harness"

3. **bdr-hf-adapters**
   - Description: "UI adapters only - zero decision logic"
   - Public
   - Initialize with README
   - Add: "Interface layer for Hugging Face Spaces"

### Option B: Keep single repository

If you prefer to keep everything in **bdr-insurance-platform**, that's fine too. Just ensure it's the primary pinned repository.

---

## STEP 5: Pin Repositories

1. Go to your profile: https://github.com/PyBADR
2. Click "Customize your pins"
3. Select exactly 4 repositories:
   - ✅ bdr-insurance-platform (or bdr-insurance-decision-platform if renamed)
   - ✅ bdr-decision-contracts (if created)
   - ✅ bdr-evaluation-harness (if created)
   - ✅ bdr-hf-adapters (if created)
4. Click "Save pins"

**If using single repository approach:**
- Pin only: bdr-insurance-platform
- Unpin all others

---

## STEP 6: Create GitHub Release

1. Go to: https://github.com/PyBADR/bdr-insurance-platform/releases
2. Click "Create a new release"
3. Tag: **reference-v1.0** (should already exist)
4. Release title: **Reference Architecture v1.0 - FROZEN**
5. Description:
```
# Reference Architecture v1.0 - FROZEN

This release marks the BDR Insurance Decision Intelligence Platform as a frozen reference architecture.

## Status
- Architecture: FROZEN
- Mutability: DISALLOWED
- Purpose: Regulatory/legal/audit review

## Complete Governance Stack
- Phase 2.1: Ownership & Accountability Layer
- Phase 2.1.1: Decision Authority Layer
- Phase 2.2: Authority Anchor + Production Gate
- Phase 2.3: Decision Finality & Execution Boundary
- Phase 3: Evaluation Harness as Release Gate

## Platform Guarantees
1. Legal Attribution - Every decision traceable
2. Runtime Enforcement - All rules enforced at execution
3. Execution Boundary - Decisions separate from execution
4. Immutable Finality - FINALIZED decisions cannot change
5. Release Safety - Evaluation gate blocks unsafe releases

## Documentation
- See PHASE_2_2_IMPLEMENTATION_SUMMARY.md
- See PHASE_3_IMPLEMENTATION_SUMMARY.md
- See PHASE_A_IMPLEMENTATION_SUMMARY.md
- See OPTION_A_COMPLETE.md
- See docs/REFERENCE_RUN_2026.md

## Installation
```bash
pip install git+https://github.com/PyBADR/bdr-insurance-platform.git@reference-v1.0
```

## Important
This is NOT a product. This is NOT a demo.
This is a frozen architectural reference.

All future work requires fork or new version.
```

6. Click "Publish release"

---

## STEP 7: Update Hugging Face Spaces

For each HF Space you have:

1. Go to Space settings
2. Update README.md with content from HF_SPACE_README_TEMPLATE.md
3. Ensure app.py uses:
```python
from bdr_insurance_platform.modules.[module] import service
from bdr_insurance_platform.core.execution import ExecutionEnvironment

env = ExecutionEnvironment.SIMULATION

def run(input_data):
    return service.simulate(input_data, env=env)
```

4. Update requirements.txt:
```
bdr-insurance-platform @ git+https://github.com/PyBADR/bdr-insurance-platform.git@reference-v1.0
gradio
```

5. Remove any decision logic from Space code

---

## STEP 8: Verify Profile

1. Go to: https://github.com/PyBADR
2. Verify:
   - ✅ Profile README shows "BDR.AI — Decision Intelligence Architecture"
   - ✅ Exactly 4 repositories pinned (or 1 if single-repo approach)
   - ✅ Archived repos don't show in "Popular repositories"
   - ✅ Profile reads like architecture spec, not CV

---

## STEP 9: Final Verification

```bash
# Verify package installable
pip install git+https://github.com/PyBADR/bdr-insurance-platform.git@reference-v1.0

# Verify imports work
python3 -c "from bdr_insurance_platform.core.governance import DecisionAuthority; print('✅ SUCCESS')"

# Verify tag exists
cd ~/Desktop/bdr-insurance-platform
git tag -l reference-v1.0
git show reference-v1.0
```

---

## COMPLETION CHECKLIST

- [ ] Step 1: Committed and pushed latest changes
- [ ] Step 2: Created PyBADR/PyBADR profile repository
- [ ] Step 3: Archived 6 non-reference repositories
- [ ] Step 4: Created reference repositories (or kept single repo)
- [ ] Step 5: Pinned exactly 4 repositories (or 1)
- [ ] Step 6: Created GitHub Release for reference-v1.0
- [ ] Step 7: Updated HF Spaces with template
- [ ] Step 8: Verified profile appearance
- [ ] Step 9: Verified package installation

---

## FINAL STATUS

After completing all steps:

**GitHub:**
- ✅ System of Record
- ✅ Reference Architecture visible
- ✅ Profile reads like spec, not CV
- ✅ Archived repos hidden
- ✅ Release published

**Hugging Face:**
- ✅ Interface layer only
- ✅ No decision logic
- ✅ Simulation mode only
- ✅ Warning displayed

**Architecture:**
- ✅ FROZEN
- ✅ Version 1.0
- ✅ Mutability DISALLOWED
- ✅ Ready for regulatory review

---

**LOCKED. READY FOR PUBLICATION.**
