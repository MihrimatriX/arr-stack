# 🎬 Complete Media Automation Stack

A comprehensive Docker-based media automation stack that provides a complete solution for managing, downloading, organizing, and streaming your media collection. This stack combines the power of the *arr ecosystem with media servers and management tools to create a fully automated media center.

## 🌟 What This Stack Does

This stack automates the entire media lifecycle:
- **Discovery**: Find and track movies, TV shows, music, and books
- **Download**: Automatically download content based on your preferences
- **Organization**: Sort and rename files according to your standards
- **Streaming**: Serve media to all your devices
- **Management**: Monitor, request, and maintain your collection

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discovery     │    │   Download      │    │   Organization  │
│                 │    │                 │    │                 │
│ • Overseerr     │───▶│ • qBittorrent   │───▶│ • *arr Apps     │
│ • Prowlarr      │    │ • Indexers      │    │ • Bazarr        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streaming     │    │   Management    │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • Jellyfin      │    │ • Homarr        │    │ • Tautulli      │
│ • Plex          │    │ • Portainer     │    │ • Jellystat     │
│ • Navidrome     │    │ • Watchtower    │    │ • Audiobookshelf│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Services Included

### 📺 Content Management (*arr Ecosystem)
- **[Sonarr](https://sonarr.tv/)** - TV show collection manager
- **[Radarr](https://radarr.video/)** - Movie collection manager  
- **[Lidarr](https://lidarr.audio/)** - Music collection manager
- **[Readarr](https://readarr.com/)** - Book and audiobook manager
- **[Prowlarr](https://prowlarr.com/)** - Indexer manager for all *arr apps
- **[Bazarr](https://www.bazarr.media/)** - Subtitle manager

### 🎬 Media Servers
- **[Jellyfin](https://jellyfin.org/)** - Free, open-source media server
- **[Plex](https://www.plex.tv/)** - Popular media server with extensive device support
- **[Navidrome](https://www.navidrome.org/)** - Lightweight music server
- **[Audiobookshelf](https://www.audiobookshelf.org/)** - Audiobook server

### 🛠️ Management & Automation
- **[Homarr](https://homarr.dev/)** - Unified dashboard for all services
- **[Overseerr](https://overseerr.dev/)** - Request management and discovery
- **[qBittorrent](https://www.qbittorrent.org/)** - Torrent client
- **[Recyclarr](https://recyclarr.dev/)** - Quality profile synchronization
- **[Portainer](https://www.portainer.io/)** - Docker container management
- **[Watchtower](https://containrrr.dev/watchtower/)** - Automatic container updates

### 📊 Monitoring & Analytics
- **[Tautulli](https://tautulli.com/)** - Plex monitoring and analytics
- **[Jellystat](https://github.com/Fallenbagel/jellystat)** - Jellyfin analytics

## 🎯 Key Features

- **🔄 Fully Automated**: Set it up once and let it manage your entire media collection
- **🌐 Multi-Platform**: Works on Windows, macOS, and Linux
- **📱 Device Agnostic**: Stream to any device with a web browser or app
- **🔒 Self-Hosted**: Complete control over your data and privacy
- **⚡ High Performance**: Optimized for speed and efficiency
- **🛡️ Secure**: All services run in isolated containers
- **📈 Scalable**: Easy to add more storage or services as needed

## 🚀 Quick Start

### Prerequisites
- Docker Desktop with WSL2 backend (Windows) or Docker Engine (Linux/macOS)
- At least 4GB RAM and 20GB free disk space
- Basic understanding of Docker and networking

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/arr-stack.git
   cd arr-stack
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start the stack**
   ```bash
   docker compose up -d
   ```

4. **Access services**
   - Dashboard: http://localhost:7575 (Homarr)
   - TV Shows: http://localhost:8989 (Sonarr)
   - Movies: http://localhost:7878 (Radarr)
   - Music: http://localhost:8686 (Lidarr)
   - Books: http://localhost:8787 (Readarr)
   - Media Server: http://localhost:8096 (Jellyfin)

## 📁 Directory Structure

```
arr-stack/
├── config/                 # Service configurations
│   ├── homarr/            # Dashboard settings
│   ├── sonarr/            # TV show manager
│   ├── radarr/            # Movie manager
│   ├── lidarr/            # Music manager
│   ├── readarr/           # Book manager
│   ├── prowlarr/          # Indexer manager
│   ├── bazarr/            # Subtitle manager
│   ├── jellyfin/          # Media server
│   ├── plex/              # Alternative media server
│   ├── qbittorrent/       # Torrent client
│   ├── portainer/         # Container management
│   └── ...
├── downloads/             # Download directory
├── media/                 # Organized media files
│   ├── movies/           # Movie collection
│   ├── tv/               # TV show collection
│   ├── music/            # Music collection
│   ├── books/            # Book collection
│   └── audiobooks/       # Audiobook collection
├── docker-compose.yml     # Service definitions
├── .env                   # Environment variables
└── README.md             # This file
```

## ⚙️ Configuration

### Environment Variables
Key variables in `.env`:

```bash
# User and Timezone
PUID=1000
PGID=1000
TZ=Europe/Istanbul

# Service Ports
HOMARR_PORT=7575
SONARR_PORT=8989
RADARR_PORT=7878
LIDARR_PORT=8686
READARR_PORT=8787
PROWLARR_PORT=9696
BAZARR_PORT=6767
QBITTORRENT_WEBUI_PORT=8080
JELLYFIN_HTTP_PORT=8096
PLEX_HTTP_PORT=32400

# Directory Paths
CONFIG_ROOT=./config
MEDIA_MOVIES_DIR=./media/movies
MEDIA_TV_DIR=./media/tv
MEDIA_MUSIC_DIR=./media/music
MEDIA_BOOKS_DIR=./media/books
DOWNLOADS_ROOT=./downloads

# Optional
PLEX_CLAIM=                    # Get from plex.tv/claim
WATCHTOWER_NOTIFICATIONS=      # Discord/Slack webhook URL
```

### Initial Setup Workflow

1. **Configure qBittorrent**
   - Change default password
   - Set download categories
   - Configure download paths

2. **Setup Indexers in Prowlarr**
   - Add your preferred indexers
   - Configure API keys
   - Sync with *arr applications

3. **Configure *arr Applications**
   - Add download clients (qBittorrent)
   - Set root folders for media
   - Configure quality profiles
   - Add indexers from Prowlarr

4. **Setup Media Servers**
   - Create libraries pointing to media folders
   - Configure metadata agents
   - Set up user accounts

5. **Configure Dashboard**
   - Add service widgets to Homarr
   - Set up API integrations
   - Customize layout and themes

## 🔧 Advanced Configuration

### Custom Quality Profiles
Use Recyclarr to maintain consistent quality profiles across all *arr applications:

```yaml
# config/recyclarr/config.yml
sonarr:
  instance_name: sonarr
  base_url: http://sonarr:8989
  api_key: your_api_key
  quality_definition:
    type: series
    quality_profiles:
      - name: "HD-1080p"
        upgrade_until_quality: "Bluray-1080p"
        qualities:
          - "HDTV-1080p"
          - "Bluray-1080p"
```

### Automated Updates
Watchtower automatically updates containers. Configure notifications:

```bash
WATCHTOWER_NOTIFICATIONS=discord://webhook_url
```

### Backup Strategy
Regular backups of the `config/` directory ensure you can restore your setup:

```bash
# Create backup
tar -czf arr-stack-backup-$(date +%Y%m%d).tar.gz config/

# Restore backup
tar -xzf arr-stack-backup-20240101.tar.gz
```

## 🛠️ Troubleshooting

### Common Issues

**Services won't start**
- Check Docker is running
- Verify port conflicts
- Check disk space

**Downloads not working**
- Verify qBittorrent configuration
- Check indexer connectivity
- Review download client settings in *arr apps

**Media not appearing**
- Check file permissions
- Verify folder mappings
- Review media server library settings

**Performance issues**
- Monitor resource usage
- Adjust quality profiles
- Consider hardware transcoding

### Logs and Debugging

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f sonarr

# Check service status
docker compose ps

# Restart specific service
docker compose restart sonarr
```

## 🔒 Security Considerations

- **Network Security**: Services are exposed on localhost by default
- **Authentication**: Set strong passwords for all services
- **Updates**: Keep containers updated with Watchtower
- **Backups**: Regular backups of configuration data
- **Access Control**: Use reverse proxy for external access

## 📈 Performance Optimization

### Hardware Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 100GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 1TB+ storage
- **Optimal**: 16GB+ RAM, 8+ CPU cores, SSD storage

### Optimization Tips
- Use SSD storage for better I/O performance
- Enable hardware transcoding if supported
- Configure appropriate quality profiles
- Monitor resource usage and scale accordingly

## 🙏 Acknowledgments

- [LinuxServer.io](https://www.linuxserver.io/) for excellent Docker images
- [Hotio](https://hotio.dev/) for additional container images
- All the developers of the amazing *arr ecosystem
- The open-source community for continuous improvements
