# Шаблоны промптов для команды

> Стандартизированные шаблоны для работы с AI-ассистентами. Все шаблоны следуют формуле: **Роль → Контекст → Задача → Ограничения → Формат ответа**.

---

## Шаблон 1: Декомпозиция задач

### Промпт
```
Роль: Senior Developer / Tech Lead
Контекст: [Описание проекта/модуля]
Задача: Разбей задачу "[описание задачи]" на подзадачи с DoD и рисками
Ограничения: 
- Укажи зависимости между подзадачами
- Дай реалистичные оценки времени
- Определи критерии приёмки для каждой подзадачи
- Выяви потенциальные риски и способы их митигации

Формат ответа: Таблица с колонками:
- Подзадача
- DoD (Definition of Done)
- Риски
- Время (часы)
- Зависимости
- Приоритет (High/Medium/Low)
```

### Пример использования
```
Роль: Senior Java Developer
Контекст: Spring Boot REST API для библиотеки
Задача: Разбей задачу "Реализовать систему бронирования книг" на подзадачи с DoD и рисками
Ограничения: 
- Укажи зависимости между подзадачами
- Дай реалистичные оценки времени
- Определи критерии приёмки для каждой подзадачи
- Выяви потенциальные риски и способы их митигации

Формат ответа: Таблица с колонками:
- Подзадача
- DoD (Definition of Done)
- Риски
- Время (часы)
- Зависимости
- Приоритет (High/Medium/Low)
```

### Ожидаемый результат
| Подзадача | DoD | Риски | Время | Зависимости | Приоритет |
|-----------|-----|-------|-------|-------------|-----------|
| Создать модель Reservation | Модель создана, валидация работает, тесты зелёные | Сложность валидации дат | 4ч | - | High |
| API для создания брони | Эндпоинт работает, возвращает 201, ошибки по RFC 7807 | Конфликты броней | 6ч | Модель Reservation | High |
| Проверка доступности | Логика работает, покрыта тестами | Производительность при высокой нагрузке | 8ч | API создания | Medium |

---

## Шаблон 2: Генерация тест-скелетов

### Промпт
```
Роль: QA Engineer / Test Developer
Контекст: [Описание модуля/функции для тестирования]
Задача: Сгенерируй тест-скелеты для [модуль/функция]
Ограничения:
- Покрой happy path, edge cases и ошибки
- Укажи, что нужно мокать
- Используй существующий стиль тестов в проекте
- Добавь проверки производительности где нужно

Формат ответа:
1. Код тестов (unit/integration/e2e)
2. Список моков с обоснованием
3. Тест-кейсы в виде таблицы
4. Рекомендации по покрытию
```

### Пример использования
```
Роль: QA Engineer
Контекст: Java Spring Boot, модуль BookService
Задача: Сгенерируй тест-скелеты для BookService.createBook()
Ограничения:
- Покрой happy path, edge cases и ошибки
- Укажи, что нужно мокать
- Используй существующий стиль тестов в проекте (JUnit 5, Mockito)
- Добавь проверки производительности где нужно

Формат ответа:
1. Код тестов (unit/integration/e2e)
2. Список моков с обоснованием
3. Тест-кейсы в виде таблицы
4. Рекомендации по покрытию
```

### Ожидаемый результат
```java
@ExtendWith(MockitoExtension.class)
class BookServiceTest {
    
    @Mock
    private BookRepository bookRepository;
    
    @Mock
    private ValidationService validationService;
    
    @InjectMocks
    private BookService bookService;
    
    @Test
    @DisplayName("Should create book successfully")
    void shouldCreateBookSuccessfully() {
        // Given
        BookCreateRequest request = BookCreateRequest.builder()
            .title("Test Book")
            .author("Test Author")
            .isbn("9780123456789")
            .build();
        
        Book savedBook = Book.builder()
            .id(1L)
            .title("Test Book")
            .build();
        
        when(validationService.validateIsbn("9780123456789")).thenReturn(true);
        when(bookRepository.save(any(Book.class))).thenReturn(savedBook);
        
        // When
        BookResponse result = bookService.createBook(request);
        
        // Then
        assertThat(result.getTitle()).isEqualTo("Test Book");
        verify(bookRepository).save(any(Book.class));
    }
    
    @Test
    @DisplayName("Should throw exception for invalid ISBN")
    void shouldThrowExceptionForInvalidIsbn() {
        // Given
        BookCreateRequest request = BookCreateRequest.builder()
            .isbn("invalid")
            .build();
        
        when(validationService.validateIsbn("invalid")).thenReturn(false);
        
        // When & Then
        assertThatThrownBy(() -> bookService.createBook(request))
            .isInstanceOf(ValidationException.class)
            .hasMessage("Invalid ISBN format");
    }
}
```

**Моки:**
- `BookRepository` — для изоляции от БД
- `ValidationService` — для контроля валидации
- `NotificationService` — для проверки уведомлений

**Тест-кейсы:**
| Сценарий | Входные данные | Ожидаемый результат |
|----------|----------------|-------------------|
| Успешное создание | Валидные данные | BookResponse с ID |
| Невалидный ISBN | ISBN не по формату | ValidationException |
| Дубликат ISBN | Существующий ISBN | DuplicateException |

---

## Шаблон 3: Генерация кода под тесты

### Промпт
```
Роль: Senior Developer
Контекст: [Описание проекта, стиль кода, архитектура]
Задача: Сделай patch для [функция/модуль] под эти тесты
Ограничения:
- Следуй стилю проекта (примеры кода прилагаются)
- Добавь логирование и обработку ошибок
- Соблюдай принципы SOLID
- Добавь метрики для мониторинга
- Безопасность: валидация входных данных

Формат ответа: Diff с изменениями, включая:
- Основной код
- Обработка ошибок
- Логирование
- Метрики
```

### Пример использования
```
Роль: Senior Java Developer
Контекст: Spring Boot 3.x, Java 17, существующий стиль проекта
Задача: Сделай patch для BookService.createBook() под эти тесты
Ограничения:
- Следуй стилю проекта (примеры кода прилагаются)
- Добавь логирование и обработку ошибок
- Соблюдай принципы SOLID
- Добавь метрики для мониторинга
- Безопасность: валидация входных данных

Примеры стиля:
[Здесь 20-40 строк существующего кода]

Формат ответа: Diff с изменениями, включая:
- Основной код
- Обработка ошибок
- Логирование
- Метрики
```

### Ожидаемый результат
```diff
+ @Service
+ @Slf4j
+ @Validated
+ public class BookService {
+ 
+     private final BookRepository bookRepository;
+     private final ValidationService validationService;
+     private final MeterRegistry meterRegistry;
+ 
+     public BookService(BookRepository bookRepository, 
+                        ValidationService validationService,
+                        MeterRegistry meterRegistry) {
+         this.bookRepository = bookRepository;
+         this.validationService = validationService;
+         this.meterRegistry = meterRegistry;
+     }
+ 
+     public BookResponse createBook(@Valid BookCreateRequest request) {
+         log.info("Creating book: title={}, author={}", 
+                 request.getTitle(), request.getAuthor());
+         
+         Timer.Sample sample = Timer.start(meterRegistry);
+         try {
+             // Валидация ISBN
+             if (!validationService.validateIsbn(request.getIsbn())) {
+                 meterRegistry.counter("api.book.create.validation_error").increment();
+                 throw new ValidationException("Invalid ISBN format: " + request.getIsbn());
+             }
+ 
+             // Проверка на дубликат
+             if (bookRepository.existsByIsbn(request.getIsbn())) {
+                 meterRegistry.counter("api.book.create.duplicate_error").increment();
+                 throw new DuplicateException("Book with ISBN " + request.getIsbn() + " already exists");
+             }
+ 
+             // Создание книги
+             Book book = Book.builder()
+                 .title(request.getTitle())
+                 .author(request.getAuthor())
+                 .isbn(request.getIsbn())
+                 .publicationYear(request.getPublicationYear())
+                 .genre(request.getGenre())
+                 .status(BookStatus.AVAILABLE)
+                 .build();
+ 
+             Book savedBook = bookRepository.save(book);
+             meterRegistry.counter("api.book.create.success").increment();
+             
+             log.info("Book created successfully: id={}, title={}", 
+                     savedBook.getId(), savedBook.getTitle());
+             
+             return BookResponse.from(savedBook);
+             
+         } catch (ValidationException | DuplicateException e) {
+             log.warn("Failed to create book: {}", e.getMessage());
+             throw e;
+         } catch (Exception e) {
+             log.error("Unexpected error creating book", e);
+             meterRegistry.counter("api.book.create.error").increment();
+             throw new ServiceException("Failed to create book", e);
+         } finally {
+             sample.stop(Timer.builder("api.book.create.duration")
+                     .register(meterRegistry));
+         }
+     }
+ }
```

---

## Шаблон 4: Самоаудит кода

### Промпт
```
Роль: Code Reviewer / Senior Developer
Контекст: [Описание проекта, стандарты качества]
Задача: Проверь этот код по чек-листу качества
Ограничения:
- Проверь безопасность, производительность, читаемость
- Проверь покрытие тестами и обработку ошибок
- Укажи конкретные проблемы с примерами исправлений
- Дай рекомендации по улучшению

Формат ответа: Таблица с результатами проверки:
- Категория (Безопасность/Производительность/Читаемость/Тесты/Ошибки)
- Статус (✅/❌/⚠️)
- Проблема (если есть)
- Рекомендация
```

### Пример использования
```
Роль: Code Reviewer
Контекст: Java Spring Boot проект, стандарты команды
Задача: Проверь этот код по чек-листу качества

[Здесь код для проверки]

Ограничения:
- Проверь безопасность, производительность, читаемость
- Проверь покрытие тестами и обработку ошибок
- Укажи конкретные проблемы с примерами исправлений
- Дай рекомендации по улучшению

Формат ответа: Таблица с результатами проверки:
- Категория (Безопасность/Производительность/Читаемость/Тесты/Ошибки)
- Статус (✅/❌/⚠️)
- Проблема (если есть)
- Рекомендация
```

### Ожидаемый результат
| Категория | Статус | Проблема | Рекомендация |
|-----------|--------|----------|--------------|
| Безопасность | ✅ | - | Валидация входных данных присутствует |
| Производительность | ⚠️ | Нет кэширования | Добавить @Cacheable для часто запрашиваемых данных |
| Читаемость | ✅ | - | Код хорошо структурирован, есть логирование |
| Тесты | ❌ | Отсутствуют тесты | Добавить unit тесты для всех публичных методов |
| Ошибки | ⚠️ | Общий catch | Заменить на специфичные исключения |

---

## Дополнительные шаблоны

### Шаблон 5: Рефакторинг
```
Роль: Senior Developer
Контекст: [Описание модуля для рефакторинга]
Задача: Рефакторинг [модуль/функция] для улучшения производительности и читаемости
Ограничения:
- Сохрани существующее поведение
- Улучши производительность
- Сделай код более читаемым
- Добавь документацию

Формат ответа: Diff с объяснением изменений
```

### Шаблон 6: Документация
```
Роль: Technical Writer
Контекст: [Описание API/модуля]
Задача: Создай документацию для [API/модуль]
Ограничения:
- Включи примеры использования
- Добавь диаграммы архитектуры
- Укажи ограничения и известные проблемы
- Следуй стандартам команды

Формат ответа: Markdown документация
```

### Шаблон 7: Миграция данных
```
Роль: Database Developer
Контекст: [Описание текущей и целевой схемы]
Задача: Создай план миграции данных из [источник] в [цель]
Ограничения:
- Минимизируй downtime
- Обеспечь откат изменений
- Проверь целостность данных
- Добавь мониторинг процесса

Формат ответа: Пошаговый план с SQL скриптами
```

---

## Интеграция в CONTRIBUTING.md

```markdown
# AI Prompts Templates

## Стандартные шаблоны для работы с AI

### 1. Декомпозиция задач
[Вставить шаблон 1]

### 2. Генерация тестов
[Вставить шаблон 2]

### 3. Генерация кода
[Вставить шаблон 3]

### 4. Самоаудит
[Вставить шаблон 4]

## Использование

1. Выберите подходящий шаблон
2. Заполните переменные в квадратных скобках
3. Добавьте контекст проекта
4. Укажите примеры существующего кода
5. Получите структурированный результат

## Примеры

[Добавить ссылки на примеры использования]
```

---

## Преимущества стандартизации

### ✅ Для команды:
- **Единый язык** общения с AI
- **Предсказуемые результаты** — все получают код в одном стиле
- **Экономия времени** — не нужно каждый раз объяснять требования
- **Качество** — все используют проверенные шаблоны

### ✅ Для проекта:
- **Консистентность** кода и архитектуры
- **Соблюдение стандартов** команды
- **Лучшее покрытие** тестами и документацией
- **Быстрая онбординг** новых разработчиков

### ✅ Для процесса:
- **Меньше ревью** — код уже соответствует стандартам
- **Быстрее разработка** — AI сразу даёт нужный результат
- **Меньше ошибок** — шаблоны включают проверки качества
- **Лучшая трассируемость** — все изменения документированы

Эти шаблоны превращают работу с AI из хаотичного процесса в структурированную практику!
