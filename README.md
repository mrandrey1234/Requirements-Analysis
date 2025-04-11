# Система протоколирования совещаний

## Описание

Программное решение для автоматической записи совещаний с распознаванием речи, идентификацией спикеров и экспортом результатов в структурированный документ.

## Установка

### Предварительные требования

- Python 3.7+
- Микрофон с частотой дискретизации ≥16 кГц
- 2 ГБ свободного места (включая модель распознавания)
- ОС: Windows/Linux/macOS

### Шаги установки

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/mrandrey1234/Requirements-Analysis.git
   cd Requirements-Analysis
   ```
   
2. **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```
   
3. **Загрузите модель распознования:**
 
    ```bash
     wget https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip
     unzip vosk-model-ru-0.42.zip -d models/
     ```
   
## Использование

### Запуск системы
  ```bash
  python interface.py
  ```

## Руководство пользователя

### Настройка участников
1. Введите количество участников совещания
2. Укажите имена спикеров (или оставьте значения по умолчанию)
3. Нажмите "Обновить список участников"

### Управление записью
- **Старт записи**: автоматически начинает анализ аудиопотока
- **Стоп записи**: завершает процесс с генерацией отчета
- **Открыть файл**: просмотр сгенерированного протокола

### Формат вывода
Протокол сохраняется в файл `transcription.docx` со структурой:
```
[2023-10-15 14:30:00] Иван Петров: Предлагаю обсудить новый проект
[2023-10-15 14:30:15] Анна Сидорова: Согласна, начнем с технических требований
```

## Архитектура решения
```
src/
├── interface.py            # Графический интерфейс
├── speech_to_text.py       # Ядро обработки аудио
├── vosk-model-ru-0.42      # Модель распознавания речи
```

## Оптимизация работы
- **Рекомендуемое расстояние** до микрофона: 20-50 см
- **Оптимальное число спикеров**: 2-4 человека
- **Тихая среда** без фоновых шумов

## Лицензия
Проект распространяется под лицензией MIT. Полный текст доступен в файле [LICENSE](LICENSE).
