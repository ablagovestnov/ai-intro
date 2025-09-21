# Руководство по реализации RAG для персонализации AI

> Детальное руководство по настройке RAG (Retrieval-Augmented Generation) для локальных моделей типа Qwen Code с объяснением метрик эффективности.

---

## Что такое RAG и зачем он нужен

**RAG (Retrieval-Augmented Generation)** — это техника, которая дополняет языковые модели релевантным контекстом из вашей кодовой базы. Вместо того чтобы полагаться только на обучение модели, мы даём ей доступ к актуальной информации о вашем проекте.

### Преимущества RAG:
- **Актуальность**: модель знает текущее состояние кода
- **Контекстность**: ответы основаны на ваших паттернах и решениях
- **Безопасность**: можно контролировать, к какой информации есть доступ
- **Персонализация**: модель адаптируется под стиль вашей команды

---

## Реализация RAG для Qwen Code

### Шаг 1: Подготовка данных для индексации

**Что индексируем:**
```bash
# Структура данных для RAG
project/
├── code/                    # Исходный код
│   ├── src/
│   ├── tests/
│   └── docs/
├── architecture/            # Архитектурные решения
│   ├── ADR/               # Architecture Decision Records
│   ├── diagrams/          # Диаграммы архитектуры
│   └── design-docs/       # Дизайн-документы
├── tickets/               # Тикеты и требования
│   ├── user-stories/
│   ├── bug-reports/
│   └── feature-requests/
└── knowledge-base/       # База знаний
    ├── coding-standards/
    ├── best-practices/
    └── troubleshooting/
```

**Скрипт подготовки данных:**
```python
import os
import json
from pathlib import Path
from typing import List, Dict

class CodeIndexer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.indexed_files = []
    
    def extract_code_context(self, file_path: Path) -> Dict:
        """Извлекает контекст из файла кода"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'file_path': str(file_path.relative_to(self.project_root)),
            'content': content,
            'file_type': file_path.suffix,
            'size': len(content),
            'language': self._detect_language(file_path.suffix)
        }
    
    def extract_adr_context(self, file_path: Path) -> Dict:
        """Извлекает контекст из ADR файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим структуру ADR
        lines = content.split('\n')
        title = lines[0].replace('# ', '') if lines[0].startswith('#') else 'Unknown'
        
        return {
            'file_path': str(file_path.relative_to(self.project_root)),
            'title': title,
            'content': content,
            'type': 'ADR',
            'decision_date': self._extract_date(content)
        }
    
    def index_project(self) -> List[Dict]:
        """Индексирует весь проект"""
        indexed_data = []
        
        # Индексируем код
        for code_file in self.project_root.rglob('*.{py,java,js,ts,go,rs}'):
            if self._should_index_file(code_file):
                indexed_data.append(self.extract_code_context(code_file))
        
        # Индексируем ADR
        for adr_file in self.project_root.rglob('ADR-*.md'):
            indexed_data.append(self.extract_adr_context(adr_file))
        
        # Индексируем документацию
        for doc_file in self.project_root.rglob('*.md'):
            if 'README' in doc_file.name or 'docs' in str(doc_file):
                indexed_data.append(self.extract_code_context(doc_file))
        
        return indexed_data
    
    def _should_index_file(self, file_path: Path) -> bool:
        """Определяет, нужно ли индексировать файл"""
        # Исключаем большие файлы, тесты, конфиги
        exclude_patterns = [
            'node_modules', '.git', '__pycache__', 
            'target', 'build', 'dist', '.venv'
        ]
        
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                return False
        
        # Исключаем файлы больше 10KB
        if file_path.stat().st_size > 10240:
            return False
        
        return True
    
    def _detect_language(self, suffix: str) -> str:
        """Определяет язык программирования по расширению"""
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.rs': 'rust'
        }
        return language_map.get(suffix, 'unknown')

# Использование
indexer = CodeIndexer('/path/to/your/project')
indexed_data = indexer.index_project()
```

### Шаг 2: Создание векторной базы данных

**Используем ChromaDB для хранения эмбеддингов:**

```python
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json

class RAGDatabase:
    def __init__(self, db_path: str = "./rag_db"):
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Используем специализированную модель для кода
        self.embedding_model = SentenceTransformer('microsoft/codebert-base')
        
        # Создаём коллекцию для кода
        self.code_collection = self.client.get_or_create_collection(
            name="code_context",
            metadata={"description": "Code context for RAG"}
        )
    
    def add_code_context(self, indexed_data: List[Dict]):
        """Добавляет контекст кода в векторную базу"""
        documents = []
        metadatas = []
        ids = []
        
        for i, item in enumerate(indexed_data):
            # Создаём документ с контекстом
            if item.get('type') == 'ADR':
                doc = f"ADR: {item['title']}\n{item['content']}"
            else:
                doc = f"File: {item['file_path']}\n{item['content']}"
            
            documents.append(doc)
            metadatas.append({
                'file_path': item['file_path'],
                'file_type': item.get('file_type', 'unknown'),
                'language': item.get('language', 'unknown'),
                'size': item.get('size', 0)
            })
            ids.append(f"doc_{i}")
        
        # Добавляем в коллекцию
        self.code_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search_relevant_context(self, query: str, n_results: int = 5) -> List[Dict]:
        """Ищет релевантный контекст для запроса"""
        results = self.code_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        relevant_contexts = []
        for i, doc in enumerate(results['documents'][0]):
            relevant_contexts.append({
                'content': doc,
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return relevant_contexts

# Использование
rag_db = RAGDatabase()
rag_db.add_code_context(indexed_data)
```

### Шаг 3: Интеграция с Qwen Code

**Настройка локальной модели с RAG:**

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class QwenCodeRAG:
    def __init__(self, model_path: str, rag_db: RAGDatabase):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.rag_db = rag_db
    
    def generate_with_context(self, query: str, max_length: int = 512) -> str:
        """Генерирует ответ с использованием RAG контекста"""
        
        # Получаем релевантный контекст
        relevant_contexts = self.rag_db.search_relevant_context(query)
        
        # Формируем промпт с контекстом
        context_text = "\n\n".join([
            f"Context {i+1}:\n{ctx['content'][:500]}..."
            for i, ctx in enumerate(relevant_contexts)
        ])
        
        prompt = f"""Based on the following context from our codebase, answer the question:

Context:
{context_text}

Question: {query}

Answer:"""
        
        # Токенизируем и генерируем
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Answer:")[-1].strip()

# Использование
rag_db = RAGDatabase()
qwen_rag = QwenCodeRAG("Qwen/Qwen-Code", rag_db)

response = qwen_rag.generate_with_context(
    "How do we handle authentication in our API?"
)
```

### Шаг 4: Настройка под стиль команды

**Анализ стиля кода команды:**

```python
import ast
import re
from collections import Counter

class CodeStyleAnalyzer:
    def __init__(self, indexed_data: List[Dict]):
        self.indexed_data = indexed_data
        self.style_patterns = {}
    
    def analyze_naming_conventions(self):
        """Анализирует соглашения по именованию"""
        function_names = []
        variable_names = []
        class_names = []
        
        for item in self.indexed_data:
            if item.get('language') == 'python':
                self._extract_python_names(item['content'], function_names, variable_names, class_names)
        
        self.style_patterns['function_naming'] = self._analyze_pattern(function_names)
        self.style_patterns['variable_naming'] = self._analyze_pattern(variable_names)
        self.style_patterns['class_naming'] = self._analyze_pattern(class_names)
    
    def analyze_error_handling(self):
        """Анализирует подходы к обработке ошибок"""
        error_patterns = {
            'exceptions': 0,
            'result_types': 0,
            'error_codes': 0,
            'logging': 0
        }
        
        for item in self.indexed_data:
            content = item['content']
            if 'raise' in content or 'except' in content:
                error_patterns['exceptions'] += 1
            if 'Result' in content or 'Either' in content:
                error_patterns['result_types'] += 1
            if 'error_code' in content.lower():
                error_patterns['error_codes'] += 1
            if 'logging' in content.lower() or 'logger' in content.lower():
                error_patterns['logging'] += 1
        
        self.style_patterns['error_handling'] = error_patterns
    
    def generate_style_prompt(self) -> str:
        """Генерирует промпт с учётом стиля команды"""
        style_instructions = []
        
        # Инструкции по именованию
        if self.style_patterns.get('function_naming'):
            style_instructions.append(
                f"Use {self.style_patterns['function_naming']} naming for functions"
            )
        
        # Инструкции по обработке ошибок
        error_style = self.style_patterns.get('error_handling', {})
        if error_style.get('result_types', 0) > error_style.get('exceptions', 0):
            style_instructions.append("Use Result<T, Error> pattern instead of exceptions")
        else:
            style_instructions.append("Use try-catch blocks for error handling")
        
        # Инструкции по логированию
        if error_style.get('logging', 0) > 0:
            style_instructions.append("Always add logging for important operations")
        
        return "\n".join(style_instructions)

# Использование
analyzer = CodeStyleAnalyzer(indexed_data)
analyzer.analyze_naming_conventions()
analyzer.analyze_error_handling()
style_prompt = analyzer.generate_style_prompt()
```

---

## Метрики эффективности персонализации

### 1. Скорость разработки

**Что измеряем:**
- Строки кода в час (LOC/hour)
- Время на задачу (task completion time)
- Количество итераций до готового кода

**Как измеряем:**
```python
class DevelopmentMetrics:
    def __init__(self):
        self.metrics = {
            'lines_per_hour': [],
            'task_completion_times': [],
            'iterations_per_task': []
        }
    
    def track_coding_session(self, start_time, end_time, lines_added, task_id):
        """Отслеживает сессию кодинга"""
        duration_hours = (end_time - start_time).total_seconds() / 3600
        lines_per_hour = lines_added / duration_hours
        
        self.metrics['lines_per_hour'].append(lines_per_hour)
        self.metrics['task_completion_times'].append(duration_hours)
    
    def get_productivity_gain(self, baseline_hours: float) -> float:
        """Вычисляет прирост продуктивности"""
        avg_hours = sum(self.metrics['task_completion_times']) / len(self.metrics['task_completion_times'])
        return (baseline_hours - avg_hours) / baseline_hours * 100
```

**Ожидаемые результаты:**
- **Без AI**: 50-100 строк/час
- **С AI**: 150-300 строк/час
- **Прирост**: 200-300%

### 2. Качество кода (дефекты)

**Что измеряем:**
- Баги на 1000 строк кода (bugs/KLOC)
- Количество критических ошибок
- Время до первого бага в продакшене

**Как измеряем:**
```python
class QualityMetrics:
    def __init__(self):
        self.bugs_by_severity = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        self.total_lines = 0
    
    def track_bug(self, severity: str, lines_affected: int):
        """Отслеживает баг"""
        self.bugs_by_severity[severity] += 1
        self.total_lines += lines_affected
    
    def get_bug_density(self) -> float:
        """Вычисляет плотность багов"""
        total_bugs = sum(self.bugs_by_severity.values())
        return (total_bugs / self.total_lines) * 1000 if self.total_lines > 0 else 0
    
    def get_critical_bug_rate(self) -> float:
        """Вычисляет долю критических багов"""
        total_bugs = sum(self.bugs_by_severity.values())
        return (self.bugs_by_severity['critical'] / total_bugs) * 100 if total_bugs > 0 else 0
```

**Ожидаемые результаты:**
- **Без AI**: 2-5 багов/KLOC
- **С AI**: 0.5-1.5 багов/KLOC
- **Улучшение**: 60-75% снижение

### 3. Производительность (p95)

**Что измеряем:**
- p95 время ответа API
- p95 время выполнения задач
- Пропускная способность системы

**Как измеряем:**
```python
import statistics
from typing import List

class PerformanceMetrics:
    def __init__(self):
        self.response_times: List[float] = []
        self.task_durations: List[float] = []
    
    def track_api_response(self, response_time: float):
        """Отслеживает время ответа API"""
        self.response_times.append(response_time)
    
    def track_task_duration(self, duration: float):
        """Отслеживает время выполнения задачи"""
        self.task_durations.append(duration)
    
    def get_p95_response_time(self) -> float:
        """Вычисляет p95 время ответа"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
    
    def get_performance_improvement(self, baseline_p95: float) -> float:
        """Вычисляет улучшение производительности"""
        current_p95 = self.get_p95_response_time()
        return (baseline_p95 - current_p95) / baseline_p95 * 100
```

**Ожидаемые результаты:**
- **Без AI**: p95 = 500-1000ms
- **С AI**: p95 = 200-400ms
- **Улучшение**: 40-60% снижение

### 4. Время восстановления (MTTR)

**Что измеряем:**
- Mean Time To Recovery (среднее время восстановления)
- Время диагностики проблем
- Время исправления багов

**Как измеряем:**
```python
from datetime import datetime, timedelta

class RecoveryMetrics:
    def __init__(self):
        self.incidents = []
    
    def track_incident(self, incident_id: str, start_time: datetime, 
                      detection_time: datetime, resolution_time: datetime):
        """Отслеживает инцидент"""
        self.incidents.append({
            'id': incident_id,
            'start_time': start_time,
            'detection_time': detection_time,
            'resolution_time': resolution_time,
            'detection_duration': (detection_time - start_time).total_seconds(),
            'resolution_duration': (resolution_time - detection_time).total_seconds(),
            'total_duration': (resolution_time - start_time).total_seconds()
        })
    
    def get_mttr(self) -> float:
        """Вычисляет среднее время восстановления"""
        if not self.incidents:
            return 0
        
        total_duration = sum(incident['total_duration'] for incident in self.incidents)
        return total_duration / len(self.incidents) / 3600  # в часах
    
    def get_detection_time(self) -> float:
        """Вычисляет среднее время обнаружения"""
        if not self.incidents:
            return 0
        
        total_detection = sum(incident['detection_duration'] for incident in self.incidents)
        return total_detection / len(self.incidents) / 3600  # в часах
```

**Ожидаемые результаты:**
- **Без AI**: MTTR = 4-8 часов
- **С AI**: MTTR = 1-3 часа
- **Улучшение**: 50-75% снижение

---

## Дашборд метрик

**Создание дашборда для отслеживания эффективности:**

```python
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

class MetricsDashboard:
    def __init__(self, dev_metrics, quality_metrics, perf_metrics, recovery_metrics):
        self.dev_metrics = dev_metrics
        self.quality_metrics = quality_metrics
        self.perf_metrics = perf_metrics
        self.recovery_metrics = recovery_metrics
    
    def generate_report(self) -> str:
        """Генерирует отчёт по метрикам"""
        report = f"""
# AI Персонализация - Отчёт по эффективности

## Производительность разработки
- Средняя скорость: {self._get_avg_lines_per_hour():.1f} строк/час
- Прирост продуктивности: {self._get_productivity_gain():.1f}%

## Качество кода
- Плотность багов: {self.quality_metrics.get_bug_density():.2f} багов/KLOC
- Критические баги: {self.quality_metrics.get_critical_bug_rate():.1f}%

## Производительность системы
- p95 время ответа: {self.perf_metrics.get_p95_response_time():.0f}ms
- Улучшение производительности: {self._get_performance_improvement():.1f}%

## Надёжность
- Среднее время восстановления: {self.recovery_metrics.get_mttr():.1f} часов
- Среднее время обнаружения: {self.recovery_metrics.get_detection_time():.1f} часов

## Общий эффект
- ROI персонализации: {self._calculate_roi():.1f}%
- Рекомендация: {'Продолжить использование' if self._calculate_roi() > 20 else 'Требует оптимизации'}
        """
        return report
    
    def _calculate_roi(self) -> float:
        """Вычисляет ROI персонализации"""
        productivity_gain = self._get_productivity_gain()
        quality_gain = self.quality_metrics.get_critical_bug_rate()
        performance_gain = self._get_performance_improvement()
        
        # Простая формула ROI
        return (productivity_gain + quality_gain + performance_gain) / 3
```

---

## Заключение

**Персонализация AI через RAG даёт:**

1. **Контекстно-релевантные ответы** — модель знает ваш код
2. **Соблюдение стиля команды** — единообразный код
3. **Контролируемые границы знаний** — безопасность данных
4. **Измеримые улучшения** — конкретные метрики эффективности

**Ожидаемые результаты:**
- **200-300%** прирост скорости разработки
- **60-75%** снижение количества багов
- **40-60%** улучшение производительности
- **50-75%** снижение времени восстановления

Когда эти цифры становятся видимыми, скепсис по поводу AI уходит сам собой!
