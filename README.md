# 🚗 Markov Zinciri Trafik Simülasyonu

İTÜ kampüs trafik akışını modelleyen ve analiz eden bir Markov Zinciri simülasyon uygulaması.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![NumPy](https://img.shields.io/badge/NumPy-Scientific-orange.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-red.svg)

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Matematiksel Model](#-matematiksel-model)
- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Ekran Görüntüleri](#-ekran-görüntüleri)

---

## 🎯 Proje Hakkında

Bu proje, **Markov Zincirleri** kullanarak bir trafik ağındaki araç akışını modellemektedir. 13 düğümlü bir ağ yapısında, araçların giriş noktalarından çıkış noktalarına nasıl dağıldığını simüle eder.

### Ağ Yapısı

```
        N1 (Kuzey Giriş)
             │
             ▼
    N4 ──► N8 ◄── N5 ◄─┐
     │      │     │    │
     │      ▼     ▼    │
     │    N10   N6 ──► N3 (Çıkış)
     │           │
     │           ▼
     │          N7
     │           │
     │           ▼
    N12 ◄── N13 ◄── N11 (Güney Giriş)
  (Çıkış)        │
                 ▼
                N9 (Çıkış)
```

### Düğüm Türleri

| Tür           | Düğümler            | Açıklama                           |
| ------------- | ------------------- | ---------------------------------- |
| 🟢 **Giriş**  | N1, N2, N4, N11     | Araçların sisteme girdiği noktalar |
| 🔴 **Çıkış**  | N3, N9, N10, N12    | Yutan (Absorbing) düğümler         |
| 🟡 **Kavşak** | N5, N6, N7, N8, N13 | Geçici (Transient) düğümler        |

---

## 📐 Matematiksel Model

### Markov Zinciri Temelleri

Sistem, **ayrık zamanlı Markov zinciri** olarak modellenmiştir:

$$x(t+1) = (x(t) + U(t)) \cdot P$$

Burada:

- $x(t)$ : t anındaki durum vektörü (her düğümdeki araç sayısı)
- $U(t)$ : t anındaki giriş vektörü
- $P$ : Geçiş olasılık matrisi (13×13)

### Geçiş Olasılık Matrisi (P)

**Stokastik matris** özellikleri:

- Her satır toplamı = 1
- Tüm elemanlar ≥ 0

**Örnek geçişler:**
| Kaynak | Hedef | Olasılık |
|--------|-------|----------|
| N5 | N6 | 0.70 |
| N5 | N9 | 0.30 |
| N6 | N3 | 0.20 |
| N6 | N7 | 0.40 |
| N6 | N10 | 0.40 |

### Analiz Yöntemleri

#### 1. Darboğaz (Bottleneck) Analizi

Simülasyon boyunca en yüksek yoğunluğa ulaşan düğümü tespit eder.

#### 2. Steady State (Durağan Durum) Analizi

**Fundamental Matrix** kullanarak yapısal darboğazı belirler:

$$N = (I - Q)^{-1}$$

Burada $Q$, geçici düğümler arası geçiş alt matrisidir.

---

## ✨ Özellikler

### 🎮 İnteraktif Simülasyon Modu

- **Adım adım simülasyon**: Her saat için trafik akışını izleyin
- **Dinamik parametreler**: Araç sayılarını slider ile ayarlayın
- **Rush Hour desteği**: Saat 08:00 ve 17:00'de yoğun trafik
- **Canlı görselleştirme**: Anlık grafikler ve ağ haritası

### 📊 Analiz Araçları

- **24 saatlik simülasyon**: Tam gün trafik analizi
- **Heatmap görselleştirme**: Yoğunluk haritası
- **Darboğaz tespiti**: En kritik düğümü bulma
- **P Matrisi görselleştirme**: Geçiş olasılıkları

### 🚦 Trafik Kısıtlamaları

| Saat Dilimi               | Araç Limiti   | Açıklama        |
| ------------------------- | ------------- | --------------- |
| Normal (0-7, 9-16, 18-23) | 0 - 2,000     | Düşük yoğunluk  |
| Rush Hour (8, 17)         | 2,000 - 5,000 | Yüksek yoğunluk |

---

## 🚀 Kurulum

### Gereksinimler

```bash
Python 3.8+
```

### Bağımlılıklar

```bash
pip install numpy matplotlib
```

> **Not:** `tkinter` Python ile birlikte gelir, ayrıca kurulum gerekmez.

### Çalıştırma

```bash
python3 main.py
```

---

## 📖 Kullanım

### Ana Ekran

1. **▶ Simülasyonu Başlat**: 24 saatlik otomatik simülasyon
2. **🎮 İnteraktif Mod**: Manuel kontrollü simülasyon
3. **📊 Darboğaz Analizi**: En yoğun düğümü bul
4. **⚖ Steady State**: Yapısal analiz
5. **🎲 P Matrisi**: Geçiş olasılıklarını görüntüle

### İnteraktif Mod

```
┌─────────────────────────────────────────┐
│  ⏰ Saat Kontrolü                        │
│  [========●==========] 08:00            │
│                                         │
│  🚗 Araç Girişleri                      │
│  N1:  [====●====] 1400                  │
│  N2:  [===●=====] 1300                  │
│  N11: [===●=====] 1300                  │
│                                         │
│  ⚠️ Rush Hour: 2000-5000 araç           │
│  Toplam: 4,000 araç/saat                │
│                                         │
│  [▶ Adım İlerle]  [⏭ 10 Adım]          │
│  [🔄 Sıfırla]     [📊 Rush Hour]        │
└─────────────────────────────────────────┘
```

### Görselleştirmeler

| Grafik          | Açıklama                                   |
| --------------- | ------------------------------------------ |
| 📈 Zaman Serisi | Düğüm yoğunluklarının zamana göre değişimi |
| 🔥 Heatmap      | Tüm düğümlerin yoğunluk haritası           |
| 🗺️ Ağ Haritası  | Düğümlerin anlık durumu (renk kodlu)       |
| 📊 Bar Chart    | Karşılaştırmalı düğüm yoğunlukları         |

---

## 🎨 Arayüz

Uygulama modern bir **dark theme** tasarıma sahiptir:

- 🎨 **Renk Paleti**: Koyu mavi tonları (#1a1a2e, #16213e)
- 🔴 **Accent**: Coral kırmızı (#e94560)
- 🟢 **Başarı**: Turkuaz (#4ecca3)
- 🟡 **Uyarı**: Altın sarısı (#ffc107)

---

## 📁 Dosya Yapısı

```
Markov Trafik Modeli/
├── main.py          # Ana uygulama dosyası
├── README.md        # Bu dosya
└── requirements.txt # Bağımlılıklar (opsiyonel)
```

---

## 🔬 Teknik Detaylar

### Sınıf Yapısı

```python
TrafficSimulation    # Markov zinciri hesaplamaları
├── setup_matrix()   # P matrisini oluştur
├── run_simulation() # 24 saat simülasyon
├── run_single_step()# Tek adım simülasyon
├── analyze_bottleneck()    # Darboğaz analizi
└── analyze_steady_state()  # Durağan durum analizi

InteractiveSimulation  # İnteraktif mod penceresi
├── step_forward()     # Adım ilerle
├── update_visualization() # Grafikleri güncelle
└── update_hour_limits()   # Saat limitlerini ayarla

App                    # Ana uygulama penceresi
├── run_sim()          # Simülasyonu çalıştır
├── show_bottleneck()  # Darboğaz göster
├── show_steady_state()# Steady state göster
└── show_probability_matrix() # P matrisini göster
```

---

## 📚 Teorik Arka Plan

### Markov Zinciri Nedir?

Markov zinciri, gelecek durumun yalnızca mevcut duruma bağlı olduğu (geçmişe değil) stokastik bir süreçtir. Bu özelliğe **Markov özelliği** denir:

$$P(X_{t+1} | X_t, X_{t-1}, ..., X_0) = P(X_{t+1} | X_t)$$

### Yutan (Absorbing) Durumlar

Bir durum **yutan** (absorbing) ise, oradan çıkış yoktur:

$$P_{ii} = 1$$

Bu projede çıkış noktaları (N3, N9, N10, N12) yutan durumlardır.

### Geçici (Transient) Durumlar

Yutan olmayan durumlar **geçici** (transient) olarak adlandırılır. Araçlar bu düğümlerden geçer ve sonunda bir çıkışa ulaşır.

---

## 👨‍💻 Geliştirici

Bu proje İTÜ için geliştirilmiştir.

---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

<p align="center">
  <b>🚗 İyi Simülasyonlar! 🚦</b>
</p>
