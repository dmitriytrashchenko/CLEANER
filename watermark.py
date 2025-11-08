#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для добавления невидимых водяных знаков в текст (стеганография)
Использует zero-width Unicode символы для кодирования метаданных
"""

import json
import hashlib
import time
import base64
from typing import Dict, Optional, Tuple
from datetime import datetime


# Невидимые символы для бинарного кодирования
ZERO = '\u200B'  # Zero Width Space (0)
ONE = '\u200C'   # Zero Width Non-Joiner (1)
SEPARATOR = '\u200D'  # Zero Width Joiner (разделитель)

# Маркер начала водяного знака
WATERMARK_START = '\uFEFF'  # Zero Width No-Break Space (BOM)


def text_to_binary(text: str) -> str:
    """Преобразует текст в бинарную строку"""
    return ''.join(format(ord(char), '08b') for char in text)


def binary_to_text(binary: str) -> str:
    """Преобразует бинарную строку в текст"""
    chars = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def encode_binary_to_invisible(binary: str) -> str:
    """Кодирует бинарную строку в невидимые символы"""
    return ''.join(ZERO if bit == '0' else ONE for bit in binary)


def decode_invisible_to_binary(invisible: str) -> str:
    """Декодирует невидимые символы в бинарную строку"""
    binary = ''
    for char in invisible:
        if char == ZERO:
            binary += '0'
        elif char == ONE:
            binary += '1'
    return binary


def create_watermark_data(author: str, metadata: Optional[Dict] = None) -> Dict:
    """
    Создает данные водяного знака

    Args:
        author: Имя автора
        metadata: Дополнительные метаданные

    Returns:
        Словарь с данными водяного знака
    """
    watermark = {
        'author': author,
        'timestamp': int(time.time()),
        'date': datetime.now().isoformat(),
    }

    if metadata:
        watermark['metadata'] = metadata

    # Добавляем контрольную сумму
    data_str = json.dumps(watermark, ensure_ascii=True, separators=(',', ':'))
    watermark['checksum'] = hashlib.md5(data_str.encode()).hexdigest()[:8]

    return watermark


def embed_watermark(text: str, author: str, metadata: Optional[Dict] = None) -> str:
    """
    Встраивает невидимый водяной знак в текст

    Args:
        text: Исходный текст
        author: Имя автора
        metadata: Дополнительные метаданные

    Returns:
        Текст с встроенным водяным знаком
    """
    # Создаем данные водяного знака
    watermark_data = create_watermark_data(author, metadata)

    # Сериализуем в JSON и кодируем в base64 для надежности
    watermark_json = json.dumps(watermark_data, ensure_ascii=True, separators=(',', ':'))
    watermark_b64 = base64.b64encode(watermark_json.encode('utf-8')).decode('ascii')

    # Конвертируем в бинарный формат
    binary = text_to_binary(watermark_b64)

    # Кодируем в невидимые символы
    invisible_watermark = encode_binary_to_invisible(binary)

    # Встраиваем водяной знак в начало текста
    watermarked_text = WATERMARK_START + invisible_watermark + SEPARATOR + text

    return watermarked_text


def extract_watermark(text: str) -> Optional[Dict]:
    """
    Извлекает водяной знак из текста

    Args:
        text: Текст с возможным водяным знаком

    Returns:
        Словарь с данными водяного знака или None
    """
    try:
        # Ищем маркер начала
        if not text.startswith(WATERMARK_START):
            return None

        # Удаляем маркер начала
        text = text[len(WATERMARK_START):]

        # Ищем разделитель
        separator_pos = text.find(SEPARATOR)
        if separator_pos == -1:
            return None

        # Извлекаем невидимые символы
        invisible_data = text[:separator_pos]

        # Декодируем в бинарную строку
        binary = decode_invisible_to_binary(invisible_data)

        # Конвертируем в текст (base64)
        watermark_b64 = binary_to_text(binary)

        # Декодируем base64
        watermark_json = base64.b64decode(watermark_b64).decode('utf-8')

        # Парсим JSON
        watermark_data = json.loads(watermark_json)

        # Проверяем контрольную сумму
        checksum = watermark_data.pop('checksum', None)
        data_str = json.dumps(watermark_data, ensure_ascii=True, separators=(',', ':'))
        calculated_checksum = hashlib.md5(data_str.encode()).hexdigest()[:8]

        if checksum != calculated_checksum:
            return None

        return watermark_data

    except Exception:
        return None


def remove_watermark(text: str) -> str:
    """
    Удаляет водяной знак из текста

    Args:
        text: Текст с водяным знаком

    Returns:
        Текст без водяного знака
    """
    if not text.startswith(WATERMARK_START):
        return text

    # Удаляем маркер начала
    text = text[len(WATERMARK_START):]

    # Ищем разделитель
    separator_pos = text.find(SEPARATOR)
    if separator_pos == -1:
        return text

    # Возвращаем текст после водяного знака
    return text[separator_pos + len(SEPARATOR):]


def has_watermark(text: str) -> bool:
    """
    Проверяет наличие водяного знака в тексте

    Args:
        text: Текст для проверки

    Returns:
        True если водяной знак найден
    """
    return extract_watermark(text) is not None


def create_distributed_watermark(text: str, author: str, density: float = 0.1) -> str:
    """
    Создает распределенный водяной знак по всему тексту
    (более устойчив к редактированию)

    Args:
        text: Исходный текст
        author: Имя автора
        density: Плотность встраивания (0.0-1.0)

    Returns:
        Текст с распределенным водяным знаком
    """
    # Создаем короткую сигнатуру
    signature = hashlib.md5(author.encode()).hexdigest()[:16]
    binary = text_to_binary(signature)

    # Создаем паттерн из невидимых символов
    pattern = encode_binary_to_invisible(binary)

    # Распределяем по тексту после знаков препинания
    result = []
    pattern_index = 0
    chars_since_last = 0
    insertion_interval = max(1, int(10 / max(density, 0.01)))

    for i, char in enumerate(text):
        result.append(char)
        chars_since_last += 1

        # Вставляем после знаков препинания с определенной частотой
        if char in '.!?,;:' and chars_since_last >= insertion_interval:
            if pattern_index < len(pattern):
                result.append(pattern[pattern_index])
                pattern_index = (pattern_index + 1) % len(pattern)
                chars_since_last = 0

    return ''.join(result)


def detect_distributed_watermark(text: str, author: str) -> Tuple[bool, float]:
    """
    Определяет наличие распределенного водяного знака

    Args:
        text: Текст для проверки
        author: Предполагаемый автор

    Returns:
        Кортеж (найден ли водяной знак, уверенность 0-1)
    """
    # Создаем ожидаемую сигнатуру
    signature = hashlib.md5(author.encode()).hexdigest()[:16]
    binary = text_to_binary(signature)
    expected_pattern = encode_binary_to_invisible(binary)

    # Извлекаем все невидимые символы из текста
    invisible_chars = ''.join(char for char in text if char in [ZERO, ONE])

    if not invisible_chars:
        return False, 0.0

    # Проверяем совпадение с паттерном
    matches = 0
    total_checks = min(len(invisible_chars), len(expected_pattern))

    if total_checks == 0:
        return False, 0.0

    for i in range(total_checks):
        pattern_char = expected_pattern[i % len(expected_pattern)]
        if invisible_chars[i] == pattern_char:
            matches += 1

    confidence = matches / total_checks

    # Считаем найденным если уверенность > 70%
    return confidence > 0.7, confidence


def print_watermark_info(watermark_data: Dict):
    """
    Выводит информацию о водяном знаке

    Args:
        watermark_data: Данные водяного знака
    """
    print("\n" + "="*70)
    print("ИНФОРМАЦИЯ О ВОДЯНОМ ЗНАКЕ")
    print("="*70)
    print(f"Автор:        {watermark_data.get('author', 'Неизвестно')}")
    print(f"Дата:         {watermark_data.get('date', 'Неизвестно')}")
    print(f"Timestamp:    {watermark_data.get('timestamp', 'Неизвестно')}")

    if 'metadata' in watermark_data:
        print("\nДополнительные метаданные:")
        for key, value in watermark_data['metadata'].items():
            print(f"  {key}: {value}")

    print("="*70)


if __name__ == '__main__':
    # Пример использования
    test_text = "Это пример текста для демонстрации водяных знаков. Текст будет защищен невидимой подписью."

    print("Оригинальный текст:")
    print(test_text)
    print(f"Длина: {len(test_text)} символов\n")

    # Встраиваем водяной знак
    watermarked = embed_watermark(
        test_text,
        author="Иван Иванов",
        metadata={"version": "1.0", "project": "CLEANER"}
    )

    print("Текст с водяным знаком:")
    print(watermarked)
    print(f"Длина: {len(watermarked)} символов\n")

    # Извлекаем водяной знак
    extracted = extract_watermark(watermarked)
    if extracted:
        print_watermark_info(extracted)

    # Удаляем водяной знак
    cleaned = remove_watermark(watermarked)
    print("\nТекст после удаления водяного знака:")
    print(cleaned)
    print(f"Совпадает с оригиналом: {cleaned == test_text}")
