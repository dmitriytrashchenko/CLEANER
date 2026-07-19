#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки текста от невидимых символов Unicode, добавляемых ИИ
"""

import os
import sys
import argparse
import re
from collections import Counter
from typing import Dict, Tuple

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Проверка наличия python-docx
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Предупреждение: библиотека python-docx не установлена.")
    print("Для работы с .docx файлами установите её: pip install python-docx")


# Словарь замен символов Unicode
UNICODE_REPLACEMENTS = {
    '\u00A0': '\u0020',  # Неразрывный пробел → Обычный пробел
    '\u202F': '\u0020',  # Узкий неразрывный пробел → Обычный пробел
    '\u200B': '',        # Пробел нулевой ширины → Удалить
    '\u00AD': '',        # Мягкий перенос → Удалить
    '\u2019': '\u0027',  # Правый одинарный апостроф → Обычный апостроф
    '\u2014': '\u2013',  # Длинное тире (—) → Короткое тире (–)
}

# Описания символов для статистики
SYMBOL_DESCRIPTIONS = {
    '\u00A0': 'Неразрывный пробел',
    '\u202F': 'Узкий неразрывный пробел',
    '\u200B': 'Пробел нулевой ширины',
    '\u00AD': 'Мягкий перенос',
    '\u2019': 'Правый одинарный апостроф',
    '\u2014': 'Длинное тире',
}


def clean_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Очищает текст от специальных символов Unicode.

    Args:
        text: Исходный текст

    Returns:
        Кортеж (очищенный текст, статистика замен)
    """
    stats = {}
    cleaned_text = text

    for old_char, new_char in UNICODE_REPLACEMENTS.items():
        count = cleaned_text.count(old_char)
        if count > 0:
            stats[old_char] = count
            cleaned_text = cleaned_text.replace(old_char, new_char)

    return cleaned_text, stats


def analyze_word_frequency(text: str, top_n: int = 200) -> Counter:
    """
    Анализирует частоту использования слов в тексте.

    Args:
        text: Текст для анализа
        top_n: Количество наиболее частых слов

    Returns:
        Counter с топ-N словами
    """
    # Удаляем знаки препинания и приводим к нижнему регистру
    words = re.findall(r'\b[а-яёa-z]+\b', text.lower(), re.UNICODE)

    # Подсчитываем частоту
    word_counts = Counter(words)

    return word_counts.most_common(top_n)


def process_txt_file(input_path: str, output_path: str, analyze_words: bool = False):
    """
    Обрабатывает текстовый файл .txt

    Args:
        input_path: Путь к входному файлу
        output_path: Путь к выходному файлу
        analyze_words: Анализировать частоту слов
    """
    try:
        # Читаем файл
        with open(input_path, 'r', encoding='utf-8') as f:
            original_text = f.read()

        # Очищаем текст
        cleaned_text, stats = clean_text(original_text)

        # Сохраняем результат
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        # Выводим статистику
        print_statistics(stats, len(original_text), len(cleaned_text))

        # Анализ частоты слов
        if analyze_words:
            print("\n" + "="*70)
            print("АНАЛИЗ ЧАСТОТЫ СЛОВ (ТОП-200)")
            print("="*70)
            word_freq = analyze_word_frequency(cleaned_text)
            for i, (word, count) in enumerate(word_freq, 1):
                print(f"{i:3d}. {word:30s} - {count:5d} раз")

        print(f"\n✓ Файл успешно обработан: {output_path}")

    except Exception as e:
        print(f"Ошибка при обработке .txt файла: {e}")
        sys.exit(1)


def process_docx_file(input_path: str, output_path: str, analyze_words: bool = False):
    """
    Обрабатывает файл .docx с сохранением форматирования

    Args:
        input_path: Путь к входному файлу
        output_path: Путь к выходному файлу
        analyze_words: Анализировать частоту слов
    """
    if not DOCX_AVAILABLE:
        print("Ошибка: Для работы с .docx файлами установите python-docx")
        print("Команда: pip install python-docx")
        sys.exit(1)

    try:
        # Загружаем документ
        doc = Document(input_path)

        total_stats = {}
        all_text = []
        original_length = 0
        cleaned_length = 0

        # Обрабатываем параграфы
        for paragraph in doc.paragraphs:
            original_text = paragraph.text
            original_length += len(original_text)
            all_text.append(original_text)

            cleaned_text, stats = clean_text(original_text)
            cleaned_length += len(cleaned_text)

            # Обновляем статистику
            for char, count in stats.items():
                total_stats[char] = total_stats.get(char, 0) + count

            # Заменяем текст параграфа, сохраняя форматирование
            paragraph.text = cleaned_text

        # Обрабатываем таблицы
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        original_text = paragraph.text
                        original_length += len(original_text)
                        all_text.append(original_text)

                        cleaned_text, stats = clean_text(original_text)
                        cleaned_length += len(cleaned_text)

                        for char, count in stats.items():
                            total_stats[char] = total_stats.get(char, 0) + count

                        paragraph.text = cleaned_text

        # Сохраняем документ
        doc.save(output_path)

        # Выводим статистику
        print_statistics(total_stats, original_length, cleaned_length)

        # Анализ частоты слов
        if analyze_words:
            print("\n" + "="*70)
            print("АНАЛИЗ ЧАСТОТЫ СЛОВ (ТОП-200)")
            print("="*70)
            full_text = ' '.join(all_text)
            word_freq = analyze_word_frequency(full_text)
            for i, (word, count) in enumerate(word_freq, 1):
                print(f"{i:3d}. {word:30s} - {count:5d} раз")

        print(f"\n✓ Файл успешно обработан: {output_path}")

    except Exception as e:
        print(f"Ошибка при обработке .docx файла: {e}")
        sys.exit(1)


def print_statistics(stats: Dict[str, int], original_length: int, cleaned_length: int):
    """
    Выводит статистику замен

    Args:
        stats: Словарь со статистикой замен
        original_length: Длина исходного текста
        cleaned_length: Длина очищенного текста
    """
    print("\n" + "="*70)
    print("СТАТИСТИКА ОЧИСТКИ ТЕКСТА")
    print("="*70)

    if stats:
        print("\nНайденные и замененные символы:")
        print("-" * 70)
        total_replacements = 0

        for char, count in stats.items():
            description = SYMBOL_DESCRIPTIONS.get(char, "Неизвестный символ")
            replacement = UNICODE_REPLACEMENTS.get(char, '')
            replacement_desc = f"→ '{replacement}'" if replacement else "→ удален"
            print(f"  {description:35s} (U+{ord(char):04X}): {count:5d} {replacement_desc}")
            total_replacements += count

        print("-" * 70)
        print(f"Всего заменено символов: {total_replacements}")
    else:
        print("\n✓ Специальных символов не найдено. Текст уже чистый!")

    print(f"\nДлина исходного текста:   {original_length:,} символов")
    print(f"Длина очищенного текста:  {cleaned_length:,} символов")
    print(f"Разница:                  {original_length - cleaned_length:,} символов")
    print("="*70)


def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description='Очистка текста от невидимых символов Unicode, добавляемых ИИ',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s input.txt -o output.txt
  %(prog)s document.docx -o cleaned.docx
  %(prog)s input.txt -o output.txt --analyze-words
  %(prog)s input.txt --inplace
  %(prog)s input.txt --inplace --analyze-words

Заменяемые символы:
  • U+00A0 (Неразрывный пробел) → Обычный пробел
  • U+202F (Узкий неразрывный пробел) → Обычный пробел
  • U+200B (Пробел нулевой ширины) → Удаляется
  • U+00AD (Мягкий перенос) → Удаляется
  • U+2019 (Правый апостроф) → Обычный апостроф
  • U+2014 (Длинное тире —) → Короткое тире –
        """
    )

    parser.add_argument(
        'input',
        help='Путь к входному файлу (.txt или .docx)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Путь к выходному файлу (если не указан, используется --inplace)'
    )

    parser.add_argument(
        '--inplace',
        action='store_true',
        help='Заменить исходный файл очищенной версией'
    )

    parser.add_argument(
        '--analyze-words',
        action='store_true',
        help='Провести анализ частоты слов (топ-200)'
    )

    args = parser.parse_args()

    # Проверка входного файла
    if not os.path.exists(args.input):
        print(f"Ошибка: Файл '{args.input}' не найден!")
        sys.exit(1)

    # Определяем выходной файл
    if args.inplace:
        output_path = args.input
    elif args.output:
        output_path = args.output
    else:
        print("Ошибка: Укажите --output или используйте --inplace")
        sys.exit(1)

    # Определяем тип файла
    file_ext = os.path.splitext(args.input)[1].lower()

    print("="*70)
    print("СКРИПТ ОЧИСТКИ ТЕКСТА ОТ ИИ-СИМВОЛОВ")
    print("="*70)
    print(f"Входной файл:  {args.input}")
    print(f"Выходной файл: {output_path}")
    print(f"Тип файла:     {file_ext}")
    if args.analyze_words:
        print("Режим:         Очистка + Анализ частоты слов")
    else:
        print("Режим:         Только очистка")
    print("="*70)

    # Обработка в зависимости от типа файла
    if file_ext == '.txt':
        process_txt_file(args.input, output_path, args.analyze_words)
    elif file_ext == '.docx':
        process_docx_file(args.input, output_path, args.analyze_words)
    else:
        print(f"Ошибка: Неподдерживаемый формат файла '{file_ext}'")
        print("Поддерживаются: .txt, .docx")
        sys.exit(1)


if __name__ == '__main__':
    main()
