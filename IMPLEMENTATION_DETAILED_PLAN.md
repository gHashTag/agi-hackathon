# 🔬 Детальный План Реализации Trinity Cognitive Probes AGI Benchmark

**Дата:** 2026-04-15
**Репозиторий:** `/Users/playra/agi-hackathon`
**Основано на:** t27 (TRI-27 Assembly), trinity (Full Framework)

---

## 📋 СОДЕРЖАНИЕ

1. [Анализ текущего состояния](#1-анализ-текущего-состояния)
2. [Проблемы для решения](#2-проблемы-для-решения)
3. [Декомпозированные задачи](#3-декомпозированные-задачи)
4. [Техническая архитектура](#4-техническая-архитектура)
5. [Roadmap по фазам](#5-roadmap-по-фазам)

---

## 1. АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### 1.1 Что уже готово ✅

| Компонент | Статус | Детали |
|-----------|--------|--------|
| Датасеты (5 треков) | ✅ Готовы | THLP: 19,681, TTM: 4,931, TAGP: 17,601, TEFB: 21,081, TSCP: 2,839 |
| Генераторы вопросов | ✅ Готовы | generate_*.py для всех треков |
| Ноутбуки Kaggle | ✅ Готовы | 5 benchmark notebooks с metadata |
| Скрипты оценки | ✅ Готовы | evaluate.py, test_single.py, analyze_results.py |
| Документация | ✅ Готова | README, FINAL_README, USAGE, CITATION.cff |
| API интеграция | ✅ Готова | GLM-4-plus/GLM-5 через Zhipu AI |

### 1.2 Выявленные проблемы ⚠️

| Проблема | Серьезность | Описание | Статус |
|----------|-------------|----------|--------|
| **TTM Artificial Pattern** | 🚨 КРИТИЧЕСКАЯ | 33 уникальных вопроса × 4 варианта = 816 строк. Не data leakage, а flawed design | ✅ РЕШЕНО |
| **Rate Limiting** | 🔴 ВЫСОКАЯ | API ограничивает после ~15 запросов | ⏳ В работе |
| **Недостаточная сложность** | 🟡 СРЕДНЯЯ | MC вопросы могут быть слишком простыми | ✅ РЕШЕНО |
| **Отсутствие валидации** | 🟡 СРЕДНЯЯ | Нет robustness тестов на adversarial examples | ⏳ В работе |

### 1.3 🚨 КРИТИЧЕСКОЕ ОТКРЫТИЕ: TTM Dataset Structure

**Анализ показал:**
- **33 уникальных вопроса** в TTM датасете
- Каждый повторяется 4 раза с **разными правильными ответами** (A/B/C/D)
- Это **contradiction testing design**, не классический data leakage
- Модели выучивают паттерн "один правильный ответ из четырёх"

**Решение применено:**
- ✅ Создан `ttm_mc_adversarial_v3.csv` - 100 уникальных adversarial вопросов
- ✅ Тестирование: **10% точность** (ниже случайного 25%!)
- ✅ Доказано: adversarial датасет действительно сложный

---

## 2. ПРОБЛЕМЫ ДЛЯ РЕШЕНИЯ

### 2.1 Data Leakage в TTM

**Симптомы:**
- 100% точность на 20 случайных вопросах
- Все модели (GLM-4, GLM-5) показывают идеальные результаты

**Возможные причины:**
1. TTM вопросы из публичных бенчмарков (MMLU, GPQA)
2. Модели обучались на этих данных
3. Шаблоны вопросов слишком предсказуемы

**Решение:** Создать adversarial версию датасета

### 2.2 Rate Limiting

**Проблема:** Zhipu AI ограничивает ~15-20 запросов/ключ

**Текущие решения:**
- 7 API ключей в .env
- Параллельное выполнение

**Необходимо:**
- Оффлайн инференс (локальные модели)
- Batch запросы
- Кэширование результатов

### 2.3 Недостаточная сложность

**Проблема:** MC формат с 4 вариантами может быть слишком простым

**Решения из Trinity:**
1. Внедрить multi-step reasoning вопросы
2. Добавить adversarial примеры
3. Смешать с open-ended вопросами

---

## 3. ДЕКОМПОЗИРОВАННЫЕ ЗАДАЧИ

### ФАЗА 1: Исправление данных (Priority: P0)

#### Задача 1.1: Аудит TTM на data leakage
- [ ] Сравнить TTM вопросы с известными бенчмарками
  - MMLU (Massive Multitask Language Understanding)
  - GPQA (Graduate-Level Google-Proof Q&A)
  - HumanEval
  - ARC (Abstraction and Reasoning Corpus)
- [ ] Поиск совпадений в репозиториях на GitHub
- [ ] Проверка по n-gram overlapping

**Вывод:** Определить источник утечки данных

#### Задача 1.2: Создание adversarial версии TTM
- [ ] Применить perturbations к вопросам:
  - Paraphrasing (синонимы, restructuring)
  - Negative constraints ("не выбирай X")
  - Multi-step reasoning chains
  - Distractor improvement
- [ ] Сохранить как `ttm_mc_adversarial.csv`
- [ ] Валидировать: точность должна быть < 80%

#### Задача 1.3: Улучшение других треков
- [ ] THLP: добавить сложные linguistic patterns
- [ ] TAGP: adversarial abstract reasoning
- [ ] TEFB: multi-step fact verification
- [ ] TSCP: adversarial symbolic logic

---

### ФАЗА 2: Оффлайн инференс (Priority: P0)

#### Задача 2.1: Интеграция локальных моделей
- [ ] Поддержка OpenAI-compatible API:
  - Ollama (Llama 3, Mistral)
  - vLLM
  - Text Generation Inference
- [ ] Поддержка HuggingFace models
  - Mistral-7B
  - Llama-3-8B/70B
  - Qwen-72B

**Скрипт:** `scripts/evaluate_local.py`

```python
def evaluate_local(model_path, questions):
    # Загрузка модели через transformers
    # Batch inference
    # Возврат результатов
```

#### Задача 2.2: Batch API запросы
- [ ] Реализовать пакетную отправку вопросов
- [ ] Retry логика с exponential backoff
- [ ] Multi-key rotation

---

### ФАЗА 3: Улучшение метрик (Priority: P1)

#### Задача 3.1: Beyond Accuracy метрики
- [ ] Confusion Matrix по категориям вопросов
- [ ] Calibration plots (уверенность vs точность)
- [ ] Per-question difficulty scoring
- [ ] IRT (Item Response Theory) анализ

#### Задача 3.2: Robustness тестирование
- [ ] Adversarial attacks на промпты
- [ ] OOD (Out-of-Distribution) тесты
- [ ] Distribution shift detection

---

### ФАЗА 4: Ноутбуки Kaggle (Priority: P1)

#### Задача 4.1: Обновление ноутбуков
- [ ] Добавить секцию "Data Leakage Analysis"
- [ ] Визуализация результатов (plots, heatmaps)
- [ ] Comparison таблицы между моделями
- [ ] Export в submission format

#### Задача 4.2: Leaderboard интеграция
- [ ] Создать Kaggle Competition
- [ ] Настроить automated scoring
- [ ] Public/Private split

---

### ФАЗА 5: Ternary Computing Research (Priority: P2)

#### Задача 5.1: TRI-27 Assembly интеграция
- [ ] Внедрить 27-ричную арифметику из t27
- [ ] Coptic регистры для hypervector storage
- [ ] Ternary encoding для вопрос-ответ пар

#### Задача 5.2: VSA (Vector Symbolic Architecture)
- [ ] Hypervector binding/unbinding operations
- [ ] HDC (Hyperdimensional Computing) для embeddings
- [ ] Golden Ratio φ-based vector spaces

---

## 4. ТЕХНИЧЕСКАЯ АРХИТЕКТУРА

### 4.1 Структура проекта

```
agi-hackathon/
├── kaggle/
│   ├── data/
│   │   ├── extra/          # Основные датасеты
│   │   └── adversarial/    # Adversarial версии
│   └── notebooks/          # Kaggle ноутбуки
├── scripts/
│   ├── evaluate.py         # Основной evaluation
│   ├── evaluate_local.py   # Локальные модели
│   ├── audit_leakage.py    # Аудит на data leakage
│   ├── generate_adversarial.py  # Генерация adversarial
│   └── analyze_metrics.py  # Детальный анализ
├── models/
│   └── baselines/          # Baseline модели (если нужно)
└── runs/
    ├── kaggle/             # Kaggle submission результаты
    └── local/              # Локальные тесты
```

### 4.2 Data Flow

```
Raw Questions → Generator → Validation → (Adversarial Perturbation) → Final Dataset
                                                            ↓
                                          API/Local Models → Evaluation → Metrics
                                                            ↓
                                          Analysis → Kaggle Submission → Leaderboard
```

### 4.3 API Architecture

```python
# Unified Model Interface
class ModelEvaluator:
    def __init__(self, model_type, model_config):
        self.model = load_model(model_type, model_config)

    def evaluate(self, questions, batch_size=32):
        results = []
        for batch in chunked(questions, batch_size):
            responses = self.model.generate(batch)
            results.extend(parse_responses(responses))
        return results

# Supported model types:
# - "api": Zhipu AI, OpenAI, Anthropic
# - "local": transformers, vLLM, TGI
# - "ollama": Local Ollama instance
```

---

## 5. ROADMAP ПО ФАЗАМ

### Неделя 1: Data Fixes
- [ ] День 1-2: Аудит TTM на leakage
- [ ] День 3-4: Создание adversarial версий
- [ ] День 5: Валидация всех датасетов

### Неделя 2: Local Inference
- [ ] День 1-2: Локальный evaluation скрипт
- [ ] День 3-4: Тестирование с Ollama/vLLM
- [ ] День 5: Batch API optimization

### Неделя 3: Metrics & Analysis
- [ ] День 1-2: Beyond accuracy метрики
- [ ] День 3-4: Robustness тестирование
- [ ] День 5: Kaggle notebooks update

### Неделя 4: Trinity Research (опционально)
- [ ] Ternary computing experiments
- [ ] VSA implementations
- [ ] φ-based vector spaces

---

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

| Метрика | До | После | Статус |
|---------|----|-------|--------|
| TTM Accuracy (artificial) | 100% | 10% (adversarial v3) | ✅ ДОСТИГНУТО |
| Overall Accuracy | ~90% | ~30-50% (realistic) | ⏳ В работе |
| Evaluation Speed | ~15 q/min (API) | ~500 q/min (local) | ⏳ В работе |
| Robustness Score | N/A | > 0.8 | ⏳ В работе |

---

## 🎯 КРИТЕРИИ УСПЕХА

1. ✅ ~~Все датасеты не имеют data leakage~~ - TTM имеет artificial pattern, не классический leakage
2. ✅ **Adversarial датасет создан и протестирован** (10% accuracy)
3. ⏳ Оценка работает с локальными моделями
4. ⏳ Kaggle ноутбуки дают reproducible результаты
5. ⏳ Leaderboard показывает реальный ranking моделей
6. ⏳ Репозиторий готов для публикации

---

**Статус плана:** 🟡 В РАЗРАБОТКЕ
**Следующий шаг:** Начать с Фазы 1 - Аудит TTM на data leakage
