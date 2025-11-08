#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Инструменты для работы с ИИ-текстами:
- Детекция искусственности текста
- Анализ паттернов
- Водяные знаки (стеганография)
"""

import sys
import os
import argparse

# Импортируем наши модули
import watermark
import ai_detector
import pattern_analyzer


def process_file(file_path: str, encoding: str = 'utf-8') -> str:
    """Читает текст из файла"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)


def save_file(file_path: str, content: str, encoding: str = 'utf-8'):
    """Сохраняет текст в файл"""
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        print(f"\n✓ Файл сохранен: {file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        sys.exit(1)


def cmd_detect(args):
    """Команда: детекция ИИ-текста"""
    print("\n" + "="*70)
    print("ДЕТЕКТОР ИИ-ТЕКСТА")
    print("="*70)

    if args.file:
        text = process_file(args.file)
        print(f"Анализируется файл: {args.file}")
    else:
        text = args.text

    # Детекция искусственности
    score, metrics = ai_detector.calculate_ai_score(text)
    ai_detector.print_ai_detection_report(score, metrics)

    # Анализ паттернов (если запрошено)
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
    print("АНАЛИЗ ПАТТЕРНОВ ИИ-ТЕКСТА")
    print("="*70)

    if args.file:
        text = process_file(args.file)
        print(f"Анализируется файл: {args.file}")
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
    if args.file:
        text = process_file(args.file)
        print(f"Исходный файл: {args.file}")
    else:
        print("Ошибка: необходимо указать файл с помощью --file")
        sys.exit(1)

    # Создаем метаданные
    metadata = {}
    if args.metadata:
        for item in args.metadata:
            if '=' in item:
                key, value = item.split('=', 1)
                metadata[key] = value

    # Тип водяного знака
    if args.distributed:
        print(f"Тип: Распределенный водяной знак (плотность: {args.density})")
        watermarked_text = watermark.create_distributed_watermark(
            text, args.author, density=args.density
        )
        print(f"Автор: {args.author}")
    else:
        print("Тип: Концентрированный водяной знак (в начале текста)")
        watermarked_text = watermark.embed_watermark(text, args.author, metadata)
        print(f"Автор: {args.author}")
        if metadata:
            print("Метаданные:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")

    # Сохраняем
    output_path = args.output or args.file
    save_file(output_path, watermarked_text)

    print(f"\nДлина оригинального текста:  {len(text)} символов")
    print(f"Длина текста с водяным знаком: {len(watermarked_text)} символов")
    print(f"Добавлено символов: {len(watermarked_text) - len(text)}")


def cmd_watermark_check(args):
    """Команда: проверка водяного знака"""
    print("\n" + "="*70)
    print("ПРОВЕРКА ВОДЯНОГО ЗНАКА")
    print("="*70)

    # Читаем текст
    if args.file:
        text = process_file(args.file)
        print(f"Проверяется файл: {args.file}\n")
    else:
        text = args.text

    # Проверяем концентрированный водяной знак
    extracted = watermark.extract_watermark(text)

    if extracted:
        print("✓ ВОДЯНОЙ ЗНАК ОБНАРУЖЕН!")
        watermark.print_watermark_info(extracted)
    else:
        print("✗ Концентрированный водяной знак не найден")

    # Проверяем распределенный водяной знак (если указан автор)
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
    if args.file:
        text = process_file(args.file)
        print(f"Исходный файл: {args.file}")
    else:
        print("Ошибка: необходимо указать файл с помощью --file")
        sys.exit(1)

    # Удаляем водяной знак
    cleaned_text = watermark.remove_watermark(text)

    # Сохраняем
    output_path = args.output or args.file
    save_file(output_path, cleaned_text)

    print(f"\nДлина текста с водяным знаком: {len(text)} символов")
    print(f"Длина очищенного текста:       {len(cleaned_text)} символов")
    print(f"Удалено символов: {len(text) - len(cleaned_text)}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Инструменты для работы с ИИ-текстами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

1. Детекция ИИ-текста:
   %(prog)s detect --file document.txt
   %(prog)s detect --file document.txt --patterns
   %(prog)s detect --text "Ваш текст здесь"

2. Анализ паттернов:
   %(prog)s patterns --file document.txt

3. Добавление водяного знака:
   %(prog)s watermark-add --file document.txt --author "Иван Иванов"
   %(prog)s watermark-add --file doc.txt --author "Автор" --metadata project=MyProject version=1.0
   %(prog)s watermark-add --file doc.txt --author "Автор" --distributed --density 0.2

4. Проверка водяного знака:
   %(prog)s watermark-check --file document.txt
   %(prog)s watermark-check --file doc.txt --author "Автор"

5. Удаление водяного знака:
   %(prog)s watermark-remove --file document.txt --output clean.txt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    # Команда: detect
    parser_detect = subparsers.add_parser('detect', help='Детекция ИИ-текста')
    parser_detect.add_argument('--file', help='Путь к файлу')
    parser_detect.add_argument('--text', help='Текст для анализа')
    parser_detect.add_argument('--patterns', action='store_true', help='Также анализировать паттерны')
    parser_detect.set_defaults(func=cmd_detect)

    # Команда: patterns
    parser_patterns = subparsers.add_parser('patterns', help='Анализ паттернов')
    parser_patterns.add_argument('--file', help='Путь к файлу')
    parser_patterns.add_argument('--text', help='Текст для анализа')
    parser_patterns.set_defaults(func=cmd_patterns)

    # Команда: watermark-add
    parser_wm_add = subparsers.add_parser('watermark-add', help='Добавить водяной знак')
    parser_wm_add.add_argument('--file', required=True, help='Путь к файлу')
    parser_wm_add.add_argument('--author', required=True, help='Имя автора')
    parser_wm_add.add_argument('--output', help='Выходной файл (по умолчанию перезаписывает исходный)')
    parser_wm_add.add_argument('--metadata', nargs='+', help='Метаданные в формате key=value')
    parser_wm_add.add_argument('--distributed', action='store_true', help='Распределенный водяной знак')
    parser_wm_add.add_argument('--density', type=float, default=0.1, help='Плотность для распределенного (0.0-1.0)')
    parser_wm_add.set_defaults(func=cmd_watermark_add)

    # Команда: watermark-check
    parser_wm_check = subparsers.add_parser('watermark-check', help='Проверить водяной знак')
    parser_wm_check.add_argument('--file', help='Путь к файлу')
    parser_wm_check.add_argument('--text', help='Текст для проверки')
    parser_wm_check.add_argument('--author', help='Автор для проверки распределенного водяного знака')
    parser_wm_check.set_defaults(func=cmd_watermark_check)

    # Команда: watermark-remove
    parser_wm_remove = subparsers.add_parser('watermark-remove', help='Удалить водяной знак')
    parser_wm_remove.add_argument('--file', required=True, help='Путь к файлу')
    parser_wm_remove.add_argument('--output', help='Выходной файл (по умолчанию перезаписывает исходный)')
    parser_wm_remove.set_defaults(func=cmd_watermark_remove)

    # Парсим аргументы
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Выполняем команду
    args.func(args)


if __name__ == '__main__':
    main()
