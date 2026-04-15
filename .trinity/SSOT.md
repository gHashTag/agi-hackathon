# SSOT - Single Source of Truth
## Trinity Cognitive Probes - AGI Hackathon

**Purpose:** This file is the CANONICAL reference for all URLs, counts, slugs, and identifiers.
**Rule:** When in doubt, consult this file. All other documentation MUST match these values.

---

## 🌐 GitHub Repository

| Field | Value |
|-------|-------|
| **Primary URL** | `https://github.com/gHashTag/agi-hackathon` |
| **Git Remote** | `git@github.com:gHashTag/agi-hackathon.git` |
| **Owner** | gHashTag |
| **Repo** | agi-hackathon |
| **Visibility** | Public |
| **License** | CC0-1.0 |

**INCORRECT alternatives to NEVER use:**
- ❌ `https://github.com/gHashTag/agi-hackathon` (WRONG org)
- ❌ `https://github.com/gHashTag/t27` (different repo - this is the source project, not hackathon)

---

## 📊 Kaggle Datasets

| Track | Name | Kaggle Slug | URL | Questions | Status |
|-------|------|-------------|-----|-----------|--------|
| THLP | Hippocampal Learning Probe | `trinity-cognitive-probes-thlp-mc` | https://www.kaggle.com/datasets/playra/hlp-mc | 19,681 | ✅ Published |
| TTM | Metacognition Probe | `trinity-cognitive-probes-ttm-mc` | https://www.kaggle.com/datasets/playra/tm-mc | 4,931 | ✅ Published |
| TAGP | Attentional Gateway Probe | `trinity-cognitive-probes-tagp-mc` | https://www.kaggle.com/datasets/playra/agp-mc | 17,601 | ✅ Published |
| TEFB | Executive Function Battery | `trinity-cognitive-probes-tefb-mc` | https://www.kaggle.com/datasets/playra/efb-mc | 21,081 | ✅ Published |
| TSCP | Social Cognition Probe | `trinity-cognitive-probes-tscp-mc` | https://www.kaggle.com/datasets/playra/scp-mc | 2,839 | ✅ Published |

**TOTAL QUESTIONS: 65,133**

**Common slug errors to AVOID:**
- ❌ `trinity-cognitive-probes-tmp-mc` (tmp instead of ttm)
- ❌ `trinity-cognitive-probes-thlp` (missing -mc suffix)

---

## 📁 File Name Conventions

| Track | CSV Filename | Format |
|-------|--------------|--------|
| THLP | `thlp_mc_new.csv` | id,question_type,question,A,B,C,D,answer |
| TTM | `ttm_mc_new.csv` | id,question_type,question,A,B,C,D,answer |
| TAGP | `tagp_mc.csv` | id,question_type,question,A,B,C,D,answer |
| TEFB | `tefb_mc_new.csv` | id,question_type,question,A,B,C,D,answer |
| TSCP | `tscp_mc_new.csv` | id,question_type,question,A,B,C,D,answer |

---

## 🧠 Cognitive Tracks Reference

| Track | Full Name | Cognitive Ability | Brain Zone |
|-------|-----------|-------------------|------------|
| THLP | Trinity Hippocampal Learning Probe | Pattern learning, belief update, rule induction | Hippocampus, Entorhinal Cortex |
| TTM | Trinity Metacognition Probe | Confidence calibration, error detection, meta-learning | Prefrontal Cortex |
| TAGP | Trinity Attentional Gateway Probe | Selective filtering, sustained attention, attention shifting | Parietal Lobes |
| TEFB | Trinity Executive Function Battery | Multi-step planning, working memory, cognitive flexibility | DLPFC |
| TSCP | Trinity Social Cognition Probe | Theory of Mind, pragmatic inference, social norms | TPJ, mPFC |

---

## 🎯 API Integration

### Supported Models

| Model | API Key Variable | Model String | Cost (per 1K calls) |
|-------|-----------------|--------------|---------------------|
| Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet-20241022` | ~$3.00 |
| GPT-4o Mini | `OPENAI_API_KEY` | `gpt-4o-mini-2024-07-18` | ~$0.15 |
| Gemini 1.5 Flash | `GOOGLE_API_KEY` | `gemini-1.5-flash-latest` | ~$0.075 |

---

## 📚 Academic Citation (BibTeX)

```bibtex
@dataset{trinity_cognitive_probes_2025,
  title={Trinity Cognitive Probes: A 5-Track Benchmark for Measuring AGI Progress},
  author={gHashTag},
  year={2025},
  publisher={Kaggle},
  url={https://github.com/gHashTag/agi-hackathon},
  version={1.0.0},
  license={CC0-1.0}
}
```

---

## 🔗 Related Resources

| Resource | URL | Notes |
|----------|-----|-------|
| Source Project | https://github.com/gHashTag/t27 | T27 (TRI-27) spec-first architecture |
| Hackathon Info | TBD | Google DeepMind x Kaggle (2026) |
| Documentation | https://github.com/gHashTag/agi-hackathon/tree/main/docs | This repo |

---

## ⚠️ Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-01-21 | Fixed GitHub URL from browseros-ai to gHashTag | SSOT correction |
| 2025-01-21 | Standardized Kaggle slugs (ttm not tmp) | Consistency |
| 2025-01-21 | Created this SSOT file | Prevent divergence |

---

## ✅ Verification Checklist

Before publishing or sharing, verify:

- [ ] GitHub URL is `https://github.com/gHashTag/agi-hackathon`
- [ ] Kaggle slugs use `ttm` not `tmp`
- [ ] Question totals sum to 65,133
- [ ] License is CC0-1.0
- [ ] Citation uses `agi-hackathon` not `t27`

---

**Last Verified:** 2025-01-21
**Verified By:** Claude Agent
**φ² + 1/φ² = 3 | TRINITY**
