# arr-stack

[English](README.md) · [Proje sayfası](https://mihrimatrix.github.io/arr-stack/) · [Servis detayları](SERVICES.md)

Evde kendi medya sunucunu kurmak için hazır bir Docker Compose stack'i. İzlemek istediğin filmi, diziyi ya da albümü eklemen yeterli. Gerisini sistem hallediyor: içeriği buluyor, indiriyor, altyazısını ekliyor, dosyaya düzgün bir isim verip kütüphaneye koyuyor. Sen de TV'den, telefondan ya da tarayıcıdan izliyorsun.

Bu tür kurulumlarda asıl zahmetli kısım, uygulamaları birbirine bağlamak. Normalde her birinin arayüzüne tek tek girip API anahtarı kopyalaman, klasör yolu girmen, indirme istemcisi eklemen gerekir. Bu repoda bunu küçük bir Python script'i yapıyor. İlk `docker compose up` komutundan sonra sistem kullanıma hazır oluyor.

## Nasıl çalışıyor?

```
 Seerr ──istek──▶ Sonarr / Radarr / Lidarr ──arama──▶ Prowlarr ──▶ indexer'lar
                           │                              (Cloudflare için FlareSolverr)
                           ▼
                      qBittorrent ──indirme──▶ /downloads
                           │
                           ▼
              /media/movies, /media/tv, /media/music ──▶ Emby ──▶ TV, telefon, tarayıcı
                           ▲
                        Bazarr (altyazı)
```

1. Seerr'den istekte bulunuyorsun ya da içeriği doğrudan Sonarr'a (dizi), Radarr'a (film) veya Lidarr'a (müzik) ekliyorsun.
2. Uygulama Prowlarr üzerinden indexer'larda arama yapıyor ve en uygun sonucu qBittorrent'e gönderiyor.
3. İndirme bitince dosya `media/` altına taşınıp yeniden adlandırılıyor, Emby de kütüphaneyi tarıyor.
4. Bazarr yeni eklenen film ve bölümlere altyazı buluyor.
5. Homarr ise hepsine tek sayfadan ulaşmanı sağlıyor ve yaklaşan yayınları bir takvimde gösteriyor.

## Servisler

| Servis | Görevi | Port |
|---|---|---|
| [Homarr](https://homarr.dev/) | Tüm uygulamaları ve yayın takvimini gösteren ana panel | 7575 |
| [Seerr](https://github.com/seerr-team/seerr) | Film ve dizi isteme sayfası, Emby hesabıyla giriş yapılıyor | 5055 |
| [Sonarr](https://sonarr.tv/) | Dizileri takip ediyor, yeni bölümleri indiriyor | 8989 |
| [Radarr](https://radarr.video/) | Filmleri takip ediyor | 7878 |
| [Lidarr](https://lidarr.audio/) | Sanatçıları ve albümleri takip ediyor | 8686 |
| [Prowlarr](https://prowlarr.com/) | Indexer'ları tek yerden yönetiyor ve diğer uygulamalarla paylaşıyor | 9696 |
| [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) | Bazı indexer'lardaki Cloudflare korumasını aşıyor | dahili |
| [Bazarr](https://www.bazarr.media/) | Altyazı indiriyor | 6767 |
| [qBittorrent](https://www.qbittorrent.org/) | Torrent istemcisi | 8080 |
| [Emby](https://emby.media/) | Medya sunucusu ve oynatıcı uygulamaları (bazı özellikler Emby Premiere gerektiriyor) | 8096 |
| [Watchtower](https://github.com/nicholas-fedor/watchtower) | Bu stack'teki container'ları her gece 04:30'da güncelliyor | yok |

Her servisin ayrıntıları için [SERVICES.md](SERVICES.md) dosyasına bakabilirsin.

## Kurulumda senin yerine yapılanlar

`setup/bootstrap.py` script'ini, bir kez çalışıp kapanan iki yardımcı container çalıştırıyor.

`arr-seed`, uygulamalar açılmadan önce devreye giriyor. *arr uygulamalarının API anahtarlarını, qBittorrent'in giriş bilgilerini ve Bazarr'ın Sonarr ile Radarr'a bağlanma ayarlarını önceden dosyalara yazıyor.

`arr-setup` ise uygulamalar ayağa kalktıktan sonra çalışıyor ve hepsini API'ler üzerinden birbirine bağlıyor:

- Bütün web arayüzlerine aynı kullanıcı adı ve şifreyle giriliyor: `STACK_USER` / `STACK_PASSWORD`.
- qBittorrent'te `tv`, `movies` ve `music` kategorileri açılıyor. Paylaşım oranı 1'e ulaşınca seed duruyor, böylece biten torrent'ler uygulamalar tarafından temizlenebiliyor.
- Sonarr, Radarr ve Lidarr'a medya klasörleri tanımlanıyor ve indirme istemcisi olarak qBittorrent ekleniyor.
- Prowlarr bu üç uygulamaya bağlanıyor, `PROWLARR_INDEXERS` içindeki indexer'ları ekliyor ve hepsini FlareSolverr üzerinden çalışacak şekilde ayarlıyor.
- Bazarr'da üyelik gerektirmeyen altyazı sağlayıcıları açılıyor ve `SUBTITLE_LANGUAGES` içindeki diller kullanılıyor.
- Emby'nin ilk kurulum ekranı otomatik geçiliyor; Movies, Shows ve Music kütüphaneleri oluşturuluyor. *arr uygulamaları her yeni dosyadan sonra Emby'ye kütüphaneyi taratıyor.
- Seerr; Emby, Radarr ve Sonarr'a bağlanıyor.
- Homarr'da yönetici hesabı açılıyor ve her uygulama için bir kart içeren bir pano hazırlanıyor.

Tüm adımlar başarılı olursa iki yardımcı container da kendini siliyor. Bir adım hata verirse diğerleri yine çalışıyor ve `arr-setup` silinmiyor. Böylece `docker logs arr-setup` ile neyin ters gittiğine bakabiliyorsun. `docker compose up -d` komutunu tekrar çalıştırmaktan çekinme; script önceden yapılmış adımları atlıyor.

## Hızlı başlangıç

Gerekenler: Docker (Windows ve macOS'ta Docker Desktop, Linux'ta Docker Engine) ve birkaç GB boş RAM.

```bash
git clone https://github.com/MihrimatriX/arr-stack.git
cd arr-stack
cp .env.example .env
```

`.env` dosyasını aç ve en azından `STACK_PASSWORD` değerini değiştir. Ardından:

```bash
docker compose up -d
docker logs -f arr-setup   # "done" yazısını bekle
```

İlk açılış birkaç dakika sürüyor. Kurulum bitince tarayıcıda http://localhost:7575 adresine git ve `STACK_USER` ile `STACK_PASSWORD` bilgileriyle Homarr'a giriş yap. Homarr şifrede en az bir sembol istiyor. Şifrende sembol yoksa Homarr'a girerken sonuna `!` eklemen gerekiyor; diğer uygulamalarda şifre aynen geçerli.

## `.env` ayarları

| Değişken | Ne işe yarıyor |
|---|---|
| `PUID`, `PGID` | Dosyaların sahibi olacak kullanıcı ve grup (Linux) |
| `TZ` | Saat dilimi, örneğin `Europe/Istanbul` |
| `*_PORT` | Her uygulamanın bilgisayarında açılacağı port |
| `CONFIG_ROOT` | Uygulama ayarlarının tutulduğu klasör (`./config`) |
| `MEDIA_MOVIES_DIR`, `MEDIA_TV_DIR`, `MEDIA_MUSIC_DIR` | Kütüphane klasörleri |
| `DOWNLOADS_ROOT` | İndirme klasörü |
| `STACK_USER`, `STACK_PASSWORD` | Bütün web arayüzleri için ortak kullanıcı adı ve şifre |
| `PROWLARR_INDEXERS` | Eklenecek indexer'lar, virgülle ayrılmış. Boş bırakırsan hiçbiri eklenmez |
| `SUBTITLE_LANGUAGES` | Altyazı dilleri, ilk yazılan öncelikli. Varsayılan `tr,en` |
| `WATCHTOWER_NOTIFICATIONS` | İsteğe bağlı bildirim adresi, örneğin bir Discord webhook'u |

## Klasör yapısı

```
arr-stack/
├── docker-compose.yml   # tüm servisler
├── .env.example         # .env olarak kopyala
├── setup/bootstrap.py   # ilk kurulum script'i
├── config/              # uygulama ayarları (git'e eklenmez)
├── downloads/           # devam eden ve biten indirmeler
└── media/
    ├── movies/
    ├── tv/
    └── music/
```

`config/`, `downloads/`, `media/` ve `.env` zaten `.gitignore` içinde. Kurulumunu yedeklemek için `config/` klasörünü ve `.env` dosyasını saklaman yeterli:

```bash
tar -czf arr-stack-yedek-$(date +%Y%m%d).tar.gz config/ .env
```

## Sorun giderme

```bash
docker compose ps              # hangi servisler çalışıyor
docker logs arr-setup          # kurulum hata verdiyse nedeni
docker compose logs -f sonarr  # tek bir uygulamanın logları
docker compose restart sonarr
```

Kurulum sırasında qBittorrent'e giriş yapılamıyorsa, büyük ihtimalle `config/qbittorrent` klasöründe eski bir kurulumdan kalan ayarlar var. O kurulumun şifresini `STACK_PASSWORD` olarak yaz ya da klasörü silip baştan başla.

İndirme tamamlandığı halde içerik Emby'de görünmüyorsa, `.env` içindeki klasör yollarının gerçekten var olduğunu ve Docker'ın bu klasörlere yazabildiğini kontrol et.

## Bilmen gerekenler

Uygulamalar bilgisayarın tüm ağ arayüzlerinden erişilebilir durumda, yani evdeki diğer cihazlardan da açabilirsin. Homarr'daki kartlar `localhost` adresine yönlendiriyor; panoyu başka bir cihazdan kullanacaksan kartlardaki adresleri değiştirmen gerekiyor. Bu portları ters proxy ve HTTPS olmadan internete açma.

Yalnızca indirme hakkına sahip olduğun içerikleri indir.

Container imajları [LinuxServer.io](https://www.linuxserver.io/) ve yukarıda adı geçen projelerden geliyor.
