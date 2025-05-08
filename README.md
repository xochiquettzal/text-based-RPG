# Metin Tabanlı RPG Oyunu (AI Destekli)

Bu proje, Python (FastAPI) backend'i ve basit bir HTML/CSS/JS frontend'i kullanarak tarayıcıda oynanabilen, AI destekli metin tabanlı bir RPG oyunudur. Oyuncular farklı dünyalar seçebilir, ırk/fraksiyon seçimi yapabilir ve hikayeyi metin komutları veya sunulan seçeneklerle ilerletebilirler. AI (OpenRouter üzerinden), dinamik anlatım ve olaylar oluşturmak için kullanılır.

## Özellikler

*   Birden fazla dünya (Karanlık Fantezi, Hayvan Krallığı)
*   Dünyaya özel ırk/fraksiyon seçimi (lore ve başlangıç senaryoları ile)
*   Görsel seçim ekranları (Dünya ve Irk/Fraksiyon)
*   Sohbet benzeri oyun arayüzü
*   Karakter bilgi kartı (Stat gösterimi)
*   OpenRouter API entegrasyonu (birden fazla model fallback mekanizması ile)
*   Oyuncunun özel komut girebilmesi (başarı/başarısızlık olasılığı ile)
*   Basitleştirilmiş başlatma script'i (`start.py`)

## Kurulum

1.  **Python:** Proje için Python 3.8+ önerilir. Sisteminizde Python ve pip'in kurulu olduğundan emin olun.
2.  **Depoyu Klonlama (Opsiyonel):** Eğer projeyi bir depodan klonladıysanız, proje dizinine gidin.
3.  **API Anahtarı:**
    *   `backend/` klasörü içinde `.env` adında bir dosya oluşturun (veya var olanı düzenleyin).
    *   Dosyanın içine aşağıdaki satırı ekleyin ve `YOUR_KEY_HERE` kısmını kendi OpenRouter API anahtarınızla değiştirin:
        ```
        OPENROUTER_API_KEY="YOUR_KEY_HERE"
        ```
4.  **Bağımlılıkları Yükleme:** Projenin ana dizininde bir terminal açın ve aşağıdaki komutu çalıştırın:
    ```bash
    pip install -r backend/requirements.txt
    ```
    *Not: `start.py` script'i de bu komutu otomatik olarak çalıştırmayı dener.*

5.  **Görseller (Önemli):**
    *   `frontend/` klasörü içinde `images` adında bir klasör oluşturun.
    *   Aşağıdaki görselleri (veya kendi seçtiğiniz uygun görselleri) bu klasöre yerleştirin:
        *   `dark_fantasy.jpg` (Dünya seçimi için)
        *   `animal_kingdom.jpg` (Dünya seçimi için)
        *   `vargar.jpg` (Hayvan Krallığı - Irk seçimi)
        *   `vulpex.jpg` (Hayvan Krallığı - Irk seçimi)
        *   `noctis.jpg` (Hayvan Krallığı - Irk seçimi)
        *   `leporim.jpg` (Hayvan Krallığı - Irk seçimi)
        *   `ashen_legion.jpg` (Karanlık Fantezi - Fraksiyon seçimi)
        *   `shadow_syndicate.jpg` (Karanlık Fantezi - Fraksiyon seçimi)
        *   `primordial_cult.jpg` (Karanlık Fantezi - Fraksiyon seçimi)

## Çalıştırma

1.  Projenin ana dizininde bir terminal açın.
2.  Aşağıdaki komutu çalıştırın:
    ```bash
    python start.py
    ```
3.  Bu script backend sunucusunu başlatacak ve varsayılan web tarayıcınızda oyun arayüzünü açacaktır.
4.  Oyunu durdurmak için script'i çalıştırdığınız terminali kapatın (Ctrl+C).

## Nasıl Oynanır

1.  Uygulama açıldığında bir dünya seçin.
2.  Seçtiğiniz dünyaya göre ırk veya fraksiyon seçimi yapın (kartın üzerine gelerek detayları okuyabilir, tıklayarak seçebilirsiniz).
3.  Modal penceresinde seçiminizi onaylayın.
4.  Oyun sohbet ekranında başlar. Sol tarafta karakter bilgilerinizi görebilirsiniz.
5.  AI'nın sunduğu seçenek butonlarına tıklayarak veya alttaki metin giriş alanına kendi eyleminizi yazıp "Gönder" butonuna basarak (ya da Enter'a basarak) oyunda ilerleyin.
