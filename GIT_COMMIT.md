# Git Commit Instructions

## Commit Message

```bash
git add .
git commit -m "feat: enhance trinity benchmarks with adversarial datasets

- Add 5 adversarial datasets (2,695 total questions)
- Integrate 49 physics questions from LaTeX into TTM
- Create aggressive adversarial versions for THLP/TAGP
- Update notebooks to use adversarial datasets
- Add visualization and calibration metrics
- Create submission template and guide

Datasets:
- thlp_mc_aggressive.csv: 274 Q (adversarial)
- ttm_physics_mc.csv: 199 Q (physics enhanced)
- tagp_mc_aggressive.csv: 851 Q (adversarial)
- tefb_mc_cleaned.csv: 1,512 Q (cleaned)
- tscp_mc_cleaned.csv: 25 Q (cleaned)

Expected Performance:
- THLP: 25-40% (adversarial)
- TTM: 10-25% (physics enhanced)
- TAGP: 20-35% (adversarial)
- TEFB: 50-70% (cleaned)
- TSCP: 60-80% (cleaned)"
```

## Push Commands

```bash
git push origin master
```

## Tag (Optional)

```bash
git tag -a v2.0.0-adversarial
git push origin v2.0.0-adversarial
```

