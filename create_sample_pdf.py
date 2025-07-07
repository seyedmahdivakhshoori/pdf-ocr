#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ایجاد فایل PDF نمونه برای تست برنامه PDF OCR
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_sample_pdf():
    """ایجاد یک فایل PDF نمونه برای تست"""
    
    # ایجاد فایل PDF
    c = canvas.Canvas("your_first_sample.pdf", pagesize=letter)
    width, height = letter
    
    # تنظیم فونت
    c.setFont("Helvetica", 12)
    
    # اضافه کردن متن نمونه
    c.drawString(100, height - 100, "فاکتور نمونه")
    c.drawString(100, height - 150, "شماره فاکتور: 12345")
    c.drawString(100, height - 200, "تاریخ: 1402/12/15")
    c.drawString(100, height - 250, "مشتری: شرکت نمونه")
    
    # اضافه کردن جدول محصولات
    c.drawString(100, height - 300, "محصولات:")
    c.drawString(100, height - 320, "1. لپ‌تاپ - تعداد: 2 - قیمت واحد: 15000000")
    c.drawString(100, height - 340, "2. موس - تعداد: 5 - قیمت واحد: 500000")
    
    # اضافه کردن مبلغ کل
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 400, "مبلغ کل: 3138.00 تومان")
    
    # اضافه کردن متن‌های دیگر برای تست
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 450, "مبلغ قابل پرداخت: 3138.00")
    c.drawString(100, height - 500, "تخفیف: 0.00")
    c.drawString(100, height - 550, "مالیات: 0.00")
    
    c.save()
    print("✅ فایل PDF نمونه با موفقیت ایجاد شد: your_first_sample.pdf")

if __name__ == "__main__":
    create_sample_pdf() 