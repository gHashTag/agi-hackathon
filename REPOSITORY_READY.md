# ✅ Репозиторий AGI Hackathon - Готов к работе!

**Статус:** Все скрипты и файлы созданы

---

## 📁 Созданная структура

```
~/agi-hackathon/
├── README.md                    # Обзор хакатона
├── USAGE.md                     # Руководство
├── requirements.txt               # Зависимости Python
├── data/                        # Папка для данных
│   ├── thlp/
│   │   └── sample_mc.csv        # (созда при download_data.sh)
│   ├── ttm/
│   │   └── sample_mc.csv        # (создаётся)
│   ├── tagp/
│   │   └── sample_mc.csv        # (создаётся)
│   ├── tefb/
│   │   └── sample_mc.csv        # (создаётся)
│   └── tscp/
│       └── sample_mc.csv        # (создаётся)
├── prompts/                      # AI промпты
│   ├── system_prompts.md          # Базовый системный промпт
│   └── track_prompts.md           # Специфические промпты для каждого трека
└── scripts/                      # Скрипты
    ├── download_data.sh           # ✅ Скачать данные с Kaggle
    ├── evaluate.py                # ✅ Полная оценка всех 5 треков
    ├── test_single.py             # ✅ Быстрый тест одного вопроса (уже был)
    └── fix_kaggle_datasets.py    # ✅ Исправить проблемы Kaggle датасетов
```

---

## 🚀 Что можно сделать прямо сейчас

### 1. Протестировать работу
```bash
cd ~/agi-hackathon
python3 scripts/test_single.py --track thlp
```

### 2. Скачать данные с Kaggle
```bash
cd ~/agi-hackathon
./scripts/download_data.sh all
```

### 3. Полная оценка
```bash
cd ~/agi-hackathon
python3 scripts/evaluate.py --track all --responses path/to/ai_responses.json
```

### 4. Исправить Kaggle датасеты
```bash
cd ~/agi-hackathon
python3 scripts/fix_kaggle_datasets.py --track all
```

---

## 📊 Статус Kaggle датасетов (из t27 репозитория)

| Трек | Статус | Проблемы | Исправления |
|------|--------|----------|-------------|
| THLP  | ✅ Онлайн | ✅ Нет | ✅ Исправлен multiline |
| TTM  | ✅ Онлайн | ✅ Multiline | ✅ Исправлен multiline |
| TAGP  | ✅ Онлайн | ✅ Пустое About | ✅ Есть описания |
| TEFB  | ✅ Онлайн | ✅ Устарелое число | ✅ Исправлен файл |
| TSCP  | ✅ Онлайн | ✅ Лицензия MIT | ✅ CC0 добавлен |

---

## 💡 Заметки

1. **Все скрипты исполняемы** — `chmod +x` применено
2. **Описание About** на Kaggle может не обновиться автоматически — можно обновить вручную через UI Kaggle
3. **V5 файлы** в t27 репозитории были повреждены — используются v2 файлы (ttm_mc_new.csv, tscp_mc.csv)
4. **Промпты** созданы для Claude, Gemini и GPT-4o — можно использовать любой

---

## 📚 Документация

### README.md
- Обзор хакатона DeepMind x Kaggle
- Структура треков
- Инструкция по запуску

### USAGE.md
- Краткое руководство
- Как использовать скрипты
- Как запустить оценку

### requirements.txt
- Python >= 3.10
- anthropic >= 0.25.0
- pandas >= 2.0.0
- kaggle CLI

### prompts/
- system_prompts.md — Базовый промпт для всех моделей
- track_prompts.md — Специфические промпты для каждого из 5 треков

### scripts/
- download_data.sh — Скачть данные с Kaggle
- evaluate.py — Полная оценка с JSON выводом
- test_single.py — Быстрый тест одного вопроса
- fix_kaggle_datasets.py — Исправить проблемы и перезагрузить

---

## 🔗 Полезные ссылки

- Конкурс: https://www.kaggle.com/competitions/kaggle-measuring-agi
- Kaggle Docs: https://www.kaggle.com/docs/api
- Trinity Source: https://github.com/gHashTag/t27
- Hackathon Repo: https://github.com/gHashTag/agi-hackathon

---

**Готово к работе! 🚀**
