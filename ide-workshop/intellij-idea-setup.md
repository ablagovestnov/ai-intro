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
`Кратко объясните, перечислите подводные камни, предложите более безопасную версию.`

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
Команда плагина «Создайте модульные тесты для …; JUnit5; покройте граничные случаи.»