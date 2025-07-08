#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR - استخراج اطلاعات از فایل‌های PDF اظهارنامه
نسخه: 2.0.0
تاریخ: 2024
"""

__version__ = "2.0.0"
__author__ = "Seyed Mahdi Vakhshoori"
__email__ = "seyedmahdivakhshoori@gmail.com"
__description__ = "نرم‌افزار هوشمند استخراج اطلاعات از فایل‌های PDF اظهارنامه"
__url__ = "https://github.com/seyedmahdivakhshoori/pdf-ocr"

from .pdf_ocr import main, MainWindow, PDFProcessor, SettingsManager, PersianDateConverter

__all__ = [
    "main",
    "MainWindow", 
    "PDFProcessor",
    "SettingsManager",
    "PersianDateConverter",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__"
] 