# Пример правильного промпта: Java контроллер для сущности Book

> Детальный пример промпта для создания REST API контроллера с соблюдением всех практик из доклада.

---

## Контекст проекта

**Стек:** Java 17, Spring Boot 3.x, Spring Data JPA, OpenAPI 3, Maven

**Архитектура:** REST API с DTO, валидация через Bean Validation, обработка ошибок по RFC 7807

**Стиль кода:** Следуем существующим паттернам в проекте

---

## Промпт для AI

```
Роль: Senior Java Developer
Контекст: Spring Boot REST API проект

Задача: Создать контроллер для управления сущностью Book (книга) с поддержкой patch-операций

Требования:
1. Создать BookController с CRUD операциями
2. Создать BookPatchRequest для частичных обновлений (аналог pull request)
3. Создать OpenAPI спецификацию
4. Создать DTO для фронтенда
5. Добавить валидацию и обработку ошибок

Ограничения:
- Java 17, Spring Boot 3.x
- Используй существующие паттерны проекта
- Следуй RFC 7807 для ошибок
- Добавь логирование и метрики
- Безопасность: проверка ролей (ADMIN, USER)

Формат ответа: 
- Код контроллера
- DTO классы
- OpenAPI спецификация
- Примеры запросов/ответов

Примеры из проекта:
[Здесь  20-40 строк существующего кода контроллера для понимания стиля]

Сущность Book:
- id: Long (автогенерируемый)
- title: String (обязательное, 1-255 символов)
- author: String (обязательное, 1-100 символов)
- isbn: String (уникальный, формат ISBN-13)
- publicationYear: Integer (1800-2024)
- genre: String (enum: FICTION, NON_FICTION, SCIENCE, HISTORY)
- status: String (enum: AVAILABLE, BORROWED, RESERVED)
- createdAt: LocalDateTime
- updatedAt: LocalDateTime

BookPatchRequest должен содержать:
- fields: Map<String, Object> (поля для обновления)
- comment: String (комментарий к изменениям, как в PR)
- requestedBy: String (кто запросил изменения)
```

---

## Ожидаемый результат

### 1. BookController.java

```java
@RestController
@RequestMapping("/api/v1/books")
@Validated
@Slf4j
@Tag(name = "Books", description = "Book management API")
public class BookController {

    private final BookService bookService;
    private final MeterRegistry meterRegistry;

    public BookController(BookService bookService, MeterRegistry meterRegistry) {
        this.bookService = bookService;
        this.meterRegistry = meterRegistry;
    }

    @GetMapping
    @Operation(summary = "Get all books", description = "Retrieve paginated list of books")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<Page<BookResponseDto>> getAllBooks(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String genre,
            @RequestParam(required = false) String status) {
        
        log.info("Fetching books: page={}, size={}, genre={}, status={}", 
                page, size, genre, status);
        
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            Page<BookResponseDto> books = bookService.findAllBooks(page, size, genre, status);
            meterRegistry.counter("api.books.get.success").increment();
            return ResponseEntity.ok(books);
        } catch (Exception e) {
            meterRegistry.counter("api.books.get.error").increment();
            throw e;
        } finally {
            sample.stop(Timer.builder("api.books.get.duration").register(meterRegistry));
        }
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get book by ID", description = "Retrieve a specific book by its ID")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<BookResponseDto> getBookById(@PathVariable @Positive Long id) {
        log.info("Fetching book with id: {}", id);
        
        BookResponseDto book = bookService.findById(id);
        meterRegistry.counter("api.books.get_by_id.success").increment();
        return ResponseEntity.ok(book);
    }

    @PostMapping
    @Operation(summary = "Create new book", description = "Create a new book")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<BookResponseDto> createBook(@Valid @RequestBody BookCreateRequestDto request) {
        log.info("Creating new book: title={}, author={}", request.getTitle(), request.getAuthor());
        
        BookResponseDto book = bookService.createBook(request);
        meterRegistry.counter("api.books.create.success").increment();
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .header("Location", "/api/v1/books/" + book.getId())
                .body(book);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update book", description = "Full update of a book")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<BookResponseDto> updateBook(
            @PathVariable @Positive Long id,
            @Valid @RequestBody BookUpdateRequestDto request) {
        
        log.info("Updating book with id: {}", id);
        
        BookResponseDto book = bookService.updateBook(id, request);
        meterRegistry.counter("api.books.update.success").increment();
        return ResponseEntity.ok(book);
    }

    @PatchMapping("/{id}")
    @Operation(summary = "Patch book", description = "Partial update of a book (like PR)")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<BookPatchResponseDto> patchBook(
            @PathVariable @Positive Long id,
            @Valid @RequestBody BookPatchRequestDto request) {
        
        log.info("Patching book with id: {}, requested by: {}", id, request.getRequestedBy());
        
        BookPatchResponseDto response = bookService.patchBook(id, request);
        meterRegistry.counter("api.books.patch.success").increment();
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete book", description = "Delete a book by ID")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deleteBook(@PathVariable @Positive Long id) {
        log.info("Deleting book with id: {}", id);
        
        bookService.deleteBook(id);
        meterRegistry.counter("api.books.delete.success").increment();
        return ResponseEntity.noContent().build();
    }

    @ExceptionHandler(BookNotFoundException.class)
    public ResponseEntity<ErrorResponseDto> handleBookNotFound(BookNotFoundException ex) {
        log.warn("Book not found: {}", ex.getMessage());
        meterRegistry.counter("api.books.not_found").increment();
        
        ErrorResponseDto error = ErrorResponseDto.builder()
                .type("https://api.example.com/errors/book-not-found")
                .title("Book Not Found")
                .status(404)
                .detail(ex.getMessage())
                .timestamp(Instant.now())
                .build();
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponseDto> handleValidation(MethodArgumentNotValidException ex) {
        log.warn("Validation error: {}", ex.getMessage());
        meterRegistry.counter("api.books.validation_error").increment();
        
        List<String> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .collect(Collectors.toList());
        
        ErrorResponseDto error = ErrorResponseDto.builder()
                .type("https://api.example.com/errors/validation-failed")
                .title("Validation Failed")
                .status(400)
                .detail("Request validation failed")
                .errors(errors)
                .timestamp(Instant.now())
                .build();
        
        return ResponseEntity.badRequest().body(error);
    }
}
```

### 2. DTO классы

```java
// BookResponseDto.java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Book response data")
public class BookResponseDto {
    @Schema(description = "Book ID", example = "1")
    private Long id;
    
    @Schema(description = "Book title", example = "The Great Gatsby")
    private String title;
    
    @Schema(description = "Book author", example = "F. Scott Fitzgerald")
    private String author;
    
    @Schema(description = "ISBN-13", example = "9780743273565")
    private String isbn;
    
    @Schema(description = "Publication year", example = "1925")
    private Integer publicationYear;
    
    @Schema(description = "Book genre", example = "FICTION")
    private String genre;
    
    @Schema(description = "Book status", example = "AVAILABLE")
    private String status;
    
    @Schema(description = "Creation timestamp")
    private LocalDateTime createdAt;
    
    @Schema(description = "Last update timestamp")
    private LocalDateTime updatedAt;
}

// BookCreateRequestDto.java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Request to create a new book")
public class BookCreateRequestDto {
    @NotBlank(message = "Title is required")
    @Size(min = 1, max = 255, message = "Title must be between 1 and 255 characters")
    @Schema(description = "Book title", example = "The Great Gatsby", required = true)
    private String title;
    
    @NotBlank(message = "Author is required")
    @Size(min = 1, max = 100, message = "Author must be between 1 and 100 characters")
    @Schema(description = "Book author", example = "F. Scott Fitzgerald", required = true)
    private String author;
    
    @NotBlank(message = "ISBN is required")
    @Pattern(regexp = "^\\d{13}$", message = "ISBN must be 13 digits")
    @Schema(description = "ISBN-13", example = "9780743273565", required = true)
    private String isbn;
    
    @NotNull(message = "Publication year is required")
    @Min(value = 1800, message = "Publication year must be at least 1800")
    @Max(value = 2024, message = "Publication year must be at most 2024")
    @Schema(description = "Publication year", example = "1925", required = true)
    private Integer publicationYear;
    
    @NotNull(message = "Genre is required")
    @Schema(description = "Book genre", example = "FICTION", required = true)
    private BookGenre genre;
    
    @Builder.Default
    @Schema(description = "Book status", example = "AVAILABLE")
    private BookStatus status = BookStatus.AVAILABLE;
}

// BookPatchRequestDto.java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Request to patch a book (like PR)")
public class BookPatchRequestDto {
    @NotNull(message = "Fields to update are required")
    @Schema(description = "Fields to update", required = true)
    private Map<String, Object> fields;
    
    @NotBlank(message = "Comment is required")
    @Size(min = 10, max = 500, message = "Comment must be between 10 and 500 characters")
    @Schema(description = "Comment explaining the changes", example = "Update author name and fix ISBN", required = true)
    private String comment;
    
    @NotBlank(message = "Requested by is required")
    @Size(min = 1, max = 50, message = "Requested by must be between 1 and 50 characters")
    @Schema(description = "User who requested the changes", example = "john.doe", required = true)
    private String requestedBy;
}

// BookPatchResponseDto.java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Response to book patch request")
public class BookPatchResponseDto {
    @Schema(description = "Book ID", example = "1")
    private Long bookId;
    
    @Schema(description = "Fields that were updated")
    private Map<String, Object> updatedFields;
    
    @Schema(description = "Comment from the patch request")
    private String comment;
    
    @Schema(description = "User who requested the changes")
    private String requestedBy;
    
    @Schema(description = "Timestamp when patch was applied")
    private LocalDateTime appliedAt;
    
    @Schema(description = "Updated book data")
    private BookResponseDto book;
}
```

### 3. OpenAPI спецификация

```yaml
openapi: 3.0.3
info:
  title: Book Management API
  description: API for managing books with patch operations
  version: 1.0.0
  contact:
    name: API Support
    email: api-support@example.com

servers:
  - url: https://api.example.com
    description: Production server
  - url: https://staging-api.example.com
    description: Staging server

paths:
  /api/v1/books:
    get:
      summary: Get all books
      description: Retrieve paginated list of books with optional filtering
      tags:
        - Books
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          description: Page number (0-based)
          schema:
            type: integer
            minimum: 0
            default: 0
        - name: size
          in: query
          description: Page size
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: genre
          in: query
          description: Filter by genre
          schema:
            $ref: '#/components/schemas/BookGenre'
        - name: status
          in: query
          description: Filter by status
          schema:
            $ref: '#/components/schemas/BookStatus'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BookPageResponse'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '403':
          $ref: '#/components/responses/ForbiddenError'
        '500':
          $ref: '#/components/responses/InternalServerError'

    post:
      summary: Create new book
      description: Create a new book (Admin only)
      tags:
        - Books
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookCreateRequest'
      responses:
        '201':
          description: Book created successfully
          headers:
            Location:
              description: URL of the created book
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BookResponse'
        '400':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
        '403':
          $ref: '#/components/responses/ForbiddenError'

  /api/v1/books/{id}:
    get:
      summary: Get book by ID
      description: Retrieve a specific book by its ID
      tags:
        - Books
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          description: Book ID
          schema:
            type: integer
            format: int64
            minimum: 1
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BookResponse'
        '404':
          $ref: '#/components/responses/NotFoundError'

    put:
      summary: Update book
      description: Full update of a book (Admin only)
      tags:
        - Books
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          description: Book ID
          schema:
            type: integer
            format: int64
            minimum: 1
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookUpdateRequest'
      responses:
        '200':
          description: Book updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BookResponse'
        '400':
          $ref: '#/components/responses/ValidationError'
        '404':
          $ref: '#/components/responses/NotFoundError'

    patch:
      summary: Patch book
      description: Partial update of a book (like PR) (Admin only)
      tags:
        - Books
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          description: Book ID
          schema:
            type: integer
            format: int64
            minimum: 1
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/BookPatchRequest'
            examples:
              updateAuthor:
                summary: Update author name
                value:
                  fields:
                    author: "F. Scott Fitzgerald (Updated)"
                  comment: "Fix author name spelling"
                  requestedBy: "john.doe"
              updateStatus:
                summary: Update book status
                value:
                  fields:
                    status: "BORROWED"
                  comment: "Mark book as borrowed"
                  requestedBy: "librarian"
      responses:
        '200':
          description: Book patched successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BookPatchResponse'
        '400':
          $ref: '#/components/responses/ValidationError'
        '404':
          $ref: '#/components/responses/NotFoundError'

    delete:
      summary: Delete book
      description: Delete a book by ID (Admin only)
      tags:
        - Books
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          description: Book ID
          schema:
            type: integer
            format: int64
            minimum: 1
      responses:
        '204':
          description: Book deleted successfully
        '404':
          $ref: '#/components/responses/NotFoundError'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    BookResponse:
      type: object
      properties:
        id:
          type: integer
          format: int64
          example: 1
        title:
          type: string
          example: "The Great Gatsby"
        author:
          type: string
          example: "F. Scott Fitzgerald"
        isbn:
          type: string
          example: "9780743273565"
        publicationYear:
          type: integer
          example: 1925
        genre:
          $ref: '#/components/schemas/BookGenre'
        status:
          $ref: '#/components/schemas/BookStatus'
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time

    BookCreateRequest:
      type: object
      required:
        - title
        - author
        - isbn
        - publicationYear
        - genre
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 255
          example: "The Great Gatsby"
        author:
          type: string
          minLength: 1
          maxLength: 100
          example: "F. Scott Fitzgerald"
        isbn:
          type: string
          pattern: '^\d{13}$'
          example: "9780743273565"
        publicationYear:
          type: integer
          minimum: 1800
          maximum: 2024
          example: 1925
        genre:
          $ref: '#/components/schemas/BookGenre'
        status:
          $ref: '#/components/schemas/BookStatus'

    BookPatchRequest:
      type: object
      required:
        - fields
        - comment
        - requestedBy
      properties:
        fields:
          type: object
          description: Fields to update
          additionalProperties: true
          example:
            author: "F. Scott Fitzgerald (Updated)"
            status: "BORROWED"
        comment:
          type: string
          minLength: 10
          maxLength: 500
          example: "Fix author name spelling and update status"
        requestedBy:
          type: string
          minLength: 1
          maxLength: 50
          example: "john.doe"

    BookPatchResponse:
      type: object
      properties:
        bookId:
          type: integer
          format: int64
          example: 1
        updatedFields:
          type: object
          description: Fields that were updated
        comment:
          type: string
          example: "Fix author name spelling and update status"
        requestedBy:
          type: string
          example: "john.doe"
        appliedAt:
          type: string
          format: date-time
        book:
          $ref: '#/components/schemas/BookResponse'

    BookGenre:
      type: string
      enum:
        - FICTION
        - NON_FICTION
        - SCIENCE
        - HISTORY
      example: "FICTION"

    BookStatus:
      type: string
      enum:
        - AVAILABLE
        - BORROWED
        - RESERVED
      example: "AVAILABLE"

    BookPageResponse:
      type: object
      properties:
        content:
          type: array
          items:
            $ref: '#/components/schemas/BookResponse'
        pageable:
          type: object
        totalElements:
          type: integer
        totalPages:
          type: integer
        size:
          type: integer
        number:
          type: integer

    ErrorResponse:
      type: object
      properties:
        type:
          type: string
          format: uri
          example: "https://api.example.com/errors/book-not-found"
        title:
          type: string
          example: "Book Not Found"
        status:
          type: integer
          example: 404
        detail:
          type: string
          example: "Book with ID 123 not found"
        timestamp:
          type: string
          format: date-time
        errors:
          type: array
          items:
            type: string
          description: "Validation errors (only for 400 responses)"

  responses:
    ValidationError:
      description: Validation error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            type: "https://api.example.com/errors/validation-failed"
            title: "Validation Failed"
            status: 400
            detail: "Request validation failed"
            errors:
              - "title: Title is required"
              - "isbn: ISBN must be 13 digits"

    NotFoundError:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            type: "https://api.example.com/errors/book-not-found"
            title: "Book Not Found"
            status: 404
            detail: "Book with ID 123 not found"
            timestamp: "2024-01-15T10:30:00Z"

    UnauthorizedError:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

    ForbiddenError:
      description: Forbidden
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

    InternalServerError:
      description: Internal server error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
```

### 4. Примеры запросов/ответов

```bash
# Создание книги
POST /api/v1/books
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "9780743273565",
  "publicationYear": 1925,
  "genre": "FICTION",
  "status": "AVAILABLE"
}

# Ответ 201
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "9780743273565",
  "publicationYear": 1925,
  "genre": "FICTION",
  "status": "AVAILABLE",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z"
}

# Patch запрос (как PR)
PATCH /api/v1/books/1
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "fields": {
    "author": "F. Scott Fitzgerald (Updated)",
    "status": "BORROWED"
  },
  "comment": "Fix author name spelling and mark as borrowed",
  "requestedBy": "john.doe"
}

# Ответ 200
{
  "bookId": 1,
  "updatedFields": {
    "author": "F. Scott Fitzgerald (Updated)",
    "status": "BORROWED"
  },
  "comment": "Fix author name spelling and mark as borrowed",
  "requestedBy": "john.doe",
  "appliedAt": "2024-01-15T11:00:00Z",
  "book": {
    "id": 1,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald (Updated)",
    "isbn": "9780743273565",
    "publicationYear": 1925,
    "genre": "FICTION",
    "status": "BORROWED",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T11:00:00Z"
  }
}
```

---

## Ключевые особенности промпта

### ✅ Соблюдение практик из доклада:

1. **Роль + Контекст + Задача + Ограничения + Формат** — полная формула промпта
2. **Примеры из репо** — место для вставки существующего кода
3. **Конкретные ограничения** — версии, стиль, безопасность
4. **Явный формат ответа** — структурированный результат
5. **DoD критерии** — валидация, логирование, метрики, безопасность

### ✅ Что получили:

- **Полный контроллер** с CRUD + patch операциями
- **DTO классы** с валидацией
- **OpenAPI спецификация** для фронтенда
- **Обработка ошибок** по RFC 7807
- **Логирование и метрики** для мониторинга
- **Безопасность** через роли
- **Примеры запросов/ответов** для тестирования

Этот промпт демонстрирует, как правильно структурировать запрос к AI для получения production-ready кода!
