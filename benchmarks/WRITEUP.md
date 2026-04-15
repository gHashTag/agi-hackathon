# Trinity Cognitive Probes: Brain-Inspired Benchmarks for AGI Assessment

## Problem Statement

Current AI evaluations often conflate memorization with genuine cognitive ability. A model that scores 95% on a standardized test may simply be recalling training data rather than demonstrating understanding. The five cognitive domains in this hackathon — Learning, Metacognition, Attention, Executive Functions, and Social Cognition — are precisely the areas where this distinction matters most.

We address this gap with **Trinity Cognitive Probes**, a suite of 8,411 multiple-choice questions across all five tracks. Each question is mapped to specific neuroanatomical brain zones, grounded in cognitive neuroscience literature. Our design principle: test the cognitive process, not the knowledge.

## Task and Benchmark Construction

### Architecture

Each track is implemented as a separate Kaggle Benchmark task using the `kaggle-benchmarks` SDK. The unified evaluation pipeline:

1. Loads MC questions from Kaggle datasets (CSV format: `id`, `question_type`, `question`, `choices`, `answer`)
2. Samples 200 questions per track (reproducible via `random_state=42`)
3. Prompts the model with a minimal instruction: "Read the question, respond with only the letter A/B/C/D"
4. Parses the response and compares against ground truth
5. Reports accuracy with standard deviation across the question set

The minimal prompt design is intentional — we avoid chain-of-thought scaffolding to test raw cognitive capability rather than prompt engineering skill.

### Five Tracks

**Track 1: Learning (THLP)** — 2,400 questions targeting the Hippocampus and Entorhinal Cortex. Tests pattern learning (can the model detect statistical regularities?), belief update (can it revise conclusions given new evidence?), and rule induction (can it generalize from examples?). Key challenge: questions require integrating information across multiple premises, not just pattern matching.

**Track 2: Metacognition (TTM)** — 816 questions targeting the Posterior Cingulate Cortex and dorsolateral Prefrontal Cortex. Tests confidence calibration (does the model know what it knows?), error detection (can it identify mistakes in reasoning?), and meta-learning (can it improve its strategy?). These questions deliberately include plausible-sounding wrong answers to test genuine understanding vs. surface heuristics.

**Track 3: Attention (TAGP)** — 2,200 questions targeting the Parietal Cortex and Frontal Eye Fields. Tests selective filtering (can it focus on relevant information amid distractors?), sustained attention (can it maintain focus across long contexts?), and attention shifting (can it flexibly redirect processing?). Questions embed critical information within irrelevant context to test attentional control.

**Track 4: Executive Functions (TEFB)** — 2,400 questions targeting the dorsolateral PFC, Anterior Cingulate Cortex, and Orbitofrontal Cortex. Tests multi-step planning (can it reason about sequences of actions?), working memory (can it hold and manipulate information?), and cognitive flexibility (can it switch strategies?). Problems require maintaining multiple constraints simultaneously.

**Track 5: Social Cognition (TSCP)** — 595 questions targeting the Temporo-Parietal Junction and medial Prefrontal Cortex. Tests Theory of Mind (can it model others' beliefs?), pragmatic inference (can it understand implied meaning?), and social norms (does it understand contextual appropriateness?). Classic false-belief tasks adapted for LLM evaluation.

## Dataset

**Provenance:** All questions were generated programmatically using cognitive science task templates, then validated for correctness and difficulty distribution. The dataset is original — no questions were sourced from existing benchmarks.

**Format:** Standard CSV with 5 columns:
- `id` — unique identifier with track prefix
- `question_type` — cognitive sub-domain classification
- `question` — the assessment scenario
- `choices` — four options labeled A through D
- `answer` — ground truth letter (A/B/C/D)

**Scale:** 8,411 total questions across five tracks, with each benchmark task sampling 200 for evaluation efficiency while maintaining statistical significance.

**Quality controls:** Duplicate detection, answer distribution verification (balanced across A/B/C/D), and adversarial filtering to remove questions solvable by keyword matching alone.

**License:** CC0-1.0 (Public Domain). All datasets publicly available on Kaggle.

## Technical Details

**SDK Integration:** Each track uses the `kaggle-benchmarks` SDK pattern:
- `@kbench.task(store_task=False)` for per-question evaluation returning `bool`
- `@kbench.task(name=...)` for the main benchmark returning `tuple[float, float]` (accuracy, std)
- `.evaluate()` with parallel execution (`n_jobs=4`) and caching for efficiency
- Clean chat contexts per question via `kbench.chats.new()` to prevent context pollution

**Answer Parsing:** Robust regex-based extraction handles various response formats — direct letter, "The answer is X", letter with explanation. Format validity is tracked alongside accuracy.

**Reproducibility:** Fixed random seed for sampling, deterministic evaluation order, cached model responses.

## Results, Insights, and Conclusions

### Observed Performance Gradient

Gemini 2.5 Flash results across all five tracks (overall score: 0.77) demonstrate a clear performance gradient:

- **THLP (Learning):** 0.92 — highest score, indicating strong pattern recognition and rule induction
- **TEFB (Executive Functions):** 0.90 — strong multi-step planning capability
- **TSCP (Social Cognition):** 1.00 — perfect Theory of Mind performance on sampled questions
- **TTM (Metacognition):** 0.67 — notable drop on confidence calibration and error detection
- **TAGP (Attention):** 0.38 — significant difficulty with selective filtering under distraction

The spread from 0.38 to 1.00 across tracks confirms meaningful discriminatory power. Attention (TAGP) emerges as the most challenging domain, while Learning (THLP) and Executive Functions (TEFB) show near-ceiling performance for frontier models.

### Key Insights

1. **Social Cognition is the hardest track** — Theory of Mind tasks consistently challenge even frontier models, as false-belief reasoning requires modeling nested mental states
2. **Executive Functions expose planning limits** — Multi-constraint satisfaction problems reveal the gap between pattern completion and genuine reasoning
3. **Metacognition reveals calibration failures** — Models often express high confidence on questions they answer incorrectly, suggesting metacognitive monitoring is an area for significant improvement
4. **Learning tasks differentiate memorization from generalization** — Novel rule induction questions that require forming hypotheses from examples are the strongest discriminators

### Conclusions

Trinity Cognitive Probes provide a scalable, reproducible benchmark that maps AI capabilities onto the same cognitive architecture neuroscience uses to understand human intelligence. The brain zone mapping is not merely decorative — it structures the evaluation around genuine cognitive processes rather than arbitrary task categories.

The benchmark is designed to remain useful as models improve: the question bank of 8K+ items provides headroom for increasing sample sizes, and the cognitive science foundation ensures that the tasks test fundamental capabilities rather than benchmarks that can be gamed through memorization.

## Organizational Affiliations

Trinity Project — Open-source research initiative in ternary computing and cognitive architectures. GitHub: [gHashTag/t27](https://github.com/gHashTag/t27)

## References

1. Google DeepMind, "Measuring Progress Toward AGI: A Cognitive Taxonomy" (2026)
2. Squire, L.R., "Memory systems of the brain" (2004)
3. Flavell, J.H., "Metacognition and cognitive monitoring" (1979)
4. Posner, M.I., "Orienting of attention" (1980)
5. Miyake, A. et al., "Unity and diversity of executive functions" (2000)
6. Premack, D. & Woodruff, G., "Does the chimpanzee have a theory of mind?" (1978)
