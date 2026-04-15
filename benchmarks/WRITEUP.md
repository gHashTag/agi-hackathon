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

### Performance Gradient Across Models

| Track | Gemini 2.5 Flash | Gemini 2.5 Pro | Gemma 3 27B | Gemma 3 1B |
|-------|:-:|:-:|:-:|:-:|
| THLP (Learning) | 0.92 | — | — | — |
| TTM (Metacognition) | 0.67 | — | — | — |
| **TAGP (Attention)** | **0.38** | — | — | — |
| TEFB (Executive Fn) | 0.90 | — | — | — |
| TSCP (Social Cog) | 1.00 | — | — | — |
| **Aggregate** | **0.77** | pending | pending | pending |

(Pro, Gemma 27B, and Gemma 1B evaluations are running; results will update on the leaderboard.)

### Key Findings

1. **Attention is the strongest discriminator.** TAGP produced the lowest score (0.38) among all tracks for Gemini Flash — a frontier model achieving 0.90+ on other domains. This 52-percentage-point gap between Attention and Learning reveals that selective filtering under distraction is a fundamentally different capability from pattern recognition or planning.

2. **Distractor density drives failure.** Within TAGP, questions requiring identification of a specific error code or value buried in a multi-paragraph technical passage show the steepest accuracy drops. This suggests models process long contexts via shallow scanning rather than genuine attentional gating.

3. **Metacognition is the second hardest domain.** At 0.67, TTM questions that require detecting errors in plausible-sounding reasoning expose calibration weaknesses — models select confident-looking but incorrect answers.

4. **Cross-domain analysis reveals architectural insights.** The contrast between high Executive Function scores (0.90, requiring multi-step constraint satisfaction) and low Attention scores (0.38, requiring distractor suppression) suggests that transformer attention mechanisms are better at composing information than filtering it — a non-obvious finding given the architectural name.

### Conclusions

Trinity Cognitive Probes demonstrate that **attentional control is the most under-measured cognitive capability in current LLM evaluation**. While frontier models approach ceiling on learning, planning, and even social reasoning tasks, they struggle dramatically when required to filter noise — precisely the capability that enables all other cognition in biological systems.

The neuroscience-grounded design ensures the benchmark tests genuine cognitive processes rather than arbitrary categories. As models improve, the 8K+ question bank provides headroom for harder sampling strategies.

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
