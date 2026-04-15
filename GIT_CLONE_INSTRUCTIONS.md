# AGI Hackathon - Repository Clone

## Quick Start

This is a CLONE of the official agi-hackathon repository.
Original: https://github.com/gHashTag/agi-hackathon

**What you need to do:**

### 1. Create your GitHub repository (if not already exists)
```bash
gh repo create agi-hackathon-YOURNAME --public --source=. --description "AGI Hackathon Evaluation"
```

### 2. Update git remote
```bash
cd agi-hackathon-copy
git remote set origin https://github.com/YOURNAME/agi-hackathon.git
git remote -v
```

### 3. Create a commit
```bash
cd agi-hackathon-copy
git add .
git commit -m "Initial commit: Clone of agi-hackathon repository"
```

### 4. Push to GitHub
```bash
cd agi-hackathon-copy
git push -u origin master
```

### 5. Verify
```bash
# Check the new repository
gh repo view YOURNAME/agi-hackathon
# Or open in browser:
# https://github.com/YOURNAME/agi-hackathon
```

---

## Files Included

All files from the original repository are included:
- Scripts for evaluation
- Sample data files
- AI prompts (Claude, Gemini, GPT-4o)
- Documentation

---

## Links

- Original repository: https://github.com/gHashTag/agi-hackathon
- Your repository (after creation): https://github.com/YOURNAME/agi-hackathon

---

**Note:** Replace YOURNAME with your actual GitHub username!
