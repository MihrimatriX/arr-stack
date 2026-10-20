# Services / Servisler

Each service in `docker-compose.yml`, what it does, and what `setup/bootstrap.py` sets up for it on the first start. Settings for each app live in `config/<app>/`.

`docker-compose.yml` içindeki servisler, ne işe yaradıkları ve `setup/bootstrap.py` script'inin ilk açılışta her biri için neleri ayarladığı. Her uygulamanın ayarları `config/<uygulama>/` klasöründe tutuluyor.

| Service / Servis | Port | Image / İmaj |
|---|---|---|
| Homarr | 7575 | `ghcr.io/ajnart/homarr` |
| Seerr | 5055 | `ghcr.io/seerr-team/seerr` |
| Sonarr | 8989 | `lscr.io/linuxserver/sonarr` |
| Radarr | 7878 | `lscr.io/linuxserver/radarr` |
| Lidarr | 8686 | `lscr.io/linuxserver/lidarr` |
| Prowlarr | 9696 | `lscr.io/linuxserver/prowlarr` |
| FlareSolverr | internal / dahili | `ghcr.io/flaresolverr/flaresolverr` |
| Bazarr | 6767 | `lscr.io/linuxserver/bazarr` |
| qBittorrent | 8080, 6881 | `lscr.io/linuxserver/qbittorrent` |
| Emby | 8096 | `lscr.io/linuxserver/emby` |
| Watchtower | none / yok | `nickfedor/watchtower` |

## Homarr

The start page, with a tile for every app and a calendar of upcoming episodes and movies.

Setup creates the owner account with `STACK_USER` and `STACK_PASSWORD`. Homarr requires a symbol in the password, so if yours has none it gets `!` added at the end for Homarr only. The board gets one tile per app with a status check, API keys for Sonarr, Radarr, Lidarr, and Seerr, and a calendar widget. On later runs only the API keys are refreshed, so your own layout changes stay.

Tüm uygulamalara tek yerden ulaştığın ana panel. Her uygulama için bir kart ve yaklaşan bölüm ve filmleri gösteren bir takvim var.

Kurulum, `STACK_USER` ve `STACK_PASSWORD` ile yönetici hesabını açıyor. Homarr şifrede en az bir sembol istediği için, şifrende sembol yoksa Homarr'daki şifrenin sonuna `!` ekleniyor. Panoya her uygulama için çalışıp çalışmadığını gösteren bir kart, Sonarr, Radarr, Lidarr ve Seerr'in API anahtarları ve bir takvim ekleniyor. Sonraki çalıştırmalarda yalnızca API anahtarları güncelleniyor; panoda yaptığın değişiklikler korunuyor.

## Seerr

A request page for movies and shows. Users sign in with their Emby account.

Setup signs in with your Emby login (that account becomes the Seerr admin), imports the Emby libraries, and links Radarr for movies and Sonarr for shows with their first quality profile. Music requests are not supported; add music in Lidarr.

Film ve dizi isteyebileceğin sayfa. Kullanıcılar Emby hesaplarıyla giriş yapıyor.

Kurulum senin Emby hesabınla oturum açıyor (bu hesap Seerr'in yöneticisi oluyor), Emby kütüphanelerini içeri alıyor ve filmler için Radarr'ı, diziler için Sonarr'ı ilk kalite profiliyle bağlıyor. Seerr'den müzik istenemiyor, müziği Lidarr'dan eklemen gerekiyor.

## Sonarr, Radarr, Lidarr

Sonarr tracks TV shows, Radarr movies, and Lidarr music. Each one searches through Prowlarr, sends downloads to qBittorrent, and moves finished files into the library with clean names.

For each app, setup writes an API key before the first start, sets the web login, adds the library folder (`/tv`, `/movies`, `/music`), adds qBittorrent as the download client with its own category (`tv`, `movies`, `music`), and adds an Emby connection that triggers a library rescan after imports, upgrades, renames, and deletes.

Sonarr dizileri, Radarr filmleri, Lidarr da müziği takip ediyor. Üçü de Prowlarr üzerinden arama yapıyor, indirilecekleri qBittorrent'e gönderiyor ve biten dosyaları düzgün isimlerle kütüphaneye taşıyor.

Kurulum her biri için şunları yapıyor: ilk açılıştan önce bir API anahtarı oluşturuyor, web arayüzü girişini ayarlıyor, kütüphane klasörünü (`/tv`, `/movies`, `/music`) tanımlıyor ve qBittorrent'i kendine ait bir kategoriyle (`tv`, `movies`, `music`) indirme istemcisi olarak ekliyor. Ayrıca bir Emby bağlantısı kuruyor; böylece dosya eklendiğinde, kalitesi yükseltildiğinde, adı değiştiğinde ya da silindiğinde Emby kütüphaneyi yeniden tarıyor.

## Prowlarr

Keeps the list of indexers and shares it with Sonarr, Radarr, and Lidarr.

Setup links Prowlarr to all three apps with full sync, adds FlareSolverr as an indexer proxy under a `flaresolverr` tag, and adds the indexers named in `PROWLARR_INDEXERS` with that tag. An indexer that fails its connection test is skipped and named in the `arr-setup` log.

Indexer listesini tutuyor ve Sonarr, Radarr ve Lidarr ile paylaşıyor.

Kurulum, Prowlarr'ı bu üç uygulamaya tam senkronizasyonla bağlıyor. FlareSolverr'ı `flaresolverr` etiketiyle proxy olarak ekliyor, ardından `PROWLARR_INDEXERS` içinde yazan indexer'ları aynı etiketle ekliyor. Bağlantı testini geçemeyen bir indexer olursa atlanıyor ve adı `arr-setup` loguna yazılıyor.

## FlareSolverr

Opens Cloudflare-protected indexer pages in a headless browser so Prowlarr can search them. It has no web UI and no port on the host.

Cloudflare korumalı indexer sayfalarını arka planda çalışan bir tarayıcıyla açıyor, böylece Prowlarr bu sitelerde de arama yapabiliyor. Web arayüzü yok ve dışarıya port açmıyor.

## Bazarr

Downloads subtitles for everything in Sonarr and Radarr.

Setup links Bazarr to Sonarr and Radarr, sets the web login, creates a language profile from `SUBTITLE_LANGUAGES` (default `tr,en`) and makes it the default for shows and movies. It turns on providers that need no account: Embedded Subtitles, turkcealtyazi.org, YIFY Subtitles, SubtitleCat, Subf2m, Gestdown, and TVsubtitles.

Sonarr ve Radarr'daki tüm içerikler için altyazı indiriyor.

Kurulum Bazarr'ı Sonarr ve Radarr'a bağlıyor, web arayüzü girişini ayarlıyor ve `SUBTITLE_LANGUAGES` değerine göre (varsayılan `tr,en`) bir dil profili oluşturup diziler ve filmler için varsayılan yapıyor. Üyelik gerektirmeyen şu altyazı sağlayıcılarını açıyor: Embedded Subtitles, turkcealtyazi.org, YIFY Subtitles, SubtitleCat, Subf2m, Gestdown ve TVsubtitles.

## qBittorrent

The torrent client. Web UI on `QBITTORRENT_WEBUI_PORT`, torrent traffic on `QBITTORRENT_BT_PORT`.

Setup writes the web login before the first start, sets the save path to `/downloads`, creates the `tv`, `movies`, and `music` categories, and stops seeding at ratio 1 so the *arr apps can remove finished torrents.

Torrent istemcisi. Web arayüzü `QBITTORRENT_WEBUI_PORT`, torrent trafiği ise `QBITTORRENT_BT_PORT` üzerinden çalışıyor.

Kurulum, ilk açılıştan önce web arayüzü giriş bilgilerini yazıyor, indirme klasörünü `/downloads` yapıyor ve `tv`, `movies`, `music` kategorilerini oluşturuyor. Paylaşım oranı 1'e ulaşınca seed duruyor; böylece *arr uygulamaları biten torrent'leri kaldırabiliyor.

## Emby

The media server. Plays your library in the browser and in the Emby apps for TV, phone, and tablet. Some features need Emby Premiere.

Setup completes the first-run wizard with your login, creates Movies, Shows, and Music libraries, and creates an API key that the *arr apps use to trigger rescans. Rescans matter on Windows, where Docker bind mounts don't pass file change events to the container.

Medya sunucusu. Kütüphaneni tarayıcıda ve TV, telefon, tablet için Emby uygulamalarında izleyebiliyorsun. Bazı özellikler Emby Premiere gerektiriyor.

Kurulum, ilk kurulum ekranını senin bilgilerinle geçiyor, Movies, Shows ve Music kütüphanelerini oluşturuyor ve *arr uygulamalarının tarama başlatmak için kullandığı bir API anahtarı üretiyor. Bu tarama özellikle Windows'ta önemli, çünkü orada Docker klasöre eklenen yeni dosyaları container'a haber vermiyor.

## Watchtower

Checks for new images every night at 04:30 and updates only the containers of this stack, then removes the old images. Set `WATCHTOWER_NOTIFICATIONS` to get a message when it updates something.

Her gece saat 04:30'da yeni imaj olup olmadığına bakıyor, yalnızca bu stack'teki container'ları güncelliyor ve eski imajları siliyor. Bir güncelleme yapıldığında haberin olsun istiyorsan `WATCHTOWER_NOTIFICATIONS` değerini doldur.

## arr-seed, arr-setup

One-shot helpers that run `setup/bootstrap.py`. `arr-seed` writes config files before the apps start; `arr-setup` connects the apps through their APIs once they're up. Both delete their own containers when every step succeeds. If a step fails, `arr-setup` stays so you can run `docker logs arr-setup`.

`setup/bootstrap.py` script'ini çalıştıran, işi bitince kapanan iki yardımcı container. `arr-seed` uygulamalar açılmadan önce ayar dosyalarını yazıyor, `arr-setup` ise uygulamalar açıldıktan sonra onları API'ler üzerinden birbirine bağlıyor. Tüm adımlar başarılı olursa ikisi de kendini siliyor. Bir adım hata verirse `arr-setup` silinmiyor, `docker logs arr-setup` ile nedenine bakabilirsin.
