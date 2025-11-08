#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для поиска повторяющихся конструкций и паттернов, характерных для ИИ
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import statistics


def extract_ngrams(words: List[str], n: int) -> List[str]:
    """
    Извлекает n-граммы из списка слов

    Args:
        words: Список слов
        n: Размер n-граммы

    Returns:
        Список n-грамм
    """
    if len(words) < n:
        return []

    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)

    return ngrams


def find_repeated_ngrams(text: str, min_n: int = 2, max_n: int = 5) -> Dict[int, List[Tuple[str, int]]]:
    """
    Находит повторяющиеся n-граммы разных размеров

    Args:
        text: Текст для анализа
        min_n: Минимальный размер n-граммы
        max_n: Максимальный размер n-граммы

    Returns:
        Словарь {размер n-граммы: [(n-грамма, количество повторений)]}
    """
    words = re.findall(r'\b[а-яёa-z]+\b', text.lower(), re.UNICODE)

    results = {}

    for n in range(min_n, max_n + 1):
        ngrams = extract_ngrams(words, n)
        ngram_counts = Counter(ngrams)

        # Оставляем только повторяющиеся
        repeated = [(ngram, count) for ngram, count in ngram_counts.items() if count > 1]

        # Сортируем по частоте
        repeated.sort(key=lambda x: x[1], reverse=True)

        if repeated:
            results[n] = repeated

    return results


def find_sentence_patterns(text: str) -> List[Tuple[str, int]]:
    """
    Находит повторяющиеся паттерны начала предложений
    ИИ часто начинает предложения одинаково

    Args:
        text: Текст для анализа

    Returns:
        Список (паттерн, количество)
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Извлекаем первые 2-3 слова каждого предложения
    sentence_starts = []
    for sentence in sentences:
        words = re.findall(r'\b[а-яёa-z]+\b', sentence.lower(), re.UNICODE)
        if len(words) >= 2:
            start = ' '.join(words[:3])
            sentence_starts.append(start)

    # Подсчитываем повторения
    start_counts = Counter(sentence_starts)
    repeated = [(start, count) for start, count in start_counts.items() if count > 1]
    repeated.sort(key=lambda x: x[1], reverse=True)

    return repeated


def find_formulaic_expressions(text: str) -> Dict[str, List[str]]:
    """
    Находит шаблонные выражения, характерные для ИИ

    Args:
        text: Текст для анализа

    Returns:
        Словарь {категория: [найденные выражения]}
    """
    text_lower = text.lower()

    patterns = {
        'вводные_конструкции': [
            r'\bважно (отметить|понимать|учитывать|знать)',
            r'\bстоит (отметить|учитывать|понимать|знать)',
            r'\bнеобходимо (отметить|понимать|учитывать)',
            r'\bследует (отметить|учитывать|понимать)',
        ],
        'переходы': [
            r'\bоднако\b',
            r'\bтем не менее\b',
            r'\bкроме того\b',
            r'\bболее того\b',
            r'\bтаким образом\b',
            r'\bв заключение\b',
            r'\bследовательно\b',
        ],
        'усиления': [
            r'\bв значительной степени\b',
            r'\bв полной мере\b',
            r'\bв первую очередь\b',
            r'\bпрежде всего\b',
        ],
        'общие_места': [
            r'\bв современном мире\b',
            r'\bв настоящее время\b',
            r'\bна сегодняшний день\b',
            r'\bв наши дни\b',
        ],
    }

    found = defaultdict(list)

    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, text_lower)
            if matches:
                found[category].extend(matches)

    return dict(found)


def analyze_sentence_structure_patterns(text: str) -> Dict[str, any]:
    """
    Анализирует структурные паттерны предложений

    Args:
        text: Текст для анализа

    Returns:
        Словарь с метриками структуры
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return {}

    # Длины предложений
    lengths = [len(s.split()) for s in sentences]

    # Начало предложений
    first_words = []
    for sentence in sentences:
        words = re.findall(r'\b[а-яёa-z]+\b', sentence.lower(), re.UNICODE)
        if words:
            first_words.append(words[0])

    # Типы предложений (вопросительные, восклицательные)
    question_count = text.count('?')
    exclamation_count = text.count('!')
    declarative_count = len(sentences) - question_count - exclamation_count

    return {
        'avg_length': statistics.mean(lengths) if lengths else 0,
        'length_variance': statistics.stdev(lengths) if len(lengths) > 1 else 0,
        'length_uniformity': 1 - (statistics.stdev(lengths) / statistics.mean(lengths) if statistics.mean(lengths) > 0 and len(lengths) > 1 else 0),
        'question_ratio': question_count / len(sentences) if sentences else 0,
        'exclamation_ratio': exclamation_count / len(sentences) if sentences else 0,
        'declarative_ratio': declarative_count / len(sentences) if sentences else 0,
        'first_word_diversity': len(set(first_words)) / len(first_words) if first_words else 0,
    }


def find_vocabulary_clusters(text: str) -> Dict[str, int]:
    """
    Находит кластеры часто используемой лексики
    ИИ может чрезмерно использовать определенные слова

    Args:
        text: Текст для анализа

    Returns:
        Словарь {слово: частота} для слов с высокой частотой
    """
    words = re.findall(r'\b[а-яёa-z]{4,}\b', text.lower(), re.UNICODE)

    if not words:
        return {}

    word_counts = Counter(words)

    # Вычисляем среднюю частоту
    avg_freq = statistics.mean(word_counts.values())
    std_dev = statistics.stdev(word_counts.values()) if len(word_counts) > 1 else 0

    # Находим слова с частотой выше среднего + 1 стандартное отклонение
    threshold = avg_freq + std_dev
    overused = {word: count for word, count in word_counts.items() if count > threshold and count > 2}

    # Сортируем по частоте
    overused = dict(sorted(overused.items(), key=lambda x: x[1], reverse=True))

    return overused


def detect_ai_writing_patterns(text: str) -> Tuple[float, Dict]:
    """
    Комплексный анализ паттернов, характерных для ИИ

    Args:
        text: Текст для анализа

    Returns:
        Кортеж (оценка паттернов 0-100, детальная информация)
    """
    if len(text.strip()) < 50:
        return 0.0, {'error': 'Текст слишком короткий для анализа'}

    analysis = {}

    # 1. Повторяющиеся n-граммы
    repeated_ngrams = find_repeated_ngrams(text)
    analysis['repeated_ngrams'] = repeated_ngrams

    total_repetitions = sum(
        sum(count - 1 for _, count in ngrams)
        for ngrams in repeated_ngrams.values()
    )
    analysis['total_ngram_repetitions'] = total_repetitions

    # 2. Паттерны начала предложений
    sentence_patterns = find_sentence_patterns(text)
    analysis['sentence_start_patterns'] = sentence_patterns[:5]

    # 3. Шаблонные выражения
    formulaic = find_formulaic_expressions(text)
    analysis['formulaic_expressions'] = formulaic

    formulaic_count = sum(len(expressions) for expressions in formulaic.values())
    analysis['formulaic_count'] = formulaic_count

    # 4. Структурные паттерны
    structure = analyze_sentence_structure_patterns(text)
    analysis['sentence_structure'] = structure

    # 5. Кластеры лексики
    overused_words = find_vocabulary_clusters(text)
    analysis['overused_words'] = dict(list(overused_words.items())[:10])

    # Вычисляем оценку
    words = re.findall(r'\b[а-яёa-z]+\b', text.lower(), re.UNICODE)
    word_count = len(words)

    # Баллы за различные паттерны
    scores = []

    # N-граммы: каждое повторение на 100 слов = 5 баллов
    ngram_score = min(100, (total_repetitions / max(1, word_count / 100)) * 5)
    scores.append(ngram_score * 0.2)

    # Шаблонные выражения: каждое на 50 слов = 10 баллов
    formulaic_score = min(100, (formulaic_count / max(1, word_count / 50)) * 10)
    scores.append(formulaic_score * 0.3)

    # Однородность длины предложений
    uniformity = structure.get('length_uniformity', 0)
    uniformity_score = uniformity * 100
    scores.append(uniformity_score * 0.25)

    # Повторяющиеся начала предложений
    sentence_start_score = min(100, len(sentence_patterns) * 15)
    scores.append(sentence_start_score * 0.15)

    # Чрезмерно используемые слова
    overused_score = min(100, len(overused_words) * 10)
    scores.append(overused_score * 0.1)

    total_score = sum(scores)

    analysis['component_scores'] = {
        'ngram_repetitions': round(ngram_score, 2),
        'formulaic_expressions': round(formulaic_score, 2),
        'sentence_uniformity': round(uniformity_score, 2),
        'repeated_starts': round(sentence_start_score, 2),
        'vocabulary_clustering': round(overused_score, 2),
    }

    return round(total_score, 2), analysis


def print_pattern_analysis_report(score: float, analysis: Dict):
    """
    Выводит детальный отчет об анализе паттернов

    Args:
        score: Оценка паттернов (0-100)
        analysis: Результаты анализа
    """
    print("\n" + "="*70)
    print("АНАЛИЗ ПАТТЕРНОВ И ПОВТОРЯЮЩИХСЯ КОНСТРУКЦИЙ")
    print("="*70)

    # Общая оценка
    if score < 30:
        verdict = "НИЗКИЙ УРОВЕНЬ ПАТТЕРНОВ"
        color = "🟢"
    elif score < 60:
        verdict = "СРЕДНИЙ УРОВЕНЬ ПАТТЕРНОВ"
        color = "🟡"
    else:
        verdict = "ВЫСОКИЙ УРОВЕНЬ ПАТТЕРНОВ (ХАРАКТЕРНО ДЛЯ ИИ)"
        color = "🔴"

    print(f"\n{color} ОЦЕНКА ПАТТЕРНОВ: {score:.1f}% - {verdict}")

    # Компонентные оценки
    if 'component_scores' in analysis:
        print("\n" + "-"*70)
        print("ДЕТАЛИЗАЦИЯ ПО КОМПОНЕНТАМ:")
        print("-"*70)
        scores = analysis['component_scores']

        print(f"\n  Повторяющиеся n-граммы:        {scores['ngram_repetitions']:5.1f}% {'⚠️' if scores['ngram_repetitions'] > 50 else '✓'}")
        print(f"  Шаблонные выражения:           {scores['formulaic_expressions']:5.1f}% {'⚠️' if scores['formulaic_expressions'] > 50 else '✓'}")
        print(f"  Однородность предложений:      {scores['sentence_uniformity']:5.1f}% {'⚠️' if scores['sentence_uniformity'] > 50 else '✓'}")
        print(f"  Повторяющиеся начала:          {scores['repeated_starts']:5.1f}% {'⚠️' if scores['repeated_starts'] > 50 else '✓'}")
        print(f"  Кластеризация лексики:         {scores['vocabulary_clustering']:5.1f}% {'⚠️' if scores['vocabulary_clustering'] > 50 else '✓'}")

    # Повторяющиеся n-граммы
    if analysis.get('repeated_ngrams'):
        print("\n" + "-"*70)
        print("ПОВТОРЯЮЩИЕСЯ ФРАЗЫ:")
        print("-"*70)

        for n, ngrams in sorted(analysis['repeated_ngrams'].items()):
            if ngrams[:3]:  # Показываем топ-3 для каждого размера
                print(f"\n  {n}-граммы:")
                for ngram, count in ngrams[:3]:
                    print(f"    • «{ngram}» — {count} раз(а)")

    # Паттерны начала предложений
    if analysis.get('sentence_start_patterns'):
        print("\n" + "-"*70)
        print("ПОВТОРЯЮЩИЕСЯ НАЧАЛА ПРЕДЛОЖЕНИЙ:")
        print("-"*70)
        for pattern, count in analysis['sentence_start_patterns']:
            print(f"  • «{pattern}...» — {count} раз(а)")

    # Шаблонные выражения
    if analysis.get('formulaic_expressions'):
        print("\n" + "-"*70)
        print("ШАБЛОННЫЕ ВЫРАЖЕНИЯ (ХАРАКТЕРНЫЕ ДЛЯ ИИ):")
        print("-"*70)

        for category, expressions in analysis['formulaic_expressions'].items():
            category_name = category.replace('_', ' ').title()
            print(f"\n  {category_name}:")
            unique_expr = list(set(expressions))
            for expr in unique_expr[:5]:
                count = expressions.count(expr)
                print(f"    • {expr} — {count} раз(а)")

    # Чрезмерно используемые слова
    if analysis.get('overused_words'):
        print("\n" + "-"*70)
        print("ЧРЕЗМЕРНО ИСПОЛЬЗУЕМАЯ ЛЕКСИКА:")
        print("-"*70)
        for word, count in list(analysis['overused_words'].items())[:10]:
            print(f"  • {word:20s} — {count:3d} раз(а)")

    # Структурная статистика
    if analysis.get('sentence_structure'):
        struct = analysis['sentence_structure']
        print("\n" + "-"*70)
        print("СТРУКТУРНАЯ СТАТИСТИКА:")
        print("-"*70)
        print(f"  Средняя длина предложения:     {struct.get('avg_length', 0):.1f} слов")
        print(f"  Вариативность длины:           {struct.get('length_variance', 0):.2f}")
        print(f"  Однородность длины:            {struct.get('length_uniformity', 0):.2%}")
        print(f"  Разнообразие начал:            {struct.get('first_word_diversity', 0):.2%}")

    print("\n" + "="*70)


if __name__ == '__main__':
    # Тестовый пример с паттернами ИИ
    test_text = """
    Важно отметить, что технологии развиваются быстро. Важно отметить, что это влияет на общество.
    Однако необходимо понимать риски. Однако нужно учитывать возможности. Кроме того, следует
    обратить внимание на этические аспекты. Кроме того, важно рассмотреть экономические последствия.
    В заключение, стоит отметить важность образования. В заключение, необходимо подчеркнуть роль
    инноваций в современном мире. Таким образом, мы видим значительные изменения. Таким образом,
    общество должно адаптироваться к новым реалиям.
    """

    print("\nТЕСТОВЫЙ АНАЛИЗ ТЕКСТА С ПАТТЕРНАМИ ИИ")
    score, analysis = detect_ai_writing_patterns(test_text)
    print_pattern_analysis_report(score, analysis)
