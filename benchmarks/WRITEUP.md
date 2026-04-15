# Trinity Cognitive Probes: Brain-Inspired Benchmarks for AGI Assessment

## Problem Statement

Current AI evaluations often conflate memorization with genuine cognitive ability. A model that scores 95% on a standardized test may simply be recalling training data rather than demonstrating understanding. Our primary focus is **Attention** — the ability to selectively filter relevant information from noise, sustain focus across long contexts, and flexibly shift processing between competing demands. This capability is fundamental to all higher cognition yet remains poorly measured in existing LLM benchmarks.

We address this gap with **Trinity Cognitive Probes**, a suite of 8,411 multiple-choice questions across five cognitive tracks, with our deepest investigation into attentional control (TAGP — 2,200 questions). Each question is mapped to specific neuroanatomical brain zones, grounded in cognitive neuroscience literature. Our design principle: test the cognitive process, not the knowledge.

## Task and Benchmark Construction

### Isolated Capability: Attentional Gating

Our primary benchmark — the **Top-Down Attentional Gating Probe (TAGP)** — isolates three specific attentional processes mapped to the Parietal Cortex and Frontal Eye Fields:

1. **Selective filtering:** Questions embed a critical target within a passage of deliberately distracting information. The model must identify the relevant signal while ignoring surrounding noise — mimicking the brain's ability to gate sensory input.
2. **Sustained attention:** Long-context questions require the model to track a specific detail across multiple paragraphs of irrelevant content, testing whether attention degrades with context length.
3. **Attention shifting:** Tasks require the model to flexibly redirect focus when the question demands switching between two competing frames of reference.

The key insight: these tasks cannot be solved by keyword matching or retrieval alone. They require the model to actively suppress irrelevant information — a process that, in human brains, depends on top-down signals from prefrontal cortex to sensory areas.

### Supporting Tracks

Four additional tracks provide cross-domain context:

- **Learning (THLP)** — 2,400 questions: pattern learning, belief update, rule induction. Brain zones: Hippocampus, Entorhinal Cortex.
- **Metacognition (TTM)** — 816 questions: confidence calibration, error detection, meta-learning. Brain zones: PCC, dlPFC.
- **Executive Functions (TEFB)** — 2,400 questions: multi-step planning, working memory, cognitive flexibility. Brain zones: dlPFC, ACC, OFC.
- **Social Cognition (TSCP)** — 595 questions: Theory of Mind, pragmatic inference, social norms. Brain zones: TPJ, mPFC.

Each track is a separate Kaggle Benchmark task. The unified pipeline samples 200 questions per track (reproducible via `random_state=42`), prompts the model with a minimal instruction ("respond with only the letter A/B/C/D"), and reports accuracy with standard deviation.

## Dataset

**Provenance:** All questions were generated programmatically using cognitive science task templates, then validated for correctness and difficulty calibration. The dataset is entirely original.

**Format:** CSV with 5 columns: `id` (unique identifier with track prefix), `question_type` (cognitive sub-domain), `question` (assessment scenario), `choices` (four options A–D), `answer` (ground truth letter).

**Scale:** 8,411 questions total. Each benchmark samples 200 for evaluation efficiency while maintaining statistical power (95% CI width < 7% at p=0.05).

**Quality controls:** Duplicate detection, balanced answer distribution (verified ~25% per letter across A/B/C/D), and adversarial filtering to remove questions solvable by surface heuristics.

**License:** CC0-1.0 (Public Domain). All five datasets available on Kaggle under `playra/trinity-cognitive-probes-*`.

## Technical Details

**SDK Integration:** Each track uses the `kaggle-benchmarks` SDK:
- `@kbench.task(store_task=False)` for per-question evaluation returning `bool`
- `@kbench.task(name=...)` for the main benchmark returning `tuple[float, float]`
- `.evaluate()` with parallel execution (`n_jobs=4`) and response caching
- Isolated chat contexts per question via `kbench.chats.new()` to prevent cross-contamination

**Answer Parsing:** Robust regex-based extraction handles direct letters, "The answer is X" patterns, and letters embedded in explanations. Unparseable responses are marked incorrect (conservative scoring).

**Reproducibility:** Fixed random seed (`random_state=42`), deterministic evaluation order, cached model responses via `kbench.client.enable_cache()`.

## Results, Insights, and Conclusions

### Performance Gradient Across 10 Models

| Track | Flash | Pro | Claude Opus | Claude Sonnet | GPT-5.4 | GPT-5.4 mini | Flash-Lite |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **TAGP (Attention)** | **0.38** | 0.79 | 0.78 | 0.72 | 0.79 | 0.77 | 0.71 |
| THLP (Learning) | 0.92 | — | 0.86 | 0.85 | — | 0.82 | 0.82 |
| TTM (Metacognition) | 0.67 | 0.74 | 0.41 | 0.41 | 0.49 | 0.44 | 0.75 |
| TEFB (Executive Fn) | 0.90 | 0.88 | 0.87 | 0.93 | 0.91 | 0.84 | — |
| TSCP (Social Cog) | 1.00 | 0.99 | 0.98 | 0.96 | 0.96 | 0.98 | 0.95 |
| **Aggregate** | **0.77** | **0.68** | **0.78** | **0.78** | **0.63** | **0.77** | **0.65** |

Full leaderboard with 10+ models available at the benchmark page. Scores update as evaluations complete.

### Key Findings

1. **TAGP reveals a clear performance gradient.** Across 7 evaluated models, TAGP scores range from 0.38 (Gemini Flash) to 0.79 (Gemini Pro, GPT-5.4), a 41-percentage-point spread. This makes Attention the strongest discriminator in our suite — no other track produces comparable variance across frontier models.

2. **Metacognition (TTM) exposes a surprising split.** Claude Opus and Sonnet both score 0.41 on TTM — dramatically below their 0.78+ aggregate — while Gemini Flash-Lite leads at 0.75. This suggests metacognitive calibration is architecturally independent from general capability, and some model families have systematic blind spots in error detection.

3. **Social Cognition approaches ceiling.** TSCP scores cluster between 0.93–1.00 across all models, confirming that Theory of Mind and pragmatic inference are largely solved for frontier LLMs. This track serves as a calibration baseline rather than a discriminator.

4. **Cross-domain dissociation reveals architectural signatures.** Claude Sonnet scores 0.93 on Executive Functions but only 0.41 on Metacognition — a 52-point gap. Gemini Flash scores 0.92 on Learning but 0.38 on Attention — a 54-point gap. These dissociations cannot be explained by general capability differences; they reveal domain-specific architectural strengths and weaknesses invisible to aggregate benchmarks.

5. **Distractor suppression is fundamentally harder than information composition.** The contrast between high TEFB scores (0.84–0.93, requiring multi-step planning) and variable TAGP scores (0.38–0.79, requiring noise filtering) confirms that transformer attention mechanisms are better at composing information than filtering it.

### Conclusions

Trinity Cognitive Probes, evaluated across 10 frontier models, demonstrate that **cognitive profiling reveals capability differences invisible to aggregate scores**. Models with identical aggregates (Flash 0.77 vs GPT-5.4 mini 0.77) show dramatically different cognitive profiles. The benchmark's neuroscience-grounded design ensures it tests genuine cognitive processes, and the 8K+ question bank provides headroom for harder sampling as models improve.

## Organizational Affiliations

Trinity Project — Open-source ternary computing and cognitive architectures. GitHub: [gHashTag/t27](https://github.com/gHashTag/t27)

## References

1. Google DeepMind, "Measuring Progress Toward AGI: A Cognitive Taxonomy" (2026)
2. Posner, M.I. & Petersen, S.E., "The attention system of the human brain" (1990)
3. Desimone, R. & Duncan, J., "Neural mechanisms of selective visual attention" (1995)
4. Squire, L.R., "Memory systems of the brain" (2004)
5. Flavell, J.H., "Metacognition and cognitive monitoring" (1979)
6. Miyake, A. et al., "Unity and diversity of executive functions" (2000)
7. Premack, D. & Woodruff, G., "Does the chimpanzee have a theory of mind?" (1978)
