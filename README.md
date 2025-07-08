# 📄 PDF OCR - استخراج اطلاعات از فایل‌های PDF اظهارنامه

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5%2F4-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/seyedmahdivakhshoori/pdf-ocr)
![GitHub issues](https://img.shields.io/github/issues/seyedmahdivakhshoori/pdf-ocr)
![GitHub pull requests](https://img.shields.io/github/issues-pr/seyedmahdivakhshoori/pdf-ocr)
![GitHub contributors](https://img.shields.io/github/contributors/seyedmahdivakhshoori/pdf-ocr)

**نرم‌افزار هوشمند استخراج اطلاعات از فایل‌های PDF اظهارنامه با استفاده از هوش مصنوعی**

[🚀 دانلود](#نصب-و-راه‌اندازی) • [📖 راهنما](#راهنمای-استفاده) • [⚙️ تنظیمات](#تنظیمات) • [📊 آمار](#آمار-و-گزارش)

</div>

---

## 🎯 ویژگی‌های کلیدی

- ✅ **استخراج هوشمند اطلاعات** از فایل‌های PDF اظهارنامه
- ✅ **رابط کاربری گرافیکی** زیبا و کاربرپسند با PyQt6
- ✅ **پشتیبانی از ChatGPT API** (GPT-3.5 و GPT-4)
- ✅ **تبدیل تاریخ میلادی به شمسی** خودکار
- ✅ **پردازش دسته‌ای** فایل‌ها برای کاهش هزینه
- ✅ **خروجی Excel** با فرمت استاندارد
- ✅ **آمار و گزارش** دقیق از مصرف API
- ✅ **بهینه‌سازی هزینه** با کاهش مصرف توکن
- ✅ **فونت‌های فارسی محلی** (Segoe UI) برای سازگاری کامل

## 📋 اطلاعات استخراج شده

| فیلد | توضیحات |
|------|---------|
| **ارز و مبلغ کل فاکتور** | مبلغ کل فاکتور با ارز مربوطه |

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8 یا بالاتر
- کلید API OpenAI

### مراحل نصب

1. **کلون کردن مخزن**
```bash
git clone https://github.com/seyedmahdivakhshoori/pdf-ocr.git
cd pdf-ocr
```

2. **ایجاد محیط مجازی**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **نصب وابستگی‌ها**
```bash
pip install -r requirements.txt
```

4. **دریافت کلید API**
- به [OpenAI Platform](https://platform.openai.com/) بروید
- حساب کاربری ایجاد کنید
- از بخش API Keys، یک کلید جدید ایجاد کنید

5. **اجرای برنامه**
```bash
python pdf_ocr.py
```

## 📖 راهنمای استفاده

### 1. تنظیمات اولیه
- برنامه را اجرا کنید
- به تب **تنظیمات** بروید
- کلید API خود را وارد کنید
- مدل مورد نظر را انتخاب کنید (GPT-3.5 یا GPT-4)
- تنظیمات را ذخیره کنید

### 2. آپلود فایل‌ها
- به تب **صفحه اصلی** برگردید
- نوع فایل‌ها را انتخاب کنید (واردات/صادرات)
- روی **انتخاب فایل‌های PDF** کلیک کنید
- فایل‌های اظهارنامه را انتخاب کنید

### 3. پردازش
- روی **شروع پردازش** کلیک کنید
- منتظر بمانید تا پردازش کامل شود
- نتایج در جدول نمایش داده می‌شود

### 4. خروجی
- روی **خروجی Excel** کلیک کنید
- مسیر ذخیره فایل را انتخاب کنید
- فایل Excel با اطلاعات استخراج شده ذخیره می‌شود

## ⚙️ تنظیمات

### مدل‌های پشتیبانی شده
- **GPT-3.5-turbo**: سریع و اقتصادی
- **GPT-4**: دقیق‌تر اما گران‌تر

### بهینه‌سازی هزینه
- پردازش دسته‌ای فایل‌ها
- کاهش تعداد توکن‌های مصرفی
- فیلتر کردن متن‌های غیرضروری

## 📊 آمار و گزارش

برنامه آمار دقیقی از موارد زیر ارائه می‌دهد:

- **کل فایل‌های پردازش شده**
- **تعداد توکن‌های مصرفی**
- **هزینه کل API**
- **آمار روزانه**
- **میانگین توکن‌ها**

## 🛠️ ساختار پروژه

```
pdf-ocr/
├── pdf_ocr.py              # فایل اصلی برنامه
├── create_sample_pdf.py    # ایجاد فایل PDF نمونه
├── coords_config.json      # تنظیمات مختصات
├── requirements.txt        # وابستگی‌های Python
├── README.md              # راهنمای پروژه
├── .gitignore             # فایل‌های نادیده گرفته شده
├── fonts/                 # فونت‌های فارسی
│   ├── segoeui.ttf        # Segoe UI Regular
│   ├── segoeuib.ttf       # Segoe UI Bold
│   ├── segoeuii.ttf       # Segoe UI Italic
│   └── segoeuiz.ttf       # Segoe UI Bold Italic
└── your_first_sample.pdf  # فایل PDF نمونه
```

## 🔧 کلاس‌های اصلی

### PersianDateConverter
تبدیل تاریخ میلادی به شمسی با دقت بالا

### SettingsManager
مدیریت تنظیمات برنامه و آمار استفاده

### PDFProcessor
پردازش فایل‌های PDF در thread جداگانه

### MainWindow
رابط کاربری اصلی برنامه

## 📝 نمونه کد

### ایجاد فایل PDF نمونه
```python
python create_sample_pdf.py
```

### اجرای برنامه اصلی
```python
python pdf_ocr.py
```

## 🐛 عیب‌یابی

### مشکلات رایج

1. **خطای کلید API**
   - کلید API را بررسی کنید
   - اطمینان حاصل کنید که اعتبار کافی دارید

2. **خطای نصب PyQt6**
   ```bash
   pip install PyQt6 --upgrade
   ```

3. **مشکل فونت فارسی**
   - فونت Segoe UI نصب باشد
   - سیستم عامل از RTL پشتیبانی کند

## 🤝 مشارکت

برای مشارکت در پروژه:

1. Fork کنید
2. Branch جدید ایجاد کنید (`git checkout -b feature/AmazingFeature`)
3. تغییرات را commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request ایجاد کنید

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای اطلاعات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

## 👨‍💻 توسعه‌دهنده

**Seyed Mahdi Vakhshoori** - [seyedmahdivakhshoori@gmail.com](mailto:seyedmahdivakhshoori@gmail.com)

- GitHub: [@seyedmahdivakhshoori](https://github.com/seyedmahdivakhshoori)
- Instagram: [@mahdi_vakhshoori](https://www.instagram.com/mahdi_vakhshoori/)

## 🙏 تشکر

- [OpenAI](https://openai.com/) برای ارائه API
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) برای رابط کاربری
- [PyPDF2](https://pypdf2.readthedocs.io/) برای پردازش PDF

## 📞 پشتیبانی

اگر سوال یا مشکلی دارید:

- [Issue](https://github.com/seyedmahdivakhshoori/pdf-ocr/issues)
- ایمیل: seyedmahdivakhshoori@gmail.com

---

<div align="center">

⭐ اگر این پروژه برایتان مفید بود، لطفاً ستاره بدهید!

</div> # pdf-ocr
