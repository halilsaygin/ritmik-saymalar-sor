# Ritmik Saymalar Sor

Bu uygulama, öğrencilerin ritmik sayma becerilerini geliştirmek için tasarlanmış bir PySide6 tabanlı masaüstü uygulamasıdır.

## Özellikler

- **Modern Tasarım:** Şık ve kullanıcı dostu arayüz.
- **Özelleştirilebilir Oyun Modları:**
  - **Zaman Sınırlı:** Belirli bir süre içinde ne kadar çok sayma yapılabileceğini ölçer.
  - **Hata Sınırlı:** Belirli bir hata sayısına ulaşana kadar devam eder.
- **Esnek Sayma Seçenekleri:** Farklı ritmik sayma aralıkları (2'şer, 3'er, 4'er vb. - geliştirme aşamasında).
- **QSS Desteği:** Özelleştirilmiş temalar ve grafiksel öğeler.

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.8+
- PySide6

### Adımlar

1.  **Sanal Ortamı Oluşturun ve Etkinleştirin:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate   # Windows
    ```

2.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    python main.py
    ```

## Proje Yapısı

- `main.py`: Uygulamanın giriş noktası.
- `src/`: Kaynak kodlar (Mantık ve UI bağlamaları).
- `ui/`: Qt Designer (.ui) dosyaları.
- `resources/`: Stil dosyaları (QSS) ve ikonlar.
- `src/ui_generated/`: Otomatik oluşturulan Python UI sınıfları.

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
