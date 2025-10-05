[README.md](https://github.com/user-attachments/files/22709332/README.md)
# UART Monitoring Interface

Version: 3.0

## PROJE TANIMI

UART Monitoring Interface, seri port üzerinden FPGA tabanlı donanım kartlarından gelen verileri gerçek zamanlı olarak izlemek, analiz etmek ve kontrol etmek için geliştirilmiş profesyonel bir PyQt5 GUI uygulamasıdır.

Uygulama, özellikle güç yönetimi, sensör okuma ve donanım durumu izleme senaryoları için tasarlanmıştır.

## ANA ÖZELLIKLER

### Veri İzleme ve Görselleştirme
- 128 byte veriyi eş zamanlı görüntüleme
- 3 sütunlu tablo düzeni (her sütunda 43 satır)
- Gerçek zamanlı renk kodlu durum gösterimi
- 2-byte ölçüm çiftleri için özel işleme (Voltage, Current, Power)
- Min/Max aralık kontrolü ve validasyonu
- Anlam (meaning) sütununda dinamik çözümleme

### Durum Göstergeleri
- **SATA0**: Kapalı (Kırmızı-DISABLED) / Açık (Yeşil-ENABLED)
- **SATA1**: Kapalı (Kırmızı-DISABLED) / Açık (Yeşil-ENABLED)
- **GPU STATUS**: Kapalı (Beyaz-DISABLED) / Açık (Yeşil-ENABLED)
- **PMON STATUS**: Hata (Kırmızı-POWER FAIL) / Normal (Yeşil-POWER OK)

### DISC Sistemi
- **DISC_IN_STATUS**: 4 kanallı giriş durumu izleme (OPEN/GND veya OPEN/28V)
- **DISC TYPE Seçimi**: OPEN/GND veya OPEN/28V mod seçimi
- **DISC OUT CONTROL**: 4 kanallı çıkış kontrolü (ENABLED/DISABLED)

### Kontrol Özellikleri
- **SATA Zeroize Control**: 
  - SATA1 tek başına zeroize
  - SATA0 ve SATA1 birlikte zeroize
- **LED2 Control**: RGB LED kontrolü (Kırmızı, Yeşil, Mavi)

### Kullanıcı Arayüzü
- Modern dark theme tasarım
- Scroll edilebilir kontrol paneli
- Optimize edilmiş buton ve yazı boyutları
- Yüksek okunabilirlik için kontrast renkler
- Responsive düzen (minimum 1200x700, önerilen 1800x950)

## KURULUM

### Gereksinimler
```
Python 3.7+
PyQt5
pyserial
```

### Kurulum Adımları
```bash
pip install PyQt5 pyserial
python UART_GUI_V3.py
```

## KULLANIM

### Bağlantı Kurma
1. COM Port seçin (otomatik algılama)
2. Baud Rate ayarlayın (varsayılan: 115200)
3. "CONNECT" butonuna tıklayın
4. Bağlantı durumu yeşil olarak görünecektir

### Veri İzleme
- Tablo otomatik olarak güncellenir (100ms interval)
- Yeşil hücreler: Geçerli değer aralığında
- Kırmızı hücreler: Aralık dışı veya hata
- Gri hücreler: N/A (tanımsız veya 2-byte çiftinin ikinci byte'ı)

### Kontrol Komutları Gönderme
1. Önce UART bağlantısı kurulmalıdır
2. İlgili kontrol butonuna tıklayın
3. Onay dialoglarını kabul edin
4. Komut gönderilir ve cihaz durumu güncellenir

## PDF'YE GÖRE YAPILAN GÜNCELLEMELER

### 1. Tablo Başlıkları İngilizce Yapıldı
**Öncesi**: #, Sinyal, Min, Değer, Max, Meaning  
**Sonrası**: #, SIGNAL, MIN, VALUE, MAX, MEANING

### 2. 2-Byte Ölçüm Çiftleri İşleme
**İmplementasyon**: 
- Voltage, Current, Power gibi ölçümler 2 byte ile temsil edilir
- İlk byte: Versiyon kontrolü yapılır, normal görünüm
- İkinci byte: Min/Max/Meaning sütunları GRİ boyanır ve "N/A" yazılır
- Sadece ilk byte üzerinden aralık kontrolü yapılır

**Etkilenen Sinyaller**:
```
LTC4281_PMON_VOLTAGE (26-27)
LTC4281_PMON_CURRENT (28-29)
LTC4281_PMON_POWER (30-31)
LTC4281_SATA0_VOLTAGE (33-34)
LTC4281_SATA0_CURRENT (35-36)
... ve benzeri tüm voltage/current/power çiftleri
```

### 3. N/A Gösterimi
**Öncesi**: "XX" yazısı (hata gibi algılanıyordu)  
**Sonrası**: 
- "N/A" metni
- Gri arka plan rengi (#424242)
- Daha kolay ayırt edilebilir

### 4. Durum Göstergeleri Yeniden Tasarlandı
**Öncesi**: Tümü basit tuşlar  
**Sonrası**: Farklılaştırılmış durum göstergeleri

#### SATA0 ve SATA1:
- Kapalı: Kırmızı (#c62828) + "DISABLED"
- Açık: Yeşil (#2e7d32) + "ENABLED"

#### GPU STATUS:
- Kapalı: Beyaz (#ffffff) + "DISABLED"
- Açık: Yeşil (#2e7d32) + "ENABLED"

#### PMON STATUS:
- Hatasız: Yeşil (#2e7d32) + "POWER OK"
- Hata: Kırmızı (#c62828) + "POWER FAIL"

### 5. DISC OUT CONTROL (Eski: TX CONTROL)
**Değişiklik**: 
- İsim: "TX KONTROL" → "DISC OUT CONTROL"
- 4 adet DISC OUT kanalı kontrolü
- Kapalı: Gri (#666666) + "DISABLED"
- Açık: Yeşil (#4caf50) + "ENABLED"

### 6. Tüm Yazılar Büyük Harf ve İngilizce
**Örnekler**:
- "Bağlantı Ayarları" → "CONNECTION SETTINGS"
- "Durum Göstergeleri" → "STATUS INDICATORS"
- "Kontrol Paneli" → "CONTROL PANEL"
- "Bağlan" → "CONNECT"
- "Bağlantıyı Kes" → "DISCONNECT"

### 7. DISC_IN_STATUS Paneli Eklendi
**Yeni Özellik**:
- 4 kanallı DISC_IN durumu gösterimi
- Her kanal için "OPEN" veya "GND"/"28V" gösterimi
- Renklendirme YOK (sadece metin)
- DISC_IN_VALUES register'ından (index 20) okunur

### 8. Renk Standardizasyonu
**Kırmızı (#c62828)**: 
- Hata durumları
- Aralık dışı değerler
- Fail durumları

**Yeşil (#2e7d32, #4caf50)**:
- OK durumları
- Enabled durumları
- Geçerli değerler

**Beyaz/Gri (#ffffff, #666666)**:
- Neutral disabled durumları
- N/A değerleri

### 9. SATA ZEROIZE CONTROL (Eski: SATA Kontrolleri)
**Değişiklik**:
- Grup adı: "SATA KONTROL" → "SATA ZEROIZE CONTROL"
- Buton 1: "SATA1 Etkinleştir" → "ONLY SATA1 ZEROIZE ACTIVATE"
- Buton 2: "SATAS Etkinleştir (SATA0 + SATA1)" → "SATA0 & SATA1 ZEROIZE ACTIVATE"
- Normal: Beyaz arka plan
- Basıldığında: Kırmızı efekt (pressed state)

### 10. LED2 CONTROL Güncellendi
**İmplementasyon**:
- Grup adı: "LED KONTROL" → "LED2 CONTROL"
- Her LED için ENABLED/DISABLED durumu gösterimi
- Disabled: Gri arka plan, renkli yazı
- Enabled: Yeşil arka plan, beyaz yazı

### 11. DISC TYPE Seçici Eklendi (Yeni)
**Özellik**:
- Radio button ile seçim
- İki mod: "OPEN/GND" ve "OPEN/28V"
- Varsayılan: "OPEN/GND"
- DISC_IN_STATUS gösterimini etkiler

### 12. Ekran Düzeni Optimizasyonu (Yeni)
**Sorun**: Butonlar ve yazılar birbirine giriyordu  
**Çözüm**:
- Sağ panel QScrollArea içine alındı
- Dikey scroll eklendi (yatay scroll kapalı)
- Tüm buton yükseklikleri küçültüldü (55px → 36-45px)
- Font boyutları optimize edildi (10px → 8-9px)
- Panel genişliği sabitlendi (300-320px)
- Spacing değerleri azaltıldı (8px → 4-6px)

### 13. Okunabilirlik İyileştirmeleri (Yeni)
**Panel Başlıkları**:
- Arka plan: Açık gri (#252526) → Koyu siyah (#1a1a1a)
- Başlık rengi: Gri → Beyaz
- Başlık arka planı: Mavi etiket (#0e639c) eklendi
- Kenarlık: 1px gri → 2px mavi kalın

**Popup Mesajları**:
- Mesaj metni: Beyaz (#ffffff)
- Font boyutu: 11px
- Minimum genişlik: 300px
- Daha büyük butonlar

## TEKNİK DETAYLAR

### UART Protokolü
- **Header**: 0x41, 0x56 (sabit)
- **Paket Uzunluğu**: 0x85 (133 byte)
- **Paket ID**: 0x02
- **Veri**: 128 byte
- **Checksum**: 1 byte (toplam 256'nın tamamlayıcısı)

### Veri Yapısı
```
Byte 0-3:   Header ve kontrol byte'ları
Byte 4-131: Veri (128 byte)
Byte 132:   Checksum
```

### Önemli Register İndeksleri
```
0-3:     HEADER_1, HEADER_2, LENGTH, PACKET_ID
4-5:     FPGA_VERSION, FPGA_REVISION
20:      DISC_IN_VALUES
25:      LTC4281_PMON_STATUS
32:      LTC4281_SATA0_STATUS
39:      LTC4281_SATA1_STATUS
46:      LTC4281_GPU_12V_STATUS
79-85:   Sıcaklık sensörleri (TMP100 ve GPU)
```

### Komut Protokolü

#### DISC OUT Komutu
```
Header1: 0x41
Header2: 0x56
Length:  0x05
Command: 0x10 + channel (0-3)
Data:    0x01 (enable) / 0x00 (disable)
Checksum
```

#### LED Komutu
```
Header1: 0x41
Header2: 0x56
Length:  0x05
Command: 0x20 + LED (0=R, 1=G, 2=B)
Data:    0x01 (enable) / 0x00 (disable)
Checksum
```

#### SATA Zeroize Komutu
```
Header1: 0x41
Header2: 0x56
Length:  0x05
Command: 0x30
Data:    0x01 (SATA0) | 0x02 (SATA1)
Checksum
```

## RENK KODLAMA SİSTEMİ

### Tablo Hücreleri
- **Yeşil (#1b5e20)**: Geçerli değer aralığında
- **Kırmızı (#b71c1c)**: Aralık dışı veya hata
- **Gri (#424242)**: N/A veya tanımsız

### Sıcaklık Sensörleri
- Her zaman yeşil (otomatik geçerli kabul edilir)

### Durum Butonları
- **Kırmızı (#c62828)**: Disabled, Fail, Hata
- **Yeşil (#2e7d32)**: Enabled, OK, Normal
- **Beyaz (#ffffff)**: Neutral disabled
- **Gri (#666666)**: N/A, Pasif

## PERFORMANS

- **Güncelleme Hızı**: 100ms (10 Hz)
- **Paket Doğrulama**: Checksum kontrolü
- **Hata Yönetimi**: Otomatik hata ayıklama ve loglama

## GELİŞTİRME NOTLARI

### Özelleştirme
`_get_dynamic_meaning()` fonksiyonu içinde status bit'lerini decode edebilirsiniz:

```python
if index == 25:  # LTC4281_PMON_STATUS
    status_bits = []
    if value & 0x80: status_bits.append("ON")
    if value & 0x40: status_bits.append("COOLDOWN")
    # ... diğer bit'ler
    return ", ".join(status_bits)
```

### Yeni Sensör Ekleme
1. `_init_data_limits()` içinde min/max değerleri tanımlayın
2. `_get_signal_names()` içinde sinyal adını ekleyin
3. Gerekirse `_get_dynamic_meaning()` içinde anlamlandırma yapın

## LİSANS

Bu yazılım [Şirket/Proje Adı] için geliştirilmiştir.

## DESTEK

Sorularınız için lütfen geliştirme ekibiyle iletişime geçin.

---

**Son Güncelleme**: Versiyon 3.0 - PDF geri bildirimleri uygulandı  
**Geliştirici**: [Geliştirici Adı]  
**Tarih**: 2025
