#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для определения искусственности текста (AI-generated text detection)
Использует эвристические методы для локального анализа без ML моделей
"""

import re
import math
from collections import Counter
from typing import Dict, List, Tuple
import statistics


# Характерные фразы для ИИ (русский и английский)
AI_PHRASES_RU = [
    'важно отметить',
    'стоит отметить',
    'следует отметить',
    'необходимо отметить',
    'как искусственный интеллект',
    'в качестве ии',
    'однако',
    'тем не менее',
    'более того',
    'кроме того',
    'в заключение',
    'таким образом',
    'следовательно',
    'в дополнение',
    'с другой стороны',
    'в то же время',
    'важно понимать',
    'стоит учитывать',
    'необходимо учитывать',
    'рекомендуется',
    'целесообразно',
]

AI_PHRASES_EN = [
    'as an ai',
    'as a language model',
    "i don't have",
    "i cannot",
    "it's important to note",
    "it's worth noting",
    'however',
    'furthermore',
    'moreover',
    'additionally',
    'in conclusion',
    'therefore',
    'thus',
    'consequently',
    'on the other hand',
    'nevertheless',
    'nonetheless',
]

# Переходные слова (transition words) - ИИ их использует чаще
TRANSITION_WORDS_RU = [
    'однако', 'тем не менее', 'кроме того', 'более того', 'также',
    'следовательно', 'таким образом', 'например', 'в частности',
    'в целом', 'в общем', 'наконец', 'в итоге', 'в результате'
]

TRANSITION_WORDS_EN = [
    'however', 'furthermore', 'moreover', 'additionally', 'therefore',
    'thus', 'consequently', 'nevertheless', 'nonetheless', 'meanwhile',
    'finally', 'in conclusion', 'for example', 'in particular'
]


def tokenize_sentences(text: str) -> List[str]:
    """Разбивает текст на предложения"""
    # Простой метод разбиения по знакам препинания
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def tokenize_words(text: str) -> List[str]:
    """Разбивает текст на слова"""
    words = re.findall(r'\b[а-яёa-z]+\b', text.lower(), re.UNICODE)
    return words


def calculate_sentence_length_variance(text: str) -> float:
    """
    Вычисляет вариативность длины предложений
    ИИ обычно создает более однородные по длине предложения
    """
    sentences = tokenize_sentences(text)
    if len(sentences) < 2:
        return 0.0

    lengths = [len(s.split()) for s in sentences]

    # Вычисляем коэффициент вариации
    mean_length = statistics.mean(lengths)
    if mean_length == 0:
        return 0.0

    std_dev = statistics.stdev(lengths) if len(lengths) > 1 else 0
    coefficient_of_variation = std_dev / mean_length

    return coefficient_of_variation


def detect_ai_phrases(text: str) -> Tuple[int, List[str]]:
    """
    Обнаруживает характерные для ИИ фразы

    Returns:
        Кортеж (количество найденных фраз, список найденных фраз)
    """
    text_lower = text.lower()
    found_phrases = []

    all_ai_phrases = AI_PHRASES_RU + AI_PHRASES_EN

    for phrase in all_ai_phrases:
        if phrase in text_lower:
            count = text_lower.count(phrase)
            found_phrases.extend([phrase] * count)

    return len(found_phrases), found_phrases


def calculate_transition_word_frequency(text: str) -> float:
    """
    Вычисляет частоту переходных слов
    ИИ использует их чаще для связности текста
    """
    words = tokenize_words(text)
    if not words:
        return 0.0

    transition_words = set(TRANSITION_WORDS_RU + TRANSITION_WORDS_EN)
    transition_count = sum(1 for word in words if word in transition_words)

    return transition_count / len(words)


def calculate_lexical_diversity(text: str) -> float:
    """
    Вычисляет лексическое разнообразие (Type-Token Ratio)
    Человеческий текст обычно более разнообразен
    """
    words = tokenize_words(text)
    if not words:
        return 0.0

    unique_words = set(words)
    ttr = len(unique_words) / len(words)

    return ttr


def calculate_average_word_length(text: str) -> float:
    """Вычисляет среднюю длину слова"""
    words = tokenize_words(text)
    if not words:
        return 0.0

    total_length = sum(len(word) for word in words)
    return total_length / len(words)


def detect_repetitive_patterns(text: str) -> Tuple[int, List[str]]:
    """
    Обнаруживает повторяющиеся паттерны (n-граммы)
    ИИ иногда повторяет одинаковые конструкции

    Returns:
        Кортеж (количество повторений, список повторяющихся паттернов)
    """
    words = tokenize_words(text)
    if len(words) < 6:
        return 0, []

    # Ищем повторяющиеся 3-граммы
    trigrams = []
    for i in range(len(words) - 2):
        trigram = ' '.join(words[i:i+3])
        trigrams.append(trigram)

    # Находим повторяющиеся
    trigram_counts = Counter(trigrams)
    repeated = [(gram, count) for gram, count in trigram_counts.items() if count > 1]

    total_repetitions = sum(count - 1 for _, count in repeated)
    repeated_patterns = [gram for gram, _ in repeated]

    return total_repetitions, repeated_patterns


def calculate_punctuation_ratio(text: str) -> float:
    """Вычисляет соотношение пунктуации к словам"""
    punctuation = len(re.findall(r'[,;:—–]', text))
    words = len(tokenize_words(text))

    if words == 0:
        return 0.0

    return punctuation / words


def calculate_perplexity_estimate(text: str) -> float:
    """
    Приблизительная оценка perplexity на основе частоты слов
    Более низкая perplexity может указывать на ИИ-текст
    """
    words = tokenize_words(text)
    if len(words) < 10:
        return 0.0

    # Вычисляем частоты слов
    word_counts = Counter(words)
    total_words = len(words)

    # Вычисляем энтропию
    entropy = 0
    for count in word_counts.values():
        probability = count / total_words
        entropy -= probability * math.log2(probability)

    # Perplexity = 2^entropy
    perplexity = 2 ** entropy

    return perplexity


def analyze_sentence_structure(text: str) -> Dict[str, float]:
    """
    Анализирует структуру предложений
    """
    sentences = tokenize_sentences(text)

    if not sentences:
        return {
            'avg_sentence_length': 0.0,
            'sentence_count': 0,
            'variance': 0.0
        }

    sentence_lengths = [len(s.split()) for s in sentences]

    return {
        'avg_sentence_length': statistics.mean(sentence_lengths),
        'sentence_count': len(sentences),
        'variance': calculate_sentence_length_variance(text),
        'min_length': min(sentence_lengths),
        'max_length': max(sentence_lengths)
    }


def calculate_ai_score(text: str) -> Tuple[float, Dict]:
    """
    Вычисляет общую оценку искусственности текста (0-100%)

    Args:
        text: Текст для анализа

    Returns:
        Кортеж (оценка 0-100, детальная информация)
    """
    if len(text.strip()) < 50:
        return 0.0, {'error': 'Текст слишком короткий для анализа (минимум 50 символов)'}

    # Собираем все метрики
    metrics = {}

    # 1. Вариативность длины предложений (низкая вариативность = больше ИИ)
    sentence_variance = calculate_sentence_length_variance(text)
    metrics['sentence_variance'] = sentence_variance
    # Нормализуем: низкая вариативность (< 0.3) указывает на ИИ
    variance_score = max(0, (0.5 - sentence_variance) / 0.5) * 100

    # 2. Характерные фразы ИИ
    ai_phrase_count, found_phrases = detect_ai_phrases(text)
    metrics['ai_phrases_count'] = ai_phrase_count
    metrics['ai_phrases'] = found_phrases[:5]  # Показываем первые 5
    # 1 фраза на 100 слов = 20 баллов
    words_count = len(tokenize_words(text))
    phrase_score = min(100, (ai_phrase_count / max(1, words_count / 100)) * 20)

    # 3. Частота переходных слов (высокая = больше ИИ)
    transition_freq = calculate_transition_word_frequency(text)
    metrics['transition_frequency'] = transition_freq
    # Более 5% = подозрительно
    transition_score = min(100, (transition_freq / 0.05) * 100)

    # 4. Лексическое разнообразие (низкое = больше ИИ)
    lexical_diversity = calculate_lexical_diversity(text)
    metrics['lexical_diversity'] = lexical_diversity
    # Низкое разнообразие (< 0.5) указывает на ИИ
    diversity_score = max(0, (0.6 - lexical_diversity) / 0.6) * 100

    # 5. Повторяющиеся паттерны
    repetition_count, repeated_patterns = detect_repetitive_patterns(text)
    metrics['repetition_count'] = repetition_count
    metrics['repeated_patterns'] = repeated_patterns[:3]
    # Каждое повторение добавляет баллы
    repetition_score = min(100, (repetition_count / max(1, words_count / 100)) * 30)

    # 6. Структура предложений
    sentence_structure = analyze_sentence_structure(text)
    metrics['sentence_structure'] = sentence_structure

    # 7. Perplexity
    perplexity = calculate_perplexity_estimate(text)
    metrics['perplexity'] = perplexity

    # Средний балл по всем метрикам
    scores = [
        variance_score * 0.25,      # 25% веса
        phrase_score * 0.30,        # 30% веса
        transition_score * 0.15,    # 15% веса
        diversity_score * 0.20,     # 20% веса
        repetition_score * 0.10,    # 10% веса
    ]

    total_score = sum(scores)

    metrics['component_scores'] = {
        'sentence_uniformity': round(variance_score, 2),
        'ai_phrases': round(phrase_score, 2),
        'transition_words': round(transition_score, 2),
        'lexical_monotony': round(diversity_score, 2),
        'repetitions': round(repetition_score, 2),
    }

    return round(total_score, 2), metrics


def print_ai_detection_report(score: float, metrics: Dict):
    """
    Выводит детальный отчет об анализе текста

    Args:
        score: Оценка искусственности (0-100)
        metrics: Детальные метрики
    """
    print("\n" + "="*70)
    print("АНАЛИЗ ИСКУССТВЕННОСТИ ТЕКСТА")
    print("="*70)

    # Определяем вероятность
    if score < 20:
        verdict = "ВЕРОЯТНО ЧЕЛОВЕК"
        color = "🟢"
    elif score < 40:
        verdict = "СКОРЕЕ ВСЕГО ЧЕЛОВЕК"
        color = "🟡"
    elif score < 60:
        verdict = "НЕОПРЕДЕЛЕННО"
        color = "🟠"
    elif score < 80:
        verdict = "ВЕРОЯТНО ИИ"
        color = "🟠"
    else:
        verdict = "СКОРЕЕ ВСЕГО ИИ"
        color = "🔴"

    print(f"\n{color} ОЦЕНКА ИСКУССТВЕННОСТИ: {score:.1f}% - {verdict}")
    print("\n" + "-"*70)
    print("ДЕТАЛЬНЫЙ АНАЛИЗ:")
    print("-"*70)

    if 'component_scores' in metrics:
        scores = metrics['component_scores']
        print(f"\n  Однородность предложений:     {scores['sentence_uniformity']:5.1f}% {'⚠️' if scores['sentence_uniformity'] > 50 else '✓'}")
        print(f"  Характерные фразы ИИ:          {scores['ai_phrases']:5.1f}% {'⚠️' if scores['ai_phrases'] > 50 else '✓'}")
        print(f"  Частота переходных слов:       {scores['transition_words']:5.1f}% {'⚠️' if scores['transition_words'] > 50 else '✓'}")
        print(f"  Лексическая монотонность:      {scores['lexical_monotony']:5.1f}% {'⚠️' if scores['lexical_monotony'] > 50 else '✓'}")
        print(f"  Повторяющиеся паттерны:        {scores['repetitions']:5.1f}% {'⚠️' if scores['repetitions'] > 50 else '✓'}")

    print("\n" + "-"*70)
    print("СТАТИСТИКА ТЕКСТА:")
    print("-"*70)

    if 'sentence_structure' in metrics:
        struct = metrics['sentence_structure']
        print(f"  Количество предложений:        {struct['sentence_count']}")
        print(f"  Средняя длина предложения:     {struct['avg_sentence_length']:.1f} слов")
        print(f"  Вариативность длины:           {metrics.get('sentence_variance', 0):.3f}")

    print(f"  Лексическое разнообразие:      {metrics.get('lexical_diversity', 0):.3f}")
    print(f"  Perplexity (оценка):           {metrics.get('perplexity', 0):.1f}")

    if metrics.get('ai_phrases_count', 0) > 0:
        print("\n" + "-"*70)
        print("НАЙДЕННЫЕ ХАРАКТЕРНЫЕ ФРАЗЫ ИИ:")
        print("-"*70)
        for phrase in metrics.get('ai_phrases', []):
            print(f"  • {phrase}")

    if metrics.get('repetition_count', 0) > 0:
        print("\n" + "-"*70)
        print("ПОВТОРЯЮЩИЕСЯ КОНСТРУКЦИИ:")
        print("-"*70)
        for pattern in metrics.get('repeated_patterns', []):
            print(f"  • {pattern}")

    print("\n" + "="*70)


if __name__ == '__main__':
    # Тестовый пример
    ai_text = """
    Важно отметить, что искусственный интеллект становится все более важным инструментом.
    Однако необходимо понимать его ограничения. Тем не менее, технология продолжает развиваться.
    Кроме того, следует учитывать этические аспекты. В заключение, стоит отметить, что ИИ
    имеет большой потенциал. Таким образом, необходимо ответственно подходить к его использованию.
    """

    human_text = """
    Вчера я был в парке. Погода была отличная! Дети играли на площадке, собаки бегали.
    Мне очень понравилось. Купил мороженое, посидел на лавочке. Хорошо отдохнул.
    Завтра снова пойду, если будет время и настроение.
    """

    print("\n" + "="*70)
    print("ТЕСТ 1: Текст, похожий на ИИ")
    print("="*70)
    score, metrics = calculate_ai_score(ai_text)
    print_ai_detection_report(score, metrics)

    print("\n\n" + "="*70)
    print("ТЕСТ 2: Человеческий текст")
    print("="*70)
    score, metrics = calculate_ai_score(human_text)
    print_ai_detection_report(score, metrics)
