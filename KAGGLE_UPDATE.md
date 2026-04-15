# 📋 Инструкция по обновлению Kaggle датасетов с GitHub репозиторием

## ✅ Что уже сделано

- **GitHub репозиторий создан:** https://github.com/gHashTag/agi-hackathon
- **Все скрипты созданы:** test_single.py, fix_kaggle_datasets.py, evaluate.py
- **Промпты для оценки:** system_prompts.md, track_prompts.md

## 📝 Что нужно сделать на Kaggle

### Для каждого трека добавить в описание:

```
GitHub repo with evaluation framework and Kaggle dataset fixes.
See https://github.com/gHashTag/agi-hackathon for:
- Quick start guide (test evaluation scripts)
- Kaggle dataset fixes (fix multiline issues)
- Evaluation prompts for all models
```

### Быстрое обновление:

**THLP и TAGP** — уже готовы, описание пустое → добавить GitHub ссылку

**TTM и TEFB и TSCP** — описание содержит правильное количество строк ✅ → добавить GitHub ссылку и отметить "See GitHub for fixes"

---

## 🔄 Порядок действий

### Вариант 1: Через редактор на Kaggle
1. Открыть трек на Kaggle
2. Нажать "Edit" на вкладке Data Card
3. В поле "Add a description" ввести:
   ```
   GitHub repo with evaluation framework and Kaggle dataset fixes.
   See https://github.com/gHashTag/agi-hackathon for:
   - Quick start guide (test evaluation scripts)
   - Kaggle dataset fixes (fix multiline issues)
   - Evaluation prompts for all models
   ```
4. Нажать "Save Changes"

### Вариант 2: Через Kaggle CLI (если есть)
```bash
pip install kaggle
kaggle datasets version -p . -m "Add GitHub link to description"
kaggle datasets push
```

---

## 📊 Сводка по трекам

| Трек | GitHub ссылка добавлена? | Описание пустое? | Статус |
|------|-------------------|------------------|--------|
| **THLP** | ❌ Нет | ⚠️ Да | Нужно добавить |
| **TTM** | ❌ Нет | ✅ Нет | ОК, но можно добавить GitHub |
| **TAGP** | ❌ Нет | ⚠️ Да | Нужно добавить |
| **TEFB** | ❌ Нет | ✅ Нет | ОК, но можно добавить GitHub |
| **TSCP** | ❌ Нет | ✅ Нет | ОК, но можно добавить GitHub |

---

## 🎯 GitHub репозиторий

**URL:** https://github.com/gHashTag/agi-hackathon

**Что там:**
- Структура для оценки всех 5 треков
- Скрипты для тестирования перед хакатоном
- Промпты для оценки (system и track-specific)
- Инструкции по использованию
