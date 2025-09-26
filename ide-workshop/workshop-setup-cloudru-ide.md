# Воркшоп (45–60 мин): Настройка трёх IDE под вашу модель на cloud.ru  
**IDE:** Cursor, VS Code, IntelliJ IDEA  
**Плагины:** Continue, Roo Code, Continue for JetBrains, CodeGPT / AI Coding (JetBrains)

---

## 0) Цель и результат
**Цель:** за 1 час вместе настроить три среды разработки так, чтобы они работали с вашей моделью на cloud.ru.  
**Результат:** участники смогут использовать чат/инлайн-подсказки/переписывания кода и агентные задачи в каждой IDE.

---

## 1) Быстрые вводные (5 мин)

**Данные для подключения (пример):**
- **Base URL:** `https://foundation-models.api.cloud.ru/v1`  
- **Model:** `Qwen/Qwen3-235B-A22B-Instruct-2507`  
- **API Key:** храните в переменной окружения

```bash
# macOS / Linux (bash/zsh)
export CLOUD_RU_API_KEY="<ВАШ_КЛЮЧ>"

# Windows (PowerShell)
setx CLOUD_RU_API_KEY "<ВАШ_КЛЮЧ>"
```

**Чек-лист перед стартом**
- Установлены Cursor, VS Code, IntelliJ IDEA (актуальные версии).
- Есть тестовый репозиторий/папка проекта.
- Есть рабочий API Key к cloud.ru (у каждого участника — свой).

---

## 2) План с таймингом (45–60 мин)

1. **VS Code** — Continue + Roo Code (15–20 мин)  
2. **IntelliJ IDEA** — Continue for JetBrains **или** CodeGPT/AI Coding (15–20 мин)  
3. **Cursor** — проверка/настройка + мини-практика (10–15 мин)  
4. **Финальный чек и типовые ошибки** (5 мин)

> Если времени мало: в IDEA выбираем **один** плагин (Continue *или* CodeGPT/AI Coding).

---

## 3) VS Code (15–20 мин)

### 3.1. Установка Continue
1. **Extensions** → найдите **Continue** → **Install**.  
2. Откройте **Continue: Settings** → вкладка **Providers/Models**.  
3. Добавьте провайдера **OpenAI Compatible** (или **OpenAI** с полем Base URL).  
4. Заполните:  
   - **Base URL:** `https://foundation-models.api.cloud.ru/v1`  
   - **API Key:** `$CLOUD_RU_API_KEY`  
   - **Model:** `Qwen/Qwen3-235B-A22B-Instruct-2507`  
5. Включите **Inline Suggestions** (по желанию) и задайте хоткеи.

**Проверка (1 мин):**  
В чате Continue:  
```
Explain this function step-by-step and propose a simpler version.
```
(на выделенном фрагменте кода)

---

### 3.2. Установка Roo Code
1. **Extensions** → найдите **Roo Code** → **Install**.  
2. В боковой панели **Roo** → ⚙️ **Settings**.  
3. **API Provider:** *OpenAI Compatible*.  
4. Поля:  
   - **Base URL:** `https://foundation-models.api.cloud.ru/v1`  
   - **API Key:** `$CLOUD_RU_API_KEY`  
   - **Model ID:** `Qwen/Qwen3-235B-A22B-Instruct-2507`  
5. **Save**.

**Проверка (1–2 мин):**  
- Нажмите **Plan**, задайте задачу:  
  `Replace axios with fetch in this file; keep strict types; update imports only here.`  
- Просмотрите дифф и примените частично.

---

## 4) IntelliJ IDEA (15–20 мин)

> Выберите **один** из плагинов ниже (если хватает времени — поставьте оба).

### Вариант A: Continue for JetBrains
1. **File → Settings → Plugins → Marketplace** → `Continue` → **Install** → перезапустите IDE.  
2. **File → Settings → Tools → Continue** (или иконка плагина).  
3. Провайдер **OpenAI / OpenAI Compatible**.  
4. Заполните:  
   - **Base URL:** `https://foundation-models.api.cloud.ru/v1`  
   - **API Key:** `$CLOUD_RU_API_KEY`  
   - **Model:** `Qwen/Qwen3-235B-A22B-Instruct-2507`  
5. **Apply/OK**.

**Проверка (1 мин):** выделите метод → спросите в чате:  
`Explain briefly, list pitfalls, suggest safer version.`

---

### Вариант B: CodeGPT **или** AI Coding (JetBrains)
1. **File → Settings → Plugins → Marketplace** → установите **CodeGPT** или **AI Coding** → перезапуск IDE.  
2. Откройте настройки плагина: **Tools → CodeGPT** (или **Tools → AI Coding**).  
3. Выберите **Custom / OpenAI Compatible**.  
4. Поля:  
   - **API Base URL:** `https://foundation-models.api.cloud.ru/v1`  
   - **API Key:** `$CLOUD_RU_API_KEY`  
   - **Model (name/ID):** `Qwen/Qwen3-235B-A22B-Instruct-2507`  
5. **Apply/OK**.

**Проверка (1–2 мин):**  
Команда плагина «Generate unit tests for …; JUnit5; cover edge cases.»

---

## 5) Cursor (10–15 мин)

> Если у части команды уже был настроен Cursor — просто быстро валидируем подключение и делаем 2 мини-упражнения.

### 5.1. Подключение
1. **Settings → Models**.  
2. Включите **Override OpenAI Base URL** → `https://foundation-models.api.cloud.ru/v1`.  
3. Введите **OpenAI API Key** → `$CLOUD_RU_API_KEY`.  
4. В **Models** добавьте/выберите: `Qwen/Qwen3-235B-A22B-Instruct-2507`.  
5. **Verify** (если есть) → сохранить.

### 5.2. Мини-практика
- **Rewrite:** выделите функцию →  
  `Convert to async/await; keep behavior; add minimal JSDoc.`  
- **Explain:** выделите стек-трейс →  
  `Explain root cause; propose minimal patch.`  
- **(Опционально) Composer:**  
  `Add input validation to POST /users using zod; return 400 on invalid; include tests.`

---

## 6) Быстрый чек/диагностика (5 мин)

**Типовые ошибки и решения**
- **401/403:** неверный ключ → проверьте `Authorization: Bearer <KEY>` и переменную `$CLOUD_RU_API_KEY`.  
- **404:** нет `/v1` в Base URL → укажите корень версии: `.../v1`.  
- **400/422:** модель не найдена → проверьте точное имя `Qwen/Qwen3-235B-A22B-Instruct-2507`.  
- **Timeout/медленно:** сократите выделение/контекст; разбейте задачу; увеличьте таймаут в настройках.  
- **Ничего не меняет:** проверьте права записи в файлы, перезапустите IDE, попробуйте меньший фрагмент.

**Критерии готовности**
- В **VS Code**: Continue отвечает и делает правки; Roo Code планирует и применяет дифф.  
- В **IDEA**: выбранный плагин генерирует ответы и правит код/тесты.  
- В **Cursor**: работают **Rewrite/Explain** (и **Composer** по желанию).

---

## 7) Шаблоны промптов (на раздатку)

**Explain (везде)**
```
Explain step-by-step what this function does, list edge cases, then propose a simpler alternative and discuss time/space complexity.
```

**Rewrite / Edit (локальные правки)**
```
Refactor to async/await, preserve exact behavior and types, minimal diff, add brief JSDoc to public functions.
```

**Агентная задача (Roo Code / Composer)**
```
Goal: Replace axios with native fetch across the project.
Constraints: Keep strict typing; no breaking changes; preserve error handling; update imports.
Deliverables: Updated files + passing linter/tests; short CHANGELOG.
Rules: Small focused changes; do not modify CI configs.
```

---

## 8) Финал
- Все три IDE подключены к одному endpoint.  
- Участники знают, где менять модель/ключ и как диагностировать ошибки.  
- Бонус: сохраните этот файл в репозитории команды или внутренней wiki.
