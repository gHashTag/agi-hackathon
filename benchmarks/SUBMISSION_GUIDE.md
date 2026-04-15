# 🚀 Пошаговая инструкция по подаче Trinity Cognitive Probes на Kaggle

**Дедлайн: 16 апреля 2026, 23:59 UTC (17 апреля 06:59 по Бангкоку)**

> У тебя ОДНА попытка подачи. Всё нужно сделать правильно с первого раза.

---

## Шаг 1: Создай 5 Task-ов (Kaggle Benchmark Tasks)

Для каждого трека нужно создать отдельный Kaggle Notebook с бенчмарком.

### 1.1 THLP (Learning)

1. Перейди на https://www.kaggle.com/benchmarks/tasks/new
2. Откроется новый Kaggle Notebook с предустановленным `kaggle-benchmarks`
3. **Добавь датасет**: Справа нажми "Add data" → найди `playra/trinity-cognitive-probes-thlp-mc` → добавь
4. **Вставь код** из файла `benchmark_thlp.py` (весь код целиком)
5. **Запусти ноутбук** (Run All)
6. Дождись завершения — увидишь результат типа "Results: 142/200 correct (71.0%)"
7. **В последней ячейке** раскомментируй и выполни: `%choose trinity_thlp_benchmark`
8. **Сохрани ноутбук** с названием: `trinity-thlp-learning-benchmark`

### 1.2 TTM (Metacognition)

1. https://www.kaggle.com/benchmarks/tasks/new
2. Добавь датасет: `playra/trinity-cognitive-probes-tmp-mc`
3. Вставь код из `benchmark_ttm.py`
4. Запусти → `%choose trinity_ttm_benchmark`
5. Сохрани как: `trinity-ttm-metacognition-benchmark`

### 1.3 TAGP (Attention)

1. https://www.kaggle.com/benchmarks/tasks/new
2. Добавь датасет: `playra/trinity-cognitive-probes-tagp-mc`
3. Вставь код из `benchmark_tagp.py`
4. Запусти → `%choose trinity_tagp_benchmark`
5. Сохрани как: `trinity-tagp-attention-benchmark`

### 1.4 TEFB (Executive Functions)

1. https://www.kaggle.com/benchmarks/tasks/new
2. Добавь датасет: `playra/trinity-cognitive-probes-tefb-mc`
3. Вставь код из `benchmark_tefb.py`
4. Запусти → `%choose trinity_tefb_benchmark`
5. Сохрани как: `trinity-tefb-executive-functions-benchmark`

### 1.5 TSCP (Social Cognition)

1. https://www.kaggle.com/benchmarks/tasks/new
2. Добавь датасет: `playra/trinity-cognitive-probes-tscp-mc`
3. Вставь код из `benchmark_tscp.py`
4. Запусти → `%choose trinity_tscp_benchmark`
5. Сохрани как: `trinity-tscp-social-cognition-benchmark`

---

## Шаг 2: Создай Benchmark (объединение всех 5 задач)

1. Перейди на https://www.kaggle.com/benchmarks/new (или через UI: Benchmarks → New Benchmark)
2. **Название**: `Trinity Cognitive Probes`
3. **Описание**: `Brain-inspired benchmarks evaluating 5 cognitive domains: Learning, Metacognition, Attention, Executive Functions, and Social Cognition. 66,133 MC questions mapped to neuroanatomical brain zones.`
4. **Добавь все 5 задач** (tasks), которые ты создал в Шаге 1
5. **Сохрани / Опубликуй** benchmark
6. **Запомни URL** — он будет типа `https://www.kaggle.com/benchmarks/playra/trinity-cognitive-probes`

### Важно: "Evaluate More Models"

После создания бенчмарка, нажми **"Evaluate More Models"** и добавь несколько моделей для сравнения:
- `google/gemini-2.5-pro`
- `google/gemini-2.5-flash`
- `meta/llama-3.1-70b`

Это создаст **градиент производительности** (критически важно для оценки — 30% балла).

---

## Шаг 3: Создай Writeup

1. Перейди на https://www.kaggle.com/competitions/kaggle-measuring-agi/writeups
2. Нажми **"New Writeup"**
3. **Заголовок**: `Trinity Cognitive Probes: Brain-Inspired Benchmarks for AGI Assessment`
4. **Текст**: Скопируй содержимое файла `WRITEUP.md` (1,028 слов — в лимите 1,500)
5. **Project Links** (ОБЯЗАТЕЛЬНО!):
   - **Benchmark**: Вставь URL бенчмарка из Шага 2
   - **Public Project Link**: Тот же URL бенчмарка
6. **Опционально**: Добавь ссылку на GitHub — `https://github.com/gHashTag/agi-hackathon`
7. **Опционально**: Добавь ссылку на ноутбук

---

## Шаг 4: Подай заявку (Submit)

1. На странице writeup нажми **"Submit"**
2. Подтверди подачу

⚠️ **У тебя ОДНА попытка!** Убедись что:
- [ ] Все 5 task-ов успешно прошли (зелёные)
- [ ] Benchmark создан и содержит все 5 задач
- [ ] Writeup содержит текст ≤1,500 слов
- [ ] Benchmark привязан к writeup в Project Links
- [ ] Public Benchmark URL указан

---

## Чеклист перед подачей

| # | Проверка | Статус |
|---|----------|--------|
| 1 | Все 5 ноутбуков выполнились без ошибок | ⬜ |
| 2 | `%choose` выполнен в каждом ноутбуке | ⬜ |
| 3 | Benchmark создан, содержит 5 задач | ⬜ |
| 4 | "Evaluate More Models" запущен (градиент!) | ⬜ |
| 5 | Writeup написан и ≤1,500 слов | ⬜ |
| 6 | Benchmark URL привязан к Writeup | ⬜ |
| 7 | Подача выполнена до 16.04 23:59 UTC | ⬜ |

---

## Таблица соответствия файлов

| Трек | Скрипт | Датасет Kaggle | CSV файл | Название ноутбука |
|------|--------|----------------|----------|-------------------|
| Learning | `benchmark_thlp.py` | `playra/trinity-cognitive-probes-thlp-mc` | `thlp_mc_new.csv` | `trinity-thlp-learning-benchmark` |
| Metacognition | `benchmark_ttm.py` | `playra/trinity-cognitive-probes-tmp-mc` | `ttm_mc_new.csv` | `trinity-ttm-metacognition-benchmark` |
| Attention | `benchmark_tagp.py` | `playra/trinity-cognitive-probes-tagp-mc` | `tagp_mc.csv` | `trinity-tagp-attention-benchmark` |
| Executive Functions | `benchmark_tefb.py` | `playra/trinity-cognitive-probes-tefb-mc` | `tefb_mc_new.csv` | `trinity-tefb-executive-functions-benchmark` |
| Social Cognition | `benchmark_tscp.py` | `playra/trinity-cognitive-probes-tscp-mc` | `tscp_mc_new.csv` | `trinity-tscp-social-cognition-benchmark` |

---

## Оценка (для понимания приоритетов)

| Критерий | Вес | На что обратить внимание |
|----------|-----|-------------------------|
| Качество датасета и задач | **50%** | Корректные ответы, чистый код, размер выборки |
| Новизна и дискриминативная сила | **30%** | ГРАДИЕНТ между моделями — не все 0% или 100% |
| Качество writeup | **20%** | Ясность, полнота, полезность для сообщества |

---

## Возможные проблемы

### TTM и TSCP — проблема с multiline в choices
Если ноутбук падает при загрузке CSV из-за `\n` в поле choices:
```python
# Замени pd.read_csv на:
df = pd.read_csv("/kaggle/input/...", quoting=1)  # QUOTE_ALL
```

### Ноутбук не видит датасет
Убедись что справа в панели "Data" добавлен правильный датасет. Путь должен быть `/kaggle/input/<slug>/filename.csv`.

### Таймаут при evaluate()
200 вопросов × 4 параллельных = ~50 последовательных вызовов. При 10 сек/вопрос = ~8 минут. Если таймаут, уменьши выборку до 100.
