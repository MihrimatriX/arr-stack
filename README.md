# arr-stack

[Türkçe](README-TR.md) · [Project page](https://mihrimatrix.github.io/arr-stack/) · [Service details](SERVICES.md)

A Docker Compose setup for a home media server. You add a movie, show, or album you want. The stack searches for it, downloads it, grabs subtitles, renames the files, and puts them in a library you can watch from any device.

What sets this repo apart is the setup. These apps usually take an evening of clicking through web UIs to connect to each other. Here a small Python script does that wiring on the first `docker compose up`, so you start with a working system.

## How it works

```
 Seerr ──request──▶ Sonarr / Radarr / Lidarr ──search──▶ Prowlarr ──▶ indexers
                           │                                (FlareSolverr for Cloudflare)
                           ▼
                      qBittorrent ──download──▶ /downloads
                           │
                           ▼
              /media/movies, /media/tv, /media/music ──▶ Emby ──▶ your TV, phone, browser
                           ▲
                        Bazarr (subtitles)
```

1. You ask for something in Seerr, or add it directly in Sonarr (TV), Radarr (movies), or Lidarr (music).
2. That app asks Prowlarr to search the indexers, then sends the best match to qBittorrent.
3. When the download finishes, the app moves and renames the file into `media/`, and tells Emby to rescan.
4. Bazarr finds subtitles for new movies and episodes.
5. Homarr gives you one page with links to everything and a release calendar.

## Services

| Service | What it does | Port |
|---|---|---|
| [Homarr](https://homarr.dev/) | Dashboard with every app and a calendar | 7575 |
| [Seerr](https://github.com/seerr-team/seerr) | Request page for movies and shows, signs in with your Emby account | 5055 |
| [Sonarr](https://sonarr.tv/) | Tracks TV shows and grabs new episodes | 8989 |
| [Radarr](https://radarr.video/) | Tracks movies | 7878 |
| [Lidarr](https://lidarr.audio/) | Tracks music artists and albums | 8686 |
| [Prowlarr](https://prowlarr.com/) | Manages indexers and shares them with the apps above | 9696 |
| [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) | Gets Prowlarr past Cloudflare checks on some indexers | internal |
| [Bazarr](https://www.bazarr.media/) | Downloads subtitles | 6767 |
| [qBittorrent](https://www.qbittorrent.org/) | Torrent client | 8080 |
| [Emby](https://emby.media/) | Media server and player apps (some features need Emby Premiere) | 8096 |
| [Watchtower](https://github.com/nicholas-fedor/watchtower) | Updates this stack's containers every night at 04:30 | none |

## What gets set up for you

Two one-shot containers run `setup/bootstrap.py`.

`arr-seed` runs before the apps start. It writes API keys for the *arr apps, the qBittorrent login, and Bazarr's links to Sonarr and Radarr.

`arr-setup` runs after the apps are up and connects them through their APIs:

- Every web UI gets the same login, `STACK_USER` / `STACK_PASSWORD`.
- qBittorrent gets `tv`, `movies`, and `music` categories and stops seeding at ratio 1, so the apps can clean up finished torrents.
- Sonarr, Radarr, and Lidarr get their media folders and qBittorrent as the download client.
- Prowlarr is linked to all three, adds the indexers from `PROWLARR_INDEXERS`, and routes them through FlareSolverr.
- Bazarr turns on subtitle providers that need no account and uses the languages in `SUBTITLE_LANGUAGES`.
- Emby finishes its first-run wizard and gets Movies, Shows, and Music libraries. The *arr apps tell Emby to rescan after each import.
- Seerr connects to Emby, Radarr, and Sonarr.
- Homarr gets an owner account and a board with a tile for each app.

When everything succeeds, both setup containers delete themselves. If a step fails, the others still run and `arr-setup` stays so you can read `docker logs arr-setup`. Running `docker compose up -d` again is safe; the script skips anything already in place.

## Quick start

You need Docker (Docker Desktop on Windows or macOS, Docker Engine on Linux) and a few GB of free RAM.

```bash
git clone https://github.com/MihrimatriX/arr-stack.git
cd arr-stack
cp .env.example .env
```

Open `.env` and at least change `STACK_PASSWORD`. Then:

```bash
docker compose up -d
docker logs -f arr-setup   # wait for "done"
```

The first boot takes a few minutes. After that, open Homarr at http://localhost:7575 and sign in with your `STACK_USER` and `STACK_PASSWORD`. Homarr requires a symbol in the password, so if yours has none, the script adds `!` to the end for Homarr only.

## Settings in `.env`

| Variable | Meaning |
|---|---|
| `PUID`, `PGID` | User and group that own the files (Linux) |
| `TZ` | Time zone, for example `Europe/Istanbul` |
| `*_PORT` | Port each app uses on your machine |
| `CONFIG_ROOT` | Where app settings live (`./config`) |
| `MEDIA_MOVIES_DIR`, `MEDIA_TV_DIR`, `MEDIA_MUSIC_DIR` | Library folders |
| `DOWNLOADS_ROOT` | Download folder |
| `STACK_USER`, `STACK_PASSWORD` | One login for all web UIs |
| `PROWLARR_INDEXERS` | Indexers to add, comma separated. Leave empty to skip |
| `SUBTITLE_LANGUAGES` | Subtitle languages, the first one is preferred. Default `tr,en` |
| `WATCHTOWER_NOTIFICATIONS` | Optional notification URL, for example a Discord webhook |

## Folders

```
arr-stack/
├── docker-compose.yml   # all services
├── .env.example         # copy to .env
├── setup/bootstrap.py   # first-run wiring
├── config/              # app settings (not in git)
├── downloads/           # in-progress and finished downloads
└── media/
    ├── movies/
    ├── tv/
    └── music/
```

`config/`, `downloads/`, `media/`, and `.env` are in `.gitignore`. To back up your setup, copy `config/` and `.env`:

```bash
tar -czf arr-stack-backup-$(date +%Y%m%d).tar.gz config/ .env
```

## Troubleshooting

```bash
docker compose ps              # what is running
docker logs arr-setup          # why setup failed, if it did
docker compose logs -f sonarr  # one app's logs
docker compose restart sonarr
```

If qBittorrent login fails during setup, you probably have an old qBittorrent config in `config/qbittorrent`. Put its password in `STACK_PASSWORD`, or delete that folder and start again.

If a file finishes downloading but never shows up in Emby, check that the folder paths in `.env` exist and that Docker can write to them.

## Notes

The apps listen on every network interface of the host, so other devices on your LAN can reach them. Homarr tiles link to `localhost`; edit the tiles if you use the board from another device. Don't expose these ports to the internet without a reverse proxy and HTTPS.

Only download content you have the right to download.

Container images come from [LinuxServer.io](https://www.linuxserver.io/) and the projects listed above.
