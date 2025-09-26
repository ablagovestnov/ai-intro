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
Пошагово объясните, что делает эта функция, и предложите более простую версию.
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
  `Замените axios на fetch в этом файле; сохраните строгую типизацию; обновите импорты только здесь.`  
- Просмотрите дифф и примените частично.