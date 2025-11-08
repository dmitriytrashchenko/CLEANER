#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEANER - Инструменты для работы с ИИ-текстами
Единая точка входа для всех функций
"""

import os
import sys
import argparse
import re
from collections import Counter

# Импорт модулей очистки
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Импорт модулей AI
import watermark
import ai_detector
import pattern_analyzer


# ============================================================================
# МОДУЛЬ ОЧИСТКИ ТЕКСТА
# ============================================================================

UNICODE_REPLACEMENTS = {
    '\u00A0': '\u0020',  # Неразрывный пробел → Обычный пробел
    '\u202F': '\u0020',  # Узкий неразрывный пробел → Обычный пробел
    '\u200B': '',        # Пробел нулевой ширины → Удалить
    '\u00AD': '',        # Мягкий перенос → Удалить
    '\u2019': '\u0027',  # Правый одинарный апостроф → Обычный апостроф
    '\u2014': '\u2013',  # Длинное тире (—) → Короткое тире (–)
}

SYMBOL_DESCRIPTIONS = {
    '\u00A0': 'Неразрывный пробел',
    '\u202F': 'Узкий неразрывный пробел',
    '\u200B': 'Пробел нулевой ширины',
    '\u00AD': 'Мягкий перенос',
    '\u2019': 'Правый одинарный апостроф',
    '\u2014': 'Длинное тире',
}


def clean_text(text):
    """Очищает текст от специальных символов Unicode"""
    stats = {}
    cleaned_text = text

    for old_char, new_char in UNICODE_REPLACEMENTS.items():
        count = cleaned_text.count(old_char)
        if count > 0:
            stats[old_char] = count
            cleaned_text = cleaned_text.replace(old_char, new_char)

    return cleaned_text, stats


def analyze_word_frequency(text, top_n=200):
    """Анализирует частоту использования слов"""
    words = re.findall(r'\b[а-яёa-z]+\b', text.lower(), re.UNICODE)
    word_counts = Counter(words)
    return word_counts.most_common(top_n)


def print_clean_statistics(stats, original_length, cleaned_length):
    """Выводит статистику очистки"""
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


# ============================================================================
# КОМАНДЫ
# ============================================================================

def cmd_clean(args):
    """Команда: очистка текста"""
    print("\n" + "="*70)
    print("ОЧИСТКА ТЕКСТА ОТ UNICODE-АРТЕФАКТОВ")
    print("="*70)

    # Читаем файл
    try:
        if args.input.endswith('.txt'):
            with open(args.input, 'r', encoding='utf-8') as f:
                original_text = f.read()
        elif args.input.endswith('.docx'):
            if not DOCX_AVAILABLE:
                print("Ошибка: Для работы с .docx установите python-docx")
                print("Команда: pip install python-docx")
                sys.exit(1)
            doc = Document(args.input)
            original_text = '\n'.join([p.text for p in doc.paragraphs])
        else:
            print("Ошибка: Неподдерживаемый формат файла")
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)

    # Очищаем
    cleaned_text, stats = clean_text(original_text)

    # Определяем выходной файл
    if args.inplace:
        output_path = args.input
    elif args.output:
        output_path = args.output
    else:
        print("Ошибка: Укажите --output или используйте --inplace")
        sys.exit(1)

    # Сохраняем
    try:
        if output_path.endswith('.txt'):
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
        elif output_path.endswith('.docx'):
            doc = Document(args.input)
            for paragraph in doc.paragraphs:
                cleaned_para, _ = clean_text(paragraph.text)
                paragraph.text = cleaned_para
            doc.save(output_path)
        print(f"\n✓ Файл сохранен: {output_path}")
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        sys.exit(1)

    # Статистика
    print_clean_statistics(stats, len(original_text), len(cleaned_text))

    # Анализ слов
    if args.analyze_words:
        print("\n" + "="*70)
        print("АНАЛИЗ ЧАСТОТЫ СЛОВ (ТОП-200)")
        print("="*70)
        word_freq = analyze_word_frequency(cleaned_text)
        for i, (word, count) in enumerate(word_freq, 1):
            print(f"{i:3d}. {word:30s} - {count:5d} раз")


def cmd_detect(args):
    """Команда: детекция ИИ"""
    print("\n" + "="*70)
    print("ДЕТЕКТОР ИИ-ТЕКСТА")
    print("="*70)

    # Читаем текст
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Анализируется файл: {args.file}")
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
    else:
        text = args.text

    # Детекция
    score, metrics = ai_detector.calculate_ai_score(text)
    ai_detector.print_ai_detection_report(score, metrics)

    # Паттерны
    if args.patterns:
        pattern_score, pattern_analysis = pattern_analyzer.detect_ai_writing_patterns(text)
        pattern_analyzer.print_pattern_analysis_report(pattern_score, pattern_analysis)

        # Комбинированная оценка
        combined_score = (score + pattern_score) / 2
        print("\n" + "="*70)
        print(f"КОМБИНИРОВАННАЯ ОЦЕНКА: {combined_score:.1f}%")
        print("="*70)


def cmd_patterns(args):
    """Команда: анализ паттернов"""
    print("\n" + "="*70)
    print("АНАЛИЗ ПАТТЕРНОВ")
    print("="*70)

    # Читаем текст
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Анализируется файл: {args.file}")
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
    else:
        text = args.text

    score, analysis = pattern_analyzer.detect_ai_writing_patterns(text)
    pattern_analyzer.print_pattern_analysis_report(score, analysis)


def cmd_watermark_add(args):
    """Команда: добавление водяного знака"""
    print("\n" + "="*70)
    print("ДОБАВЛЕНИЕ ВОДЯНОГО ЗНАКА")
    print("="*70)

    # Читаем текст
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"Исходный файл: {args.file}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    # Метаданные
    metadata = {}
    if args.metadata:
        for item in args.metadata:
            if '=' in item:
                key, value = item.split('=', 1)
                metadata[key] = value

    # Добавляем водяной знак
    if args.distributed:
        print(f"Тип: Распределенный водяной знак (плотность: {args.density})")
        watermarked_text = watermark.create_distributed_watermark(
            text, args.author, density=args.density
        )
        print(f"Автор: {args.author}")
    else:
        print("Тип: Концентрированный водяной знак")
        watermarked_text = watermark.embed_watermark(text, args.author, metadata)
        print(f"Автор: {args.author}")
        if metadata:
            print("Метаданные:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")

    # Сохраняем
    output_path = args.output or args.file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(watermarked_text)
        print(f"\n✓ Файл сохранен: {output_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    print(f"\nДлина оригинального текста:    {len(text):,} символов")
    print(f"Длина текста с водяным знаком: {len(watermarked_text):,} символов")
    print(f"Добавлено символов:            {len(watermarked_text) - len(text):,}")


def cmd_watermark_check(args):
    """Команда: проверка водяного знака"""
    print("\n" + "="*70)
    print("ПРОВЕРКА ВОДЯНОГО ЗНАКА")
    print("="*70)

    # Читаем текст
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"Проверяется файл: {args.file}\n")
        except Exception as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
    else:
        text = args.text

    # Проверка концентрированного
    extracted = watermark.extract_watermark(text)

    if extracted:
        print("✓ ВОДЯНОЙ ЗНАК ОБНАРУЖЕН!")
        watermark.print_watermark_info(extracted)
    else:
        print("✗ Концентрированный водяной знак не найден")

    # Проверка распределенного
    if args.author:
        print("\nПроверка распределенного водяного знака...")
        found, confidence = watermark.detect_distributed_watermark(text, args.author)

        print(f"Автор для проверки: {args.author}")
        print(f"Уверенность: {confidence:.1%}")

        if found:
            print(f"✓ РАСПРЕДЕЛЕННЫЙ ВОДЯНОЙ ЗНАК НАЙДЕН (уверенность: {confidence:.1%})")
        else:
            print(f"✗ Распределенный водяной знак не найден (уверенность: {confidence:.1%})")

    print("\n" + "="*70)


def cmd_watermark_remove(args):
    """Команда: удаление водяного знака"""
    print("\n" + "="*70)
    print("УДАЛЕНИЕ ВОДЯНОГО ЗНАКА")
    print("="*70)

    # Читаем текст
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"Исходный файл: {args.file}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    # Удаляем
    cleaned_text = watermark.remove_watermark(text)

    # Сохраняем
    output_path = args.output or args.file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"\n✓ Файл сохранен: {output_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    print(f"\nДлина текста с водяным знаком: {len(text):,} символов")
    print(f"Длина очищенного текста:       {len(cleaned_text):,} символов")
    print(f"Удалено символов:              {len(text) - len(cleaned_text):,}")


# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Главная функция с единым CLI"""
    parser = argparse.ArgumentParser(
        description='CLEANER - Инструменты для работы с ИИ-текстами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Доступные команды:

1. ОЧИСТКА ТЕКСТА:
   clean               Очистка от Unicode-символов

2. ДЕТЕКЦИЯ И АНАЛИЗ:
   detect              Детекция ИИ-текста (0-100%%)
   patterns            Анализ паттернов ИИ

3. ВОДЯНЫЕ ЗНАКИ:
   watermark-add       Добавить водяной знак
   watermark-check     Проверить водяной знак
   watermark-remove    Удалить водяной знак

Примеры:
  python cleaner.py clean input.txt -o output.txt
  python cleaner.py detect --file document.txt --patterns
  python cleaner.py watermark-add --file doc.txt --author "Имя" -o marked.txt

Для справки по команде: python cleaner.py <команда> --help
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Команда для выполнения')

    # ===== CLEAN =====
    parser_clean = subparsers.add_parser('clean', help='Очистка текста от Unicode-символов')
    parser_clean.add_argument('input', help='Входной файл (.txt или .docx)')
    parser_clean.add_argument('-o', '--output', help='Выходной файл')
    parser_clean.add_argument('--inplace', action='store_true', help='Заменить исходный файл')
    parser_clean.add_argument('--analyze-words', action='store_true', help='Анализ частоты слов (топ-200)')
    parser_clean.set_defaults(func=cmd_clean)

    # ===== DETECT =====
    parser_detect = subparsers.add_parser('detect', help='Детекция ИИ-текста')
    parser_detect.add_argument('--file', help='Файл для анализа')
    parser_detect.add_argument('--text', help='Текст для анализа')
    parser_detect.add_argument('--patterns', action='store_true', help='Также анализировать паттерны')
    parser_detect.set_defaults(func=cmd_detect)

    # ===== PATTERNS =====
    parser_patterns = subparsers.add_parser('patterns', help='Анализ паттернов')
    parser_patterns.add_argument('--file', help='Файл для анализа')
    parser_patterns.add_argument('--text', help='Текст для анализа')
    parser_patterns.set_defaults(func=cmd_patterns)

    # ===== WATERMARK-ADD =====
    parser_wm_add = subparsers.add_parser('watermark-add', help='Добавить водяной знак')
    parser_wm_add.add_argument('--file', required=True, help='Файл')
    parser_wm_add.add_argument('--author', required=True, help='Имя автора')
    parser_wm_add.add_argument('-o', '--output', help='Выходной файл')
    parser_wm_add.add_argument('--metadata', nargs='+', help='Метаданные (key=value)')
    parser_wm_add.add_argument('--distributed', action='store_true', help='Распределенный тип')
    parser_wm_add.add_argument('--density', type=float, default=0.1, help='Плотность (0.0-1.0)')
    parser_wm_add.set_defaults(func=cmd_watermark_add)

    # ===== WATERMARK-CHECK =====
    parser_wm_check = subparsers.add_parser('watermark-check', help='Проверить водяной знак')
    parser_wm_check.add_argument('--file', help='Файл')
    parser_wm_check.add_argument('--text', help='Текст')
    parser_wm_check.add_argument('--author', help='Автор (для распределенного)')
    parser_wm_check.set_defaults(func=cmd_watermark_check)

    # ===== WATERMARK-REMOVE =====
    parser_wm_remove = subparsers.add_parser('watermark-remove', help='Удалить водяной знак')
    parser_wm_remove.add_argument('--file', required=True, help='Файл')
    parser_wm_remove.add_argument('-o', '--output', help='Выходной файл')
    parser_wm_remove.set_defaults(func=cmd_watermark_remove)

    # Парсинг
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Выполнение команды
    args.func(args)


if __name__ == '__main__':
    main()
