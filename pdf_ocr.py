#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR - استخراج اطلاعات از فایل‌های PDF اظهارنامه
نسخه: 2.0.0
تاریخ: 2024
"""

import sys
import os
import json
import openai
import pandas as pd
import PyPDF2
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, 
    QProgressBar, QTableWidget, QTableWidgetItem, QTabWidget,
    QGroupBox, QGridLayout, QMessageBox, QSpinBox, QComboBox,
    QSplitter, QFrame, QScrollArea, QSizePolicy, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QFontDatabase

# بارگذاری متغیرهای محیطی
load_dotenv()

class PersianDateConverter:
    """تبدیل تاریخ میلادی به شمسی"""
    
    def __init__(self):
        # جدول تبدیل سال‌های میلادی به شمسی
        self.gregorian_to_persian = {
            2020: 1399, 2021: 1400, 2022: 1401, 2023: 1402, 2024: 1403, 2025: 1404,
            2026: 1405, 2027: 1406, 2028: 1407, 2029: 1408, 2030: 1409, 2031: 1410,
            2010: 1389, 2011: 1390, 2012: 1391, 2013: 1392, 2014: 1393, 2015: 1394,
            2016: 1395, 2017: 1396, 2018: 1397, 2019: 1398, 2000: 1379, 2001: 1380,
            2002: 1381, 2003: 1382, 2004: 1383, 2005: 1384, 2006: 1385, 2007: 1386,
            2008: 1387, 2009: 1388, 1990: 1369, 1991: 1370, 1992: 1371, 1993: 1372,
            1994: 1373, 1995: 1374, 1996: 1375, 1997: 1376, 1998: 1377, 1999: 1378
        }
        
        # نام ماه‌های شمسی
        self.persian_months = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد', 4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر', 10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        
        # تعداد روزهای هر ماه شمسی
        self.persian_month_days = {
            1: 31, 2: 31, 3: 31, 4: 31, 5: 31, 6: 31,
            7: 30, 8: 30, 9: 30, 10: 30, 11: 30, 12: 29
        }
    
    def convert_gregorian_to_persian(self, gregorian_date_str):
        """تبدیل تاریخ میلادی به شمسی"""
        try:
            # پاک کردن متن اضافی
            gregorian_date_str = gregorian_date_str.strip()
            
            # الگوهای مختلف تاریخ
            patterns = [
                r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',  # 2024/01/15 یا 2024-01-15
                r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',  # 15/01/2024 یا 15-01-2024
                r'(\d{4})\.(\d{1,2})\.(\d{1,2})',        # 2024.01.15
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})',        # 15.01.2024
            ]
            
            import re
            for pattern in patterns:
                match = re.search(pattern, gregorian_date_str)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # سال اول
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # روز اول
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    
                    return self._convert_date(year, month, day)
            
            # اگر هیچ الگویی پیدا نشد، سعی می‌کنیم با datetime پارس کنیم
            try:
                date_obj = datetime.strptime(gregorian_date_str, '%Y-%m-%d')
                return self._convert_date(date_obj.year, date_obj.month, date_obj.day)
            except:
                pass
            
            # اگر نتوانستیم تبدیل کنیم، همان متن را برمی‌گردانیم
            return gregorian_date_str
            
        except Exception as e:
            return gregorian_date_str
    
    def _convert_date(self, gregorian_year, gregorian_month, gregorian_day):
        """تبدیل تاریخ میلادی به شمسی با محاسبات دقیق"""
        try:
            # تبدیل سال میلادی به شمسی
            persian_year = self.gregorian_to_persian.get(gregorian_year, gregorian_year - 621)
            
            # محاسبه روز سال میلادی
            gregorian_days_in_year = self._days_in_gregorian_year(gregorian_year, gregorian_month, gregorian_day)
            
            # محاسبه روز سال شمسی + اضافه کردن یک روز برای جبران اختلاف
            persian_days_in_year = gregorian_days_in_year - 79 + 1  # اختلاف تقویم‌ها + یک روز اضافی
            
            if persian_days_in_year <= 0:
                persian_year -= 1
                persian_days_in_year += 365 if self._is_persian_leap_year(persian_year) else 366
            
            # محاسبه ماه و روز شمسی
            persian_month = 1
            persian_day = persian_days_in_year
            
            for month in range(1, 13):
                days_in_month = self.persian_month_days[month]
                if month == 12 and self._is_persian_leap_year(persian_year):
                    days_in_month = 30
                
                if persian_day <= days_in_month:
                    break
                
                persian_day -= days_in_month
                persian_month += 1
            
            # فرمت‌بندی تاریخ شمسی
            return f"{persian_year}/{persian_month:02d}/{persian_day:02d}"
            
        except:
            return f"{gregorian_year}/{gregorian_month:02d}/{gregorian_day:02d}"
    
    def _days_in_gregorian_year(self, year, month, day):
        """محاسبه روز سال میلادی"""
        days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # بررسی سال کبیسه
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            days_in_month[2] = 29
        
        days = day
        for i in range(1, month):
            days += days_in_month[i]
        
        return days
    
    def _is_persian_leap_year(self, year):
        """بررسی سال کبیسه شمسی"""
        return (year + 2346) % 33 in [1, 5, 9, 13, 17, 22, 26, 30]

class SettingsManager:
    """مدیریت تنظیمات برنامه"""
    
    def __init__(self):
        self.settings = QSettings('PDF_OCR', 'ChatGPT_OCR')
        self.usage_file = 'usage_stats.json'
        self.load_usage_stats()
    
    def get_api_key(self):
        return self.settings.value('api_key', '')
    
    def set_api_key(self, api_key):
        self.settings.setValue('api_key', api_key)
    
    def get_model(self):
        return self.settings.value('model', 'gpt-3.5-turbo')
    
    def set_model(self, model):
        self.settings.setValue('model', model)
    
    def get_max_tokens(self):
        return int(self.settings.value('max_tokens', 150))  # کاهش پیش‌فرض max_tokens
    
    def set_max_tokens(self, tokens):
        self.settings.setValue('max_tokens', tokens)
    
    def load_usage_stats(self):
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    self.usage_stats = json.load(f)
                    # اطمینان از وجود فیلدهای جدید
                    if 'daily_usage' in self.usage_stats:
                        for date in self.usage_stats['daily_usage']:
                            if 'files' not in self.usage_stats['daily_usage'][date]:
                                self.usage_stats['daily_usage'][date]['files'] = 0
                            if 'total_size' not in self.usage_stats['daily_usage'][date]:
                                self.usage_stats['daily_usage'][date]['total_size'] = 0
            else:
                self.usage_stats = {
                    'total_tokens': 0,
                    'total_cost': 0.0,
                    'daily_usage': {},
                    'files_processed': 0
                }
        except:
            self.usage_stats = {
                'total_tokens': 0,
                'total_cost': 0.0,
                'daily_usage': {},
                'files_processed': 0
            }
    
    def save_usage_stats(self):
        with open(self.usage_file, 'w', encoding='utf-8') as f:
            json.dump(self.usage_stats, f, ensure_ascii=False, indent=2)
    
    def add_usage(self, tokens, cost, files_processed=1, total_size=0):
        today = datetime.now().strftime('%Y-%m-%d')
        self.usage_stats['total_tokens'] += tokens
        self.usage_stats['total_cost'] += cost
        self.usage_stats['files_processed'] += files_processed
        
        if today not in self.usage_stats['daily_usage']:
            self.usage_stats['daily_usage'][today] = {
                'tokens': 0, 
                'cost': 0, 
                'files': 0, 
                'total_size': 0
            }
        
        self.usage_stats['daily_usage'][today]['tokens'] += tokens
        self.usage_stats['daily_usage'][today]['cost'] += cost
        self.usage_stats['daily_usage'][today]['files'] += files_processed
        self.usage_stats['daily_usage'][today]['total_size'] += total_size
        self.save_usage_stats()

class PDFProcessor(QThread):
    """پردازش PDF در thread جداگانه"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, files, api_key, model, max_tokens=None):
        super().__init__()
        self.files = files
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.settings_manager = SettingsManager()
        self.date_converter = PersianDateConverter()
    
    def run(self):
        try:
            client = openai.OpenAI(api_key=self.api_key)
            all_extracted_data = []
            total_size = 0
            file_names = []
            total_tokens_used = 0
            total_cost = 0
            
            # پردازش فایل‌ها به صورت دسته‌ای برای کاهش مصرف توکن
            batch_size = 3  # پردازش 3 فایل در هر دسته
            for i in range(0, len(self.files), batch_size):
                batch_files = self.files[i:i+batch_size]
                self.progress.emit(f"پردازش دسته {i//batch_size + 1}: فایل‌های {i+1}-{min(i+batch_size, len(self.files))}")
                
                # پردازش دسته‌ای
                batch_results = self.process_batch(client, batch_files)
                if batch_results:
                    all_extracted_data.extend(batch_results['data'])
                    total_tokens_used += batch_results['tokens']
                    total_cost += batch_results['cost']
                    
                    # اضافه کردن نام فایل‌ها و حجم
                    for file_path in batch_files:
                        total_size += os.path.getsize(file_path)
                        file_names.append(os.path.basename(file_path))
                else:
                    self.error.emit(f"خطا در پردازش دسته {i//batch_size + 1}")
                    return
            
            if not all_extracted_data:
                self.error.emit("هیچ داده‌ای از فایل‌ها استخراج نشد!")
                return
            
            # ذخیره آمار استفاده
            total_size_kb = round(total_size / 1024, 2)
            self.settings_manager.add_usage(total_tokens_used, total_cost, len(file_names), total_size_kb)
            
            # ساختاردهی نتایج برای نمایش
            results = []
            for i, data in enumerate(all_extracted_data):
                result = {
                    'شماره اظهارنامه': data.get('شماره اظهارنامه', ''),
                    'ارز و مبلغ کل فاکتور': data.get('ارز و مبلغ کل فاکتور', '')
                }
                results.append(result)
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def extract_text_from_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += f"\n--- صفحه {page_num + 1} ---\n"
                    text += page.extract_text()
                return text
        except Exception as e:
            self.error.emit(f"خطا در خواندن PDF: {str(e)}")
            return None
    
    def process_with_chatgpt(self, client, text):
        try:
            # پیش‌پردازش متن بهینه: خطوط مهم برای استخراج شماره اظهارنامه و ارز و مبلغ کل فاکتور
            text = self.preprocess_text(text)
            
            prompt = f"""استخراج اطلاعات از متن:
- ارز و مبلغ کل فاکتور: فقط اگر عنوان دقیق «22. ارز و مبلغ کل فاکتور :» وجود داشت، مقدار عددی بلافاصله زیر آن را استخراج کن (مثلاً: 1000000 ریال یا 500 دلار). اگر این عنوان نبود یا مقدار زیر آن نبود، مقدار را خالی بگذار. به هیچ عنوان مقدار زیر عناوین دیگر را استخراج نکن.

JSON: {{"ارز و مبلغ کل فاکتور":""}}

متن: {text[:1000]}"""
            
            max_tokens = 150  # کاهش بیشتر max_tokens
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "فقط JSON برگردان."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.0  # کاهش temperature برای دقت بیشتر
            )
            
            # محاسبه هزینه
            tokens_used = response.usage.total_tokens
            if self.model == "gpt-3.5-turbo":
                cost = tokens_used * 0.000002  # $0.002 per 1K tokens
            else:
                cost = tokens_used * 0.00003   # $0.03 per 1K tokens
            
            # پارس کردن JSON پاسخ
            try:
                import json
                response_text = response.choices[0].message.content.strip()
                # حذف کدهای markdown اگر وجود داشته باشد
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                extracted_data = json.loads(response_text)
                extracted_data['tokens_used'] = tokens_used
                extracted_data['cost'] = cost
                
                return extracted_data, tokens_used, cost
                
            except json.JSONDecodeError:
                # اگر JSON نبود، سعی می‌کنیم با regex استخراج کنیم
                import re
                extracted_data = {
                    'شماره اظهارنامه': '',
                    'ارز و مبلغ کل فاکتور': '',
                    'tokens_used': tokens_used,
                    'cost': cost
                }
                
                # استخراج با regex بهبود یافته
                patterns = {
                    'شماره اظهارنامه': r'شماره اظهارنامه["\s]*:["\s]*(.*?)(?:\n|$)',
                    'ارز و مبلغ کل فاکتور': r'ارز و مبلغ کل فاکتور["\s]*:["\s]*(.*?)(?:\n|$)'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        extracted_data[key] = match.group(1).strip()
                
                return extracted_data, tokens_used, cost
            
        except Exception as e:
            self.error.emit(f"خطا در ارتباط با ChatGPT: {str(e)}")
            return None, 0, 0
    
    def preprocess_text(self, text):
        """پیش‌پردازش بهینه: خطوط مهم برای استخراج شماره اظهارنامه و ارز و مبلغ کل فاکتور"""
        import re
        lines = text.split('\n')
        filtered_lines = []
        keywords = ['اظهارنامه', 'مبلغ', 'ارز', 'فاکتور']
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            # اگر خط شامل 'ارز و مبلغ کل فاکتور' بود، این خط و خط بعدی را اضافه کن
            if 'ارز و مبلغ کل فاکتور' in line:
                filtered_lines.append(line)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line:
                        filtered_lines.append(next_line)
                i += 2
                continue
            # فقط خطوطی که هم عدد دارند و هم یکی از کلمات کلیدی
            if any(k in line for k in keywords) and re.search(r'\d', line):
                filtered_lines.append(line)
            # یا خطوطی که فقط عدد طولانی (مثلاً شماره اظهارنامه) دارند
            elif re.search(r'\d{8,}', line):
                filtered_lines.append(line)
            i += 1
        return '\n'.join(filtered_lines[:20])  # حداکثر ۲۰ خط برای کاهش بیشتر مصرف توکن

    def process_batch(self, client, files):
        """پردازش هر فایل به صورت جداگانه و مستقل و فقط استخراج ارز و مبلغ کل فاکتور"""
        try:
            results = []
            total_tokens = 0
            total_cost = 0
            for file_path in files:
                text = self.extract_text_from_pdf(file_path)
                if not text:
                    continue
                processed_text = self.preprocess_text(text)
                extracted_data, tokens_used, cost = self.process_with_chatgpt(client, processed_text[:800])
                total_tokens += tokens_used
                total_cost += cost
                if extracted_data:
                    results.append({
                        'ارز و مبلغ کل فاکتور': extracted_data.get('ارز و مبلغ کل فاکتور', '')
                    })
            return {
                'data': results,
                'tokens': total_tokens,
                'cost': total_cost
            }
        except Exception as e:
            self.error.emit(f"خطا در پردازش دسته‌ای: {str(e)}")
            return None

    def extract_faktor_value(self, text):
        import re
        lines = text.split('\n')
        # الگوی انعطاف‌پذیر: با یا بدون شماره، اعداد فارسی و انگلیسی، با یا بدون دو نقطه
        pattern = re.compile(r'^(۲۲|22)?[\s\.\-]*ارز و مبلغ کل فاکتور[\s\:]*$', re.UNICODE)
        for i, line in enumerate(lines):
            if pattern.match(line.strip()):
                if i + 1 < len(lines):
                    return lines[i+1].strip()
        return ''

class MainWindow(QMainWindow):
    """پنجره اصلی برنامه"""
    
    export_columns = [
        'ارز و مبلغ کل فاکتور'
    ]
    
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.init_ui()
        self.load_settings()
        
        # تایمر برای به‌روزرسانی آمار
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)  # هر 5 ثانیه
    
    def setup_persian_font(self):
        """تنظیم فونت فارسی برای برنامه"""
        try:
            # مسیر فونت‌های محلی
            font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
            
            # فونت‌های Segoe UI
            font_files = {
                'Segoe UI': 'segoeui.ttf',
                'Segoe UI Bold': 'segoeuib.ttf',
                'Segoe UI Italic': 'segoeuii.ttf',
                'Segoe UI Bold Italic': 'segoeuiz.ttf'
            }
            
            # ثبت فونت‌ها
            for font_name, font_file in font_files.items():
                font_path = os.path.join(font_dir, font_file)
                if os.path.exists(font_path):
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        print(f"✅ فونت {font_name} با موفقیت بارگذاری شد")
                    else:
                        print(f"❌ خطا در بارگذاری فونت {font_name}")
                else:
                    print(f"⚠️ فایل فونت {font_file} یافت نشد")
            
            # تنظیم فونت پیش‌فرض
            app = QApplication.instance()
            if app:
                font = QFont("Segoe UI", 9)
                app.setFont(font)
                
        except Exception as e:
            print(f"⚠️ خطا در تنظیم فونت: {str(e)}")
            # استفاده از فونت پیش‌فرض سیستم
            pass
    
    def init_ui(self):
        self.setWindowTitle("📄 استخراج شماره اظهارنامه - نسخه بهینه")
        self.setGeometry(100, 100, 1400, 900)
        
        # تنظیم فونت فارسی
        self.setup_persian_font()
        
        # تنظیم استایل
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #c0c0c0;
                border-radius: 3px;
                padding: 5px;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #0078d4;
            }
        """)
        
        # ایجاد widget مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # ایجاد layout اصلی
        main_layout = QVBoxLayout(central_widget)
        
        # ایجاد tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # ایجاد tab ها
        self.create_main_tab()
        self.create_settings_tab()
        self.create_stats_tab()
    
    def create_main_tab(self):
        """ایجاد tab اصلی"""
        main_tab = QWidget()
        layout = QVBoxLayout(main_tab)
        layout.setSpacing(15)  # افزایش فاصله بین بخش‌ها
        
        # بخش آمار سریع
        stats_group = QGroupBox("📊 آمار سریع")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078d4;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #0078d4;
                font-size: 14px;
            }
        """)
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setSpacing(20)
        
        self.total_files_label = QLabel("فایل‌های پردازش شده: 0")
        self.total_tokens_label = QLabel("کل توکن‌ها: 0")
        self.total_cost_label = QLabel("کل هزینه: $0.00")
        self.today_tokens_label = QLabel("توکن‌های امروز: 0")
        
        for label in [self.total_files_label, self.total_tokens_label, 
                     self.total_cost_label, self.today_tokens_label]:
            label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e8f4fd, stop:1 #d1e9fb);
                    padding: 12px 15px;
                    border-radius: 8px;
                    border: 2px solid #0078d4;
                    font-weight: bold;
                    color: #005a9e;
                    min-width: 150px;
                    text-align: center;
                }
            """)
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_group)
        
        # بخش آپلود و پردازش
        process_group = QGroupBox("🔄 پردازش فایل‌های اظهارنامه")
        process_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #28a745;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8fff9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #28a745;
                font-size: 14px;
            }
        """)
        process_layout = QVBoxLayout(process_group)
        process_layout.setSpacing(15)
        
        # دکمه‌های آپلود و نوع فایل در یک ردیف
        upload_layout = QHBoxLayout()
        upload_layout.setSpacing(10)

        # باکس نوع فایل‌های آپلودی (در ابتدای راست)
        type_group = QGroupBox("نوع فایل‌های آپلودی")
        type_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #fd7e14;
                border-radius: 8px;
                margin-top: 0px;
                padding-top: 10px;
                background-color: #fff8f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #fd7e14;
                font-size: 14px;
            }
        """)
        type_group.setFixedWidth(220)
        type_layout = QHBoxLayout(type_group)
        type_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.radio_import = QRadioButton("واردات")
        self.radio_export = QRadioButton("صادرات")
        self.radio_import.setChecked(True)
        for r in [self.radio_import, self.radio_export]:
            r.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px 16px;")
        type_layout.addWidget(self.radio_import)
        type_layout.addWidget(self.radio_export)
        type_layout.addStretch()
        self.selected_file_type = 'import'
        self.radio_import.toggled.connect(lambda checked: self.set_file_type('import' if checked else 'export'))
        upload_layout.addWidget(type_group)
        upload_layout.addSpacing(230)
        self.upload_btn = QPushButton("📁 انتخاب فایل‌های PDF")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #106ebe);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-width: 180px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106ebe, stop:1 #005a9e);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #004578);
            }
        """)
        self.upload_btn.clicked.connect(self.upload_files)
        self.clear_btn = QPushButton("🗑️ پاک کردن لیست")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c82333, stop:1 #bd2130);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bd2130, stop:1 #a71e2a);
            }
        """)
        self.clear_btn.clicked.connect(self.clear_files)
        upload_layout.addWidget(self.upload_btn)
        upload_layout.addWidget(self.clear_btn)
        upload_layout.addStretch()
        process_layout.addLayout(upload_layout)
        
        # لیست فایل‌ها
        files_label = QLabel("📋 فایل‌های انتخاب شده:")
        files_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #495057;
                font-size: 13px;
                padding: 5px 0;
            }
        """)
        process_layout.addWidget(files_label)

        # ویجت لیست فایل‌ها (جدید)
        self.files_list_widget = QWidget()
        self.files_list_layout = QGridLayout(self.files_list_widget)
        self.files_list_layout.setContentsMargins(0, 0, 0, 0)
        self.files_list_layout.setSpacing(8)
        
        # اضافه کردن اسکرول برای لیست فایل‌ها
        self.files_scroll_area = QScrollArea()
        self.files_scroll_area.setWidgetResizable(True)
        self.files_scroll_area.setWidget(self.files_list_widget)
        self.files_scroll_area.setFixedHeight(140)  # ارتفاع مناسب برای نمایش چند ردیف
        self.files_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: #f8f9fa;
            }
        """)
        process_layout.addWidget(self.files_scroll_area)
        
        # دکمه پردازش
        self.process_btn = QPushButton("🚀 شروع پردازش")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #218838);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
                margin: 10px 0;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #218838, stop:1 #1e7e34);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e7e34, stop:1 #1c7430);
            }
            QPushButton:disabled {
                background: #6c757d;
                color: #adb5bd;
            }
        """)
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        
        # قرار دادن دکمه در وسط
        process_btn_layout = QHBoxLayout()
        process_btn_layout.addStretch()
        process_btn_layout.addWidget(self.process_btn)
        process_btn_layout.addStretch()
        process_layout.addLayout(process_btn_layout)
        
        # نوار پیشرفت
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                color: #495057;
                background-color: #f8f9fa;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #106ebe);
                border-radius: 6px;
                margin: 2px;
            }
        """)
        process_layout.addWidget(self.progress_bar)
        
        layout.addWidget(process_group)
        
        # جدول نتایج
        results_group = QGroupBox("📋 نتایج استخراج اظهارنامه")
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ffc107;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fffbf0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #856404;
                font-size: 14px;
            }
        """)
        results_layout = QVBoxLayout(results_group)
        results_layout.setSpacing(10)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(len(self.export_columns))
        self.results_table.setHorizontalHeaderLabels(self.export_columns)
        # تنظیم اندازه ستون‌ها برای دو ستون
        column_widths = [400, 500]  # شماره اظهارنامه، ارز و مبلغ کل فاکتور
        for i, width in enumerate(column_widths):
            self.results_table.setColumnWidth(i, width)
        self.results_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e9ecef;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 8px;
                font-weight: bold;
                color: #495057;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        results_layout.addWidget(self.results_table)
        
        # دکمه‌های خروجی
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        
        self.export_excel_btn = QPushButton("📊 خروجی Excel")
        self.export_excel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #17a2b8, stop:1 #138496);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #138496, stop:1 #117a8b);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #117a8b, stop:1 #10707f);
            }
            QPushButton:disabled {
                background: #6c757d;
                color: #adb5bd;
            }
        """)
        self.export_excel_btn.clicked.connect(self.export_excel)
        self.export_excel_btn.setEnabled(False)
        
        self.clear_results_btn = QPushButton("🗑️ پاک کردن نتایج")
        self.clear_results_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c757d, stop:1 #5a6268);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6268, stop:1 #545b62);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #545b62, stop:1 #4e555b);
            }
        """)
        self.clear_results_btn.clicked.connect(self.clear_results)
        
        output_layout.addWidget(self.export_excel_btn)
        output_layout.addWidget(self.clear_results_btn)
        output_layout.addStretch()
        results_layout.addLayout(output_layout)
        
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(main_tab, "🏠 صفحه اصلی")
        
        # متغیرهای کلاس
        self.selected_files = []
        self.results_data = []
    
    def create_settings_tab(self):
        """ایجاد tab تنظیمات"""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        layout.setSpacing(15)  # کاهش فاصله بین المان‌ها
        
        # تنظیمات API
        api_group = QGroupBox("🔑 تنظیمات API")
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #6f42c1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f5ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #6f42c1;
                font-size: 14px;
            }
        """)
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(15)
        
        # فیلد کلید API
        api_row = QHBoxLayout()
        api_row.setSpacing(15)
        api_label = QLabel("کلید API:")
        api_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        api_label.setMinimumWidth(120)
        api_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #495057;
                font-size: 13px;
                padding: 8px 0;
            }
        """)
        api_row.addWidget(api_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("کلید API ChatGPT خود را وارد کنید")
        self.api_key_input.setMaximumWidth(400)
        self.api_key_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 10px 15px;
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #6f42c1;
                background-color: white;
                box-shadow: 0 0 5px rgba(111, 66, 193, 0.3);
            }
        """)
        api_row.addWidget(self.api_key_input)
        api_row.addStretch()
        api_layout.addLayout(api_row)
        
        # فیلد مدل
        model_row = QHBoxLayout()
        model_row.setSpacing(15)
        model_label = QLabel("مدل:")
        model_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        model_label.setMinimumWidth(120)
        model_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #495057;
                font-size: 13px;
                padding: 8px 0;
            }
        """)
        model_row.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(['gpt-3.5-turbo', 'gpt-4'])
        self.model_combo.setMaximumWidth(200)
        self.model_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 15px;
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
                color: #495057;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #6f42c1;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #6c757d;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #6f42c1;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #6f42c1;
                selection-color: white;
            }
        """)
        model_row.addWidget(self.model_combo)
        model_row.addStretch()
        api_layout.addLayout(model_row)
        
        # دکمه ذخیره تنظیمات در وسط
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # فاصله از چپ
        self.save_settings_btn = QPushButton("💾 ذخیره تنظیمات")
        self.save_settings_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6f42c1, stop:1 #5a32a3);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-width: 180px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a32a3, stop:1 #4a2b8a);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a2b8a, stop:1 #3d2371);
            }
        """)
        self.save_settings_btn.clicked.connect(self.save_settings)
        self.save_settings_btn.setMaximumWidth(200)  # محدود کردن عرض
        button_layout.addWidget(self.save_settings_btn)
        button_layout.addStretch()  # فاصله از راست
        
        api_layout.addLayout(button_layout)
        
        layout.addWidget(api_group)
        
        # راهنما
        help_group = QGroupBox("❓ راهنما")
        help_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #fd7e14;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fff8f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #fd7e14;
                font-size: 14px;
            }
        """)
        help_text = QTextEdit()
        help_text.setHtml("""
        <div style="font-family: 'Segoe UI', Arial; font-size: 12px; line-height: 1.6;">
            <h3 style="color: #fd7e14; margin-bottom: 10px;">نحوه دریافت کلید API:</h3>
            <ol style="color: #495057; margin-bottom: 15px;">
                <li>به سایت <a href="https://platform.openai.com/" style="color: #6f42c1; text-decoration: none;">OpenAI</a> بروید</li>
                <li>حساب کاربری ایجاد کنید</li>
                <li>از بخش API Keys، یک کلید جدید ایجاد کنید</li>
                <li>کلید را کپی کرده و در فیلد بالا وارد کنید</li>
            </ol>
            
            <h3 style="color: #fd7e14; margin-bottom: 10px;">اطلاعات استخراج شده:</h3>
            <ul style="color: #495057; margin-bottom: 15px;">
                <li><strong>شماره اظهارنامه:</strong> شماره زیر بارکد</li>
                <li><strong>ارز و مبلغ کل فاکتور:</strong> مبلغ کل فاکتور</li>
            </ul>
            
            <h3 style="color: #fd7e14; margin-bottom: 10px;">نکات مهم:</h3>
            <ul style="color: #495057;">
                <li>کلید API شما به صورت امن ذخیره می‌شود</li>
                <li>استفاده از API مستلزم پرداخت هزینه است</li>
                <li>مدل GPT-4 گران‌تر اما دقیق‌تر است</li>
                <li>تعداد توکن‌ها بهینه شده برای کاهش هزینه</li>
            </ul>
        </div>
        """)
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(300)
        help_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 15px;
                background-color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
            }
        """)
        help_group_layout = QVBoxLayout(help_group)
        help_group_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        layout.addStretch()
        
        self.tab_widget.addTab(settings_tab, "⚙️ تنظیمات")
    
    def create_stats_tab(self):
        """ایجاد tab آمار"""
        stats_tab = QWidget()
        layout = QVBoxLayout(stats_tab)
        layout.setSpacing(15)
        
        # آمار کلی
        overall_group = QGroupBox("📈 آمار کلی")
        overall_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #20c997;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f0fdfa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #20c997;
                font-size: 14px;
            }
        """)
        overall_layout = QGridLayout(overall_group)
        overall_layout.setSpacing(15)
        overall_layout.setHorizontalSpacing(20)
        
        # استایل برای عنوان‌ها
        title_style = """
            QLabel {
                font-weight: bold;
                color: #495057;
                font-size: 13px;
                padding: 8px 0;
            }
        """
        
        # استایل برای مقادیر
        value_style = """
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f5e8, stop:1 #d4edda);
                padding: 10px 15px;
                border-radius: 6px;
                border: 2px solid #20c997;
                font-weight: bold;
                color: #155724;
                min-width: 120px;
                text-align: center;
            }
        """
        
        self.stats_total_files = QLabel("0")
        self.stats_total_tokens = QLabel("0")
        self.stats_total_cost = QLabel("$0.00")
        self.stats_avg_tokens = QLabel("0")
        
        # اعمال استایل
        for label in [self.stats_total_files, self.stats_total_tokens, 
                     self.stats_total_cost, self.stats_avg_tokens]:
            label.setStyleSheet(value_style)
        
        # اضافه کردن به layout
        total_files_label = QLabel("کل فایل‌های پردازش شده:")
        total_files_label.setStyleSheet(title_style)
        overall_layout.addWidget(total_files_label, 0, 0)
        overall_layout.addWidget(self.stats_total_files, 0, 1)
        
        total_tokens_label = QLabel("کل توکن‌های مصرفی:")
        total_tokens_label.setStyleSheet(title_style)
        overall_layout.addWidget(total_tokens_label, 1, 0)
        overall_layout.addWidget(self.stats_total_tokens, 1, 1)
        
        total_cost_label = QLabel("کل هزینه:")
        total_cost_label.setStyleSheet(title_style)
        overall_layout.addWidget(total_cost_label, 2, 0)
        overall_layout.addWidget(self.stats_total_cost, 2, 1)
        
        avg_tokens_label = QLabel("میانگین توکن‌ها:")
        avg_tokens_label.setStyleSheet(title_style)
        overall_layout.addWidget(avg_tokens_label, 3, 0)
        overall_layout.addWidget(self.stats_avg_tokens, 3, 1)
        
        layout.addWidget(overall_group)
        
        # آمار روزانه
        daily_group = QGroupBox("📅 آمار روزانه")
        daily_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e83e8c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fdf2f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #e83e8c;
                font-size: 14px;
            }
        """)
        daily_layout = QVBoxLayout(daily_group)
        daily_layout.setSpacing(10)
        
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(3)
        self.daily_table.setHorizontalHeaderLabels([
            'تعداد فایل‌ها', 'مجموع توکن‌های مصرف شده', 'حجم کل (KB)'
        ])
        self.daily_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: #fff;
                gridline-color: #f8bbd0;
                selection-background-color: #e83e8c;
                selection-color: white;
                font-size: 13px;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fce4ec, stop:1 #f8bbd0);
                border: 1px solid #fbcfe8;
                padding: 12px;
                font-weight: bold;
                color: #ad1457;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background-color: #e83e8c;
                color: white;
            }
        """)
        self.daily_table.horizontalHeader().setStretchLastSection(True)
        self.daily_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daily_table.setAlternatingRowColors(True)
        self.daily_table.setShowGrid(True)
        daily_layout.addWidget(self.daily_table)
        
        layout.addWidget(daily_group)
        
        # دکمه‌های مدیریت آمار
        stats_buttons_layout = QHBoxLayout()
        stats_buttons_layout.setSpacing(15)
        
        self.refresh_stats_btn = QPushButton("🔄 به‌روزرسانی آمار")
        self.refresh_stats_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #20c997, stop:1 #1ea085);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-width: 160px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1ea085, stop:1 #1a8f78);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a8f78, stop:1 #167f6b);
            }
        """)
        self.refresh_stats_btn.clicked.connect(self.update_stats)
        
        self.reset_stats_btn = QPushButton("🗑️ پاک کردن آمار")
        self.reset_stats_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e83e8c, stop:1 #d63384);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                min-width: 140px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d63384, stop:1 #c2255c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c2255c, stop:1 #a91e47);
            }
        """)
        self.reset_stats_btn.clicked.connect(self.reset_stats)
        
        stats_buttons_layout.addWidget(self.refresh_stats_btn)
        stats_buttons_layout.addWidget(self.reset_stats_btn)
        stats_buttons_layout.addStretch()
        layout.addLayout(stats_buttons_layout)
        
        self.tab_widget.addTab(stats_tab, "📊 آمار و گزارش")
    
    def load_settings(self):
        """بارگذاری تنظیمات"""
        self.api_key_input.setText(self.settings_manager.get_api_key())
        self.model_combo.setCurrentText(self.settings_manager.get_model())
        self.update_stats()
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        self.settings_manager.set_api_key(self.api_key_input.text())
        self.settings_manager.set_model(self.model_combo.currentText())
        
        QMessageBox.information(self, "✅ موفق", "تنظیمات با موفقیت ذخیره شد!")
    
    def upload_files(self):
        """آپلود فایل‌های PDF"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "انتخاب فایل‌های PDF", "", "PDF Files (*.pdf)"
        )
        
        if files:
            self.selected_files.extend(files)
            self.update_files_display()
            self.process_btn.setEnabled(True)
    
    def clear_files(self):
        """پاک کردن لیست فایل‌ها"""
        self.selected_files.clear()
        self.update_files_display()
        self.process_btn.setEnabled(False)
    
    def update_files_display(self):
        """به‌روزرسانی نمایش فایل‌ها به صورت لیستی با دکمه حذف"""
        # پاک کردن آیتم‌های قبلی
        for i in reversed(range(self.files_list_layout.count())):
            item = self.files_list_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        if self.selected_files:
            for idx, file_path in enumerate(self.selected_files):
                row = idx // 4
                col = idx % 4
                file_widget = QWidget()
                file_layout = QHBoxLayout(file_widget)
                file_layout.setContentsMargins(0, 0, 0, 0)
                file_layout.setSpacing(4)
                remove_btn = QPushButton("❌")
                remove_btn.setFixedSize(32, 32)
                remove_btn.setStyleSheet("""
                    QPushButton {
                        background: #ffebee;
                        color: #c82333;
                        border: 1px solid #f5c6cb;
                        border-radius: 16px;
                        font-size: 20px;
                        font-weight: bold;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background: #f8d7da;
                        color: #a71d2a;
                    }
                """)
                remove_btn.setContentsMargins(0, 0, 0, 0)
                remove_btn.clicked.connect(lambda _, i=idx: self.remove_selected_file(i))
                file_label = QLabel(os.path.basename(file_path))
                file_label.setStyleSheet("""
                    QLabel {
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 6px;
                        padding: 6px 10px;
                        font-size: 12px;
                        min-width: 80px;
                    }
                """)
                file_layout.addWidget(remove_btn)
                file_layout.addWidget(file_label)
                file_widget.setLayout(file_layout)
                self.files_list_layout.addWidget(file_widget, row, col)
        self.process_btn.setEnabled(bool(self.selected_files))

    def remove_selected_file(self, index):
        """حذف یک فایل از لیست انتخاب شده"""
        if 0 <= index < len(self.selected_files):
            del self.selected_files[index]
            self.update_files_display()
    
    def start_processing(self):
        """شروع پردازش فایل‌ها"""
        if not self.selected_files:
            QMessageBox.warning(self, "⚠️ هشدار", "لطفاً ابتدا فایل‌های اظهارنامه انتخاب کنید!")
            return
        
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            QMessageBox.warning(self, "⚠️ هشدار", "لطفاً ابتدا کلید API را در تنظیمات وارد کنید!")
            return
        
        # شروع پردازش
        self.processor = PDFProcessor(
            self.selected_files,
            api_key,
            self.settings_manager.get_model()
        )
        
        self.processor.progress.connect(self.update_progress)
        self.processor.finished.connect(self.processing_finished)
        self.processor.error.connect(self.processing_error)
        
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.selected_files))
        self.progress_bar.setValue(0)
        
        self.processor.start()
    
    def update_progress(self, message):
        """به‌روزرسانی نوار پیشرفت"""
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.statusBar().showMessage(message)
    
    def processing_finished(self, results):
        """پایان پردازش"""
        self.results_data = results
        self.display_results(results)
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.export_excel_btn.setEnabled(True)
        QMessageBox.information(self, "✅ موفق", f"استخراج اطلاعات {len(results)} فایل با موفقیت انجام شد!")
        self.update_stats()
    
    def processing_error(self, error_message):
        """خطا در پردازش"""
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "❌ خطا", f"خطا در استخراج اطلاعات: {error_message}")
    
    def display_results(self, results):
        """نمایش نتایج در جدول"""
        if not results:
            return
        columns = self.export_columns
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        for row, data in enumerate(results):
            for col, col_name in enumerate(columns):
                value = data.get(col_name, "")
                self.results_table.setItem(row, col, QTableWidgetItem(str(value)))
        self.results_table.resizeColumnsToContents()
    
    def export_excel(self):
        """خروجی Excel"""
        if not self.results_data:
            QMessageBox.warning(self, "⚠️ هشدار", "هیچ اطلاعاتی برای خروجی وجود ندارد!")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره فایل Excel", 
            f"مبالغ_کل_فاکتور_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if file_path:
            try:
                df = pd.DataFrame(self.results_data)
                df = df[[col for col in self.export_columns if col in df.columns]]
                df.to_excel(file_path, index=False, engine='openpyxl')
                QMessageBox.information(self, "✅ موفق", f"فایل اطلاعات در مسیر زیر ذخیره شد:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "❌ خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def clear_results(self):
        """پاک کردن نتایج"""
        self.results_data.clear()
        self.results_table.setRowCount(0)
        self.export_excel_btn.setEnabled(False)
    
    def update_stats(self):
        """به‌روزرسانی آمار"""
        stats = self.settings_manager.usage_stats
        
        # آمار سریع
        self.total_files_label.setText(f"فایل‌های پردازش شده: {stats['files_processed']}")
        self.total_tokens_label.setText(f"کل توکن‌ها: {stats['total_tokens']:,}")
        self.total_cost_label.setText(f"کل هزینه: ${stats['total_cost']:.4f}")
        
        # توکن‌های امروز
        today = datetime.now().strftime('%Y-%m-%d')
        today_tokens = stats['daily_usage'].get(today, {}).get('tokens', 0)
        self.today_tokens_label.setText(f"توکن‌های امروز: {today_tokens:,}")
        
        # آمار کلی
        self.stats_total_files.setText(str(stats['files_processed']))
        self.stats_total_tokens.setText(f"{stats['total_tokens']:,}")
        self.stats_total_cost.setText(f"${stats['total_cost']:.4f}")
        
        avg_tokens = stats['total_tokens'] // stats['files_processed'] if stats['files_processed'] > 0 else 0
        self.stats_avg_tokens.setText(f"{avg_tokens:,}")
        
        # جدول روزانه
        self.update_daily_table()
    
    def update_daily_table(self):
        """به‌روزرسانی جدول روزانه"""
        daily_stats = self.settings_manager.usage_stats['daily_usage']
        dates = sorted(daily_stats.keys(), reverse=True)
        
        self.daily_table.setRowCount(len(dates))
        
        for row, date in enumerate(dates):
            stats = daily_stats[date]
            tokens = stats['tokens']
            files = stats.get('files', 1) if stats.get('files', 1) > 0 else 1
            total_size = stats.get('total_size', 0)  # حجم کل در KB
            self.daily_table.setItem(row, 0, QTableWidgetItem(str(files)))
            self.daily_table.setItem(row, 1, QTableWidgetItem(f"{tokens:,}"))
            self.daily_table.setItem(row, 2, QTableWidgetItem(f"{total_size:,.2f}"))
        self.daily_table.resizeColumnsToContents()
    
    def reset_stats(self):
        """پاک کردن آمار"""
        reply = QMessageBox.question(
            self, "⚠️ تأیید", 
            "آیا مطمئن هستید که می‌خواهید تمام آمار را پاک کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.usage_stats = {
                'total_tokens': 0,
                'total_cost': 0.0,
                'daily_usage': {},
                'files_processed': 0
            }
            self.settings_manager.save_usage_stats()
            self.update_stats()
            QMessageBox.information(self, "✅ موفق", "آمار با موفقیت پاک شد!")

    def set_file_type(self, file_type):
        """تنظیم نوع فایل‌های آپلودی (واردات یا صادرات)"""
        self.selected_file_type = file_type
        # حالا که ساختار داده‌ها یکسان است، نیازی به تغییر جدول نیست
        # جدول به صورت خودکار بر اساس داده‌های دریافتی تنظیم می‌شود

def main():
    app = QApplication(sys.argv)
    
    # تنظیم جهت راست به چپ
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()