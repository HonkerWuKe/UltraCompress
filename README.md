# 极限压缩工具 / Ultimate Compression Tool / Инструмент Сжатия / अल्टीमेट कंप्रेशन टूल

[简体中文](#简体中文) | [English](#english) | [Русский](#русский) | [हिंदी](#हिंदी)

## 简体中文

### 简介
极限压缩工具是一个基于Python开发的图形界面压缩软件，使用7z算法进行高效压缩。它提供了简单直观的界面，支持文件和文件夹的压缩，并且允许用户自定义压缩参数。

### 主要特性
- 图形化界面，操作简单直观
- 支持文件和文件夹压缩
- 自定义字典大小和线程数
- 实时压缩进度显示
- 详细的压缩信息统计（压缩比、耗时等）
- 自动建议输出路径

### 使用说明
1. 选择输入文件/文件夹
2. 选择输出路径（默认与输入文件同目录）
3. 设置压缩参数：
   - 字典大小：建议256-4096MB，不超过物理内存的1/3
   - 线程数：建议设置为CPU核心数
4. 点击"开始压缩"即可

## English

### Introduction
Ultimate Compression Tool is a GUI-based compression software developed in Python using the 7z algorithm. It provides a simple and intuitive interface for compressing files and folders with customizable compression parameters.

### Key Features
- User-friendly graphical interface
- Support for both file and folder compression
- Customizable dictionary size and thread count
- Real-time compression progress
- Detailed compression statistics (compression ratio, time taken, etc.)
- Automatic output path suggestion

### Usage
1. Select input file/folder
2. Choose output path (defaults to same directory as input)
3. Set compression parameters:
   - Dictionary size: recommended 256-4096MB, not exceeding 1/3 of physical memory
   - Thread count: recommended to match CPU core count
4. Click "Start Compression"

## Русский

### Введение
Инструмент Сжатия - это программное обеспечение для сжатия файлов с графическим интерфейсом, разработанное на Python с использованием алгоритма 7z. Программа предоставляет простой и интуитивно понятный интерфейс для сжатия файлов и папок с настраиваемыми параметрами.

### Основные функции
- Удобный графический интерфейс
- Поддержка сжатия файлов и папок
- Настраиваемый размер словаря и количество потоков
- Отображение прогресса сжатия в реальном времени
- Подробная статистика сжатия (коэффициент сжатия, затраченное время и т.д.)
- Автоматическое предложение пути вывода

### Использование
1. Выберите входной файл/папку
2. Выберите путь вывода (по умолчанию - та же директория)
3. Установите параметры сжатия:
   - Размер словаря: рекомендуется 256-4096МБ, не более 1/3 физической памяти
   - Количество потоков: рекомендуется соответствие количеству ядер процессора
4. Нажмите "Начать сжатие"

## हिंदी

### परिचय
अल्टीमेट कंप्रेशन टूल एक Python में विकसित GUI-आधारित कंप्रेशन सॉफ्टवेयर है जो 7z एल्गोरिथम का उपयोग करता है। यह फ़ाइलों और फ़ोल्डरों को कस्टमाइज़ करने योग्य कंप्रेशन पैरामीटर के साथ कंप्रेस करने के लिए एक सरल और सहज इंटरफ़ेस प्रदान करता है।

### मुख्य विशेषताएं
- उपयोगकर्ता-अनुकूल ग्राफिकल इंटरफेस
- फ़ाइल और फ़ोल्डर कंप्रेशन के लिए समर्थन
- कस्टमाइज़ करने योग्य डिक्शनरी साइज और थ्रेड काउंट
- रीयल-टाइम कंप्रेशन प्रगति
- विस्तृत कंप्रेशन आंकड़े (कंप्रेशन अनुपात, लगा समय, आदि)
- स्वचालित आउटपुट पाथ सुझाव

### उपयोग
1. इनपुट फ़ाइल/फ़ोल्डर चुनें
2. आउटपुट पाथ चुनें (डिफ़ॉल्ट रूप से इनपुट के समान डायरेक्टरी)
3. कंप्रेशन पैरामीटर सेट करें:
   - डिक्शनरी साइज: 256-4096MB की सिफारिश, भौतिक मेमोरी के 1/3 से अधिक नहीं
   - थ्रेड काउंट: CPU कोर काउंट के अनुरूप सिफारिश
4. "कंप्रेशन शुरू करें" पर क्लिक करें

---

## 技术要求 / Technical Requirements / Технические требования / तकनीकी आवश्यकताएं

### 依赖项 / Dependencies / Зависимости / निर्भरताएं
- Python 3.6+
- py7zr
- tkinter

### 安装依赖 / Install Dependencies / Установка зависимостей / निर्भरताएं इंस्टॉल करें

```bash
    pip install py7zr
```
