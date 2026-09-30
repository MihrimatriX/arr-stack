# 🎬 Tam Medya Otomasyon Yığını

Bu proje, medya koleksiyonunuzu tamamen otomatik hale getiren bir Docker yığını. *arr uygulamaları, medya sunucuları ve yönetim araçlarını bir araya getirerek kendi Netflix'inizi kurmanızı sağlıyor.

## 🌟 Ne İşe Yarar?

Kısaca şöyle düşünün: Film/dizi istiyorsunuz, sistem otomatik buluyor, indiriyor, düzenliyor ve tüm cihazlarınızda izleyebiliyorsunuz. Hiç elle dokunmadan:

- **Bulur**: Yeni çıkan filmleri, dizileri, müzikleri takip eder
- **İndirir**: Tercihlerinize uygun kalitede otomatik indirir  
- **Düzenler**: Dosyaları düzgün isimlendirir ve klasörlere yerleştirir
- **Yayınlar**: Tüm cihazlarınızdan erişebilir hale getirir
- **Yönetir**: Koleksiyonunuzu sürekli güncel tutar

## 🏗️ Mimari Genel Bakış

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Keşif         │    │   İndirme       │    │   Düzenleme     │
│                 │    │                 │    │                 │
│ • Overseerr     │───▶│ • qBittorrent   │───▶│ • *arr Uygulamaları│
│ • Prowlarr      │    │ • İndeksleyiciler│    │ • Bazarr        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Yayınlama     │    │   Yönetim       │    │   İzleme        │
│                 │    │                 │    │                 │
│                 │    │ • Homarr        │    │                 │
│ • Emby          │    │ • Portainer     │    │                 │
│ • Navidrome     │    │ • Watchtower    │    │ • Audiobookshelf│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Hangi Uygulamalar Var?

### 📺 Medya Yöneticileri (*arr Ailesi)
- **[Sonarr](https://sonarr.tv/)** - Dizileri takip eder, yeni bölümleri bulur
- **[Radarr](https://radarr.video/)** - Filmleri takip eder, kaliteli sürümleri indirir  
- **[Lidarr](https://lidarr.audio/)** - Müzik albümlerini takip eder
- **[Prowlarr](https://prowlarr.com/)** - Tüm arama kaynaklarını tek yerden yönetir
- **[Bazarr](https://www.bazarr.media/)** - Altyazıları otomatik bulur ve indirir

### 🎬 Medya Sunucuları
- **[Emby](https://emby.media/)** - Şık uygulamaları olan medya sunucusu (bazı özellikler Emby Premiere ister)
- **[Navidrome](https://www.navidrome.org/)** - Spotify benzeri müzik sunucusu
- **[Audiobookshelf](https://www.audiobookshelf.org/)** - Sesli kitap sunucusu

### 🛠️ Yardımcı Araçlar
- **[Homarr](https://homarr.dev/)** - Tüm servisleri tek ekranda gösterir
- **[Overseerr](https://overseerr.dev/)** - Aile üyeleri film/dizi isteyebilir
- **[qBittorrent](https://www.qbittorrent.org/)** - Torrent indirme motoru
- **[Recyclarr](https://recyclarr.dev/)** - Kalite ayarlarını otomatik senkronize eder
- **[Portainer](https://www.portainer.io/)** - Docker konteynerlerini yönetir
- **[Watchtower](https://containrrr.dev/watchtower/)** - Uygulamaları otomatik günceller

### 📊 İstatistik Araçları

## 🎯 Neden Bu Yığını Kullanmalısınız?

- **🔄 Sıfır El Değmeden**: Kurduktan sonra hiçbir şeye dokunmadan çalışır
- **🌐 Her Yerde**: Windows, Mac, Linux - fark etmez, hepsinde çalışır
- **📱 Her Cihazda**: Telefon, tablet, TV, bilgisayar - hepsinde izleyebilirsiniz
- **🔒 Tamamen Sizin**: Verileriniz sizde kalır, kimseye gitmez
- **⚡ Hızlı**: Optimize edilmiş, yavaşlamaz
- **🛡️ Güvenli**: Her uygulama ayrı sandıkta çalışır
- **📈 Büyüyebilir**: İstediğiniz kadar film/dizi ekleyebilirsiniz

## 🚀 Nasıl Kurulur?

### Gereksinimler
- Docker Desktop (Windows'ta WSL2 ile) veya Docker Engine (Linux/Mac'te)
- En az 4GB RAM ve 20GB boş yer
- Docker hakkında biraz bilgi (çok karmaşık değil)

### Adım Adım Kurulum

1. **Projeyi indirin**
   ```bash
   git clone https://github.com/......./arr-stack.git
   cd arr-stack
   ```

2. **Ayarları yapın**
   ```bash
   cp .env.example .env
   # .env dosyasını açıp istediğiniz ayarları yapın
   ```

3. **Başlatın**
   ```bash
   docker compose up -d
   ```
   `arr-seed` + `arr-setup` konteynerleri ilk kurulumu kendisi yapar: qBittorrent şifresi ve kategorileri,
   *arr root folder + qBittorrent bağlantısı, Prowlarr ↔ *arr senkronu, Bazarr ↔ Sonarr/Radarr,
   Emby kullanıcısı ve kütüphaneleri. Tüm arayüzlerde giriş: `.env` içindeki `STACK_USER` / `STACK_PASSWORD`.
   Durumu görmek için: `docker logs arr-setup`. Elle kalanlar: indeksleyici seçimi (`PROWLARR_INDEXERS`),
   Bazarr dil profili, Homarr paneli.

4. **Kullanmaya başlayın**
   - Ana Panel:        http://localhost:7575 (Homarr)
   - Dizi Yöneticisi:  http://localhost:8989 (Sonarr)
   - Film Yöneticisi:  http://localhost:7878 (Radarr)
   - Müzik Yöneticisi: http://localhost:8686 (Lidarr)
   - Medya Sunucusu:   http://localhost:8096 (Emby)

## 📁 Dizin Yapısı

```
arr-stack/
├── config/                # Servis yapılandırmaları
│   ├── homarr/            # Kontrol paneli ayarları
│   ├── sonarr/            # Dizi yöneticisi
│   ├── radarr/            # Film yöneticisi
│   ├── lidarr/            # Müzik yöneticisi
│   ├── prowlarr/          # İndeksleyici yöneticisi
│   ├── bazarr/            # Altyazı yöneticisi
│   ├── emby/              # Alternatif medya sunucusu
│   ├── qbittorrent/       # Torrent istemcisi
│   ├── portainer/         # Konteyner yönetimi
│   └── ...
├── downloads/             # İndirme dizini
├── media/                 # Düzenlenmiş medya dosyaları
│   ├── movies/            # Film koleksiyonu
│   ├── tv/                # Dizi koleksiyonu
│   ├── music/             # Müzik koleksiyonu
│   └── audiobooks/        # Sesli kitap koleksiyonu
├── docker-compose.yml     # Servis tanımları
├── .env                   # Ortam değişkenleri
└── README.md              # Bu dosya
```

## ⚙️ Yapılandırma

### Ortam Değişkenleri
`.env` dosyasındaki önemli değişkenler:

```bash
# Kullanıcı ve Saat Dilimi
PUID=1000
PGID=1000
TZ=Europe/Istanbul

# Servis Portları
HOMARR_PORT=7575
SONARR_PORT=8989
RADARR_PORT=7878
LIDARR_PORT=8686
PROWLARR_PORT=9696
BAZARR_PORT=6767
QBITTORRENT_WEBUI_PORT=8080
EMBY_HTTP_PORT=8096

# Dizin Yolları
CONFIG_ROOT=./config
MEDIA_MOVIES_DIR=./media/movies
MEDIA_TV_DIR=./media/tv
MEDIA_MUSIC_DIR=./media/music
DOWNLOADS_ROOT=./downloads

# İsteğe Bağlı
WATCHTOWER_NOTIFICATIONS=      # Discord/Slack webhook URL'si
```

### İlk Ayarlar (Önemli!)

1. **qBittorrent'i Ayarlayın**
   - Varsayılan şifreyi değiştirin (admin/adminadmin)
   - İndirme kategorilerini ekleyin (sonarr, radarr, lidarr)
   - İndirme klasörünü ayarlayın

2. **Prowlarr'da Arama Kaynaklarını Ekleyin**
   - İstediğiniz torrent sitelerini ekleyin
   - API anahtarlarını girin
   - *arr uygulamalarıyla bağlayın

3. ***arr Uygulamalarını Hazırlayın**
   - qBittorrent'i indirme istemcisi olarak ekleyin
   - Medya klasörlerini ayarlayın
   - Kalite tercihlerinizi belirleyin
   - Prowlarr'dan arama kaynaklarını alın

4. **Medya Sunucularını Kurun**
   - Film/dizi klasörlerini kütüphaneye ekleyin
   - Metadata ayarlarını yapın
   - Kullanıcı hesapları oluşturun

5. **Ana Paneli Düzenleyin**
   - Homarr'a tüm servisleri ekleyin
   - API bağlantılarını kurun
   - İstediğiniz gibi düzenleyin

## 🔧 İleri Seviye Ayarlar

### Kalite Profillerini Senkronize Etme
Recyclarr ile tüm *arr uygulamalarında aynı kalite ayarlarını kullanabilirsiniz:

```yaml
# config/recyclarr/config.yml
sonarr:
  instance_name: sonarr
  base_url: http://sonarr:8989
  api_key: api_anahtarınız
  quality_definition:
    type: series
    quality_profiles:
      - name: "HD-1080p"
        upgrade_until_quality: "Bluray-1080p"
        qualities:
          - "HDTV-1080p"
          - "Bluray-1080p"
```

### Otomatik Güncellemeler
Watchtower uygulamaları otomatik günceller. Discord'a bildirim göndermek için:

```bash
WATCHTOWER_NOTIFICATIONS=discord://webhook_url
```

### Yedekleme
Ayarlarınızı kaybetmemek için düzenli yedek alın:

```bash
# Yedek oluştur
tar -czf arr-stack-yedek-$(date +%Y%m%d).tar.gz config/

# Yedeği geri yükle
tar -xzf arr-stack-yedek-20240101.tar.gz
```

## 🛠️ Sorun Çözme

### Sık Karşılaşılan Problemler

**Uygulamalar başlamıyor**
- Docker'ın çalıştığından emin olun
- Portların başka bir şey tarafından kullanılmadığını kontrol edin
- Yeterli disk alanı olduğunu kontrol edin

**İndirmeler gelmiyor**
- qBittorrent ayarlarını kontrol edin
- Arama kaynaklarının çalıştığını kontrol edin
- *arr uygulamalarındaki indirme ayarlarını gözden geçirin

**Filmler/diziler görünmüyor**
- Dosya izinlerini kontrol edin
- Klasör yollarının doğru olduğunu kontrol edin
- Medya sunucusu kütüphane ayarlarını kontrol edin

**Sistem yavaş**
- RAM ve CPU kullanımını kontrol edin
- Kalite ayarlarını düşürün
- Donanım transcoding'i açmayı deneyin

### Logları İnceleme

```bash
# Tüm logları göster
docker compose logs -f

# Sadece Sonarr loglarını göster
docker compose logs -f sonarr

# Hangi servislerin çalıştığını göster
docker compose ps

# Bir servisi yeniden başlat
docker compose restart sonarr
```

## 🔒 Güvenlik

- **Ağ**: Servisler sadece localhost'ta çalışır (güvenli)
- **Şifreler**: Tüm uygulamalarda güçlü şifreler kullanın
- **Güncellemeler**: Watchtower otomatik günceller
- **Yedekler**: Ayarlarınızı düzenli yedekleyin
- **Dış Erişim**: İnternetten erişim için ters proxy kullanın

## 📈 Performans

### Donanım İhtiyaçları
- **Minimum**: 4GB RAM, 2 CPU, 100GB disk
- **Rahat**: 8GB RAM, 4 CPU, 1TB+ disk
- **Mükemmel**: 16GB+ RAM, 8+ CPU, SSD disk

### Hızlandırma İpuçları
- SSD kullanın (çok daha hızlı)
- Donanım transcoding'i açın (varsa)
- Kalite ayarlarını makul tutun

## 🙏 Teşekkürler

- [LinuxServer.io](https://www.linuxserver.io/) - Harika Docker imajları için
- [Hotio](https://hotio.dev/) - Ek konteyner imajları için  
- *arr ekosisteminin tüm geliştiricileri
- Açık kaynak topluluğu