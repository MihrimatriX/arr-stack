"""Hands-off config for the stack. Idempotent: reruns on every `docker compose up` are safe.

`bootstrap.py seed` runs before the apps start and pre-writes their config files (API keys,
qBittorrent login, Bazarr links). `bootstrap.py` (no arg) runs after and wires everything via APIs.
"""
import base64, contextlib, hashlib, http.cookiejar, json, os, re, socket, sys, time
import urllib.error, urllib.parse, urllib.request
from http.client import HTTPConnection

E = os.environ
USER, PASS = E["STACK_USER"], E["STACK_PASSWORD"]
QPORT = int(E["QBITTORRENT_WEBUI_PORT"])
QBIT = f"http://qbittorrent:{QPORT}"
ARRS = {  # app: (internal port, api version, root folder, qBittorrent category)
    "sonarr": (8989, "v3", "/tv", "tv"),
    "radarr": (7878, "v3", "/movies", "movies"),
    "lidarr": (8686, "v1", "/music", "music"),
}
SUB_LANGS = [lang.strip() for lang in E.get("SUBTITLE_LANGUAGES", "tr,en").split(",") if lang.strip()]
SUB_PROVIDERS = ["embeddedsubtitles", "turkcealtyaziorg", "yifysubtitles", "subtitlecat", "subf2m",
                 "gestdown", "tvsubtitles"]  # all work without an account
http = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def call(method, url, body=None, headers=None, form=False):
    headers, data = dict(headers or {}), None
    if body is not None and form:
        data = urllib.parse.urlencode(body).encode()
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
    try:
        with http.open(urllib.request.Request(url, data, headers, method=method), timeout=60) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {url} -> {e.code}: {e.read()[:300].decode(errors='replace')}") from None
    return json.loads(raw) if raw[:1] in (b"{", b"[") else raw.decode()


def wait(url, headers=None):
    for _ in range(300):  # first boot migrations are slow on Windows bind mounts
        with contextlib.suppress(OSError, RuntimeError):
            return call("GET", url, headers=headers)
        time.sleep(2)
    raise RuntimeError(f"timeout waiting for {url}")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    with contextlib.suppress(OSError):  # no-op on Windows bind mounts
        for p in (path, os.path.dirname(path)):
            os.chown(p, int(E["PUID"]), int(E["PGID"]))


def apikey(app):
    """Read the app's key, or pre-seed a config.xml on first boot so we know it up front."""
    path = f"/config/{app}/config.xml"
    if os.path.exists(path):
        return re.search(r"<ApiKey>(\w+)</ApiKey>", open(path).read())[1]
    key = os.urandom(16).hex()
    write(path, f"<Config>\n  <ApiKey>{key}</ApiKey>\n</Config>\n")
    return key


def seed():
    keys = {app: apikey(app) for app in [*ARRS, "prowlarr"]}
    qconf = "/config/qbittorrent/qBittorrent/qBittorrent.conf"
    if not os.path.exists(qconf):
        salt = os.urandom(16)
        pw = hashlib.pbkdf2_hmac("sha512", PASS.encode(), salt, 100_000)
        b64 = lambda b: base64.b64encode(b).decode()
        write(qconf, "[LegalNotice]\nAccepted=true\n\n[Preferences]\n"
                     f"WebUI\\Username={USER}\n"
                     f'WebUI\\Password_PBKDF2="@ByteArray({b64(salt)}:{b64(pw)})"\n')
    bconf = "/config/bazarr/config/config.yaml"
    if not os.path.exists(bconf):  # Bazarr fills in every other default on first boot
        write(bconf, f"auth:\n  type: form\n  username: {USER}\n"
                     f"  password: {hashlib.md5(PASS.encode()).hexdigest()}\n"
                     "general:\n  use_sonarr: true\n  use_radarr: true\n"
                     f"sonarr:\n  ip: sonarr\n  apikey: '{keys['sonarr']}'\n"
                     f"radarr:\n  ip: radarr\n  apikey: '{keys['radarr']}'\n")


def set_fields(schema, values):
    for f in schema["fields"]:
        if f["name"] in values:
            f["value"] = values[f["name"]]
    return schema


def servarr(app, port, ver):
    """API helper for a Servarr app; also sets the web UI login."""
    base, h = f"http://{app}:{port}/api/{ver}", {"X-Api-Key": apikey(app)}
    api = lambda m, p, b=None: call(m, base + p, b, h)
    wait(base + "/system/status", h)
    host = api("GET", "/config/host")
    if host.get("authenticationMethod") != "forms" or host.get("username") != USER:
        host.update(authenticationMethod="forms", authenticationRequired="enabled",
                    username=USER, password=PASS, passwordConfirmation=PASS)
        api("PUT", f"/config/host/{host['id']}", host)
    return api


def qbittorrent():
    wait(QBIT + "/")
    # 4.x answers 200 "Fails.", 5.x answers 401 (raised by call)
    if call("POST", QBIT + "/api/v2/auth/login", {"username": USER, "password": PASS}, form=True) == "Fails.":
        raise RuntimeError("login failed: existing qBittorrent install? put its password in STACK_PASSWORD")
    # stop seeding at ratio 1 so the *arrs can delete the finished torrent instead of keeping a second copy
    prefs = {"save_path": "/downloads", "max_ratio_enabled": True, "max_ratio": 1, "max_ratio_act": 0}
    call("POST", QBIT + "/api/v2/app/setPreferences", {"json": json.dumps(prefs)}, form=True)
    have = call("GET", QBIT + "/api/v2/torrents/categories")
    for *_, cat in ARRS.values():
        if cat not in have:
            call("POST", QBIT + "/api/v2/torrents/createCategory",
                 {"category": cat, "savePath": f"/downloads/{cat}"}, form=True)


def arr(app):
    port, ver, root, cat = ARRS[app]
    api = servarr(app, port, ver)
    if not any(r["path"].rstrip("/") == root for r in api("GET", "/rootfolder")):
        body = {"path": root}
        if ver == "v1":  # Lidarr wants default profiles on the root folder
            body.update(name=cat.title(),
                        defaultQualityProfileId=api("GET", "/qualityprofile")[0]["id"],
                        defaultMetadataProfileId=api("GET", "/metadataprofile")[0]["id"])
        api("POST", "/rootfolder", body)
    if not any(c["implementation"] == "QBittorrent" for c in api("GET", "/downloadclient")):
        dc = next(s for s in api("GET", "/downloadclient/schema") if s["implementation"] == "QBittorrent")
        set_fields(dc, {"host": "qbittorrent", "port": QPORT, "username": USER, "password": PASS})
        for f in dc["fields"]:  # tvCategory / movieCategory / musicCategory / ...
            if f["name"].endswith("Category") and "Imported" not in f["name"]:
                f["value"] = cat
        dc.update(name="qBittorrent", enable=True)
        api("POST", "/downloadclient", dc)


def prowlarr():
    api = servarr("prowlarr", 9696, "v1")
    have = {a["implementation"] for a in api("GET", "/applications")}
    schema = api("GET", "/applications/schema")
    for app, (port, *_) in ARRS.items():
        tpl = next((s for s in schema if s["implementation"].lower() == app), None)
        if tpl and tpl["implementation"] not in have:
            set_fields(tpl, {"prowlarrUrl": "http://prowlarr:9696", "baseUrl": f"http://{app}:{port}",
                             "apiKey": apikey(app)})
            tpl.update(name=tpl["implementation"], syncLevel="fullSync")
            api("POST", "/applications", tpl)
    # FlareSolverr only kicks in for tagged indexers that hit a Cloudflare challenge; tag them all
    tag = next((t["id"] for t in api("GET", "/tag") if t["label"] == "flaresolverr"), None) \
        or api("POST", "/tag", {"label": "flaresolverr"})["id"]
    if not any(p["implementation"] == "FlareSolverr" for p in api("GET", "/indexerProxy")):
        tpl = next(s for s in api("GET", "/indexerProxy/schema") if s["implementation"] == "FlareSolverr")
        set_fields(tpl, {"host": "http://flaresolverr:8191/"})
        tpl.update(name="FlareSolverr", tags=[tag])
        api("POST", "/indexerProxy", tpl)
    wanted = [i.strip().lower() for i in E.get("PROWLARR_INDEXERS", "").split(",") if i.strip()]
    have = {i["definitionName"].lower() for i in api("GET", "/indexer")}
    schema = api("GET", "/indexer/schema") if set(wanted) - have else []
    for name in set(wanted) - have:
        tpl = next((s for s in schema if s["definitionName"].lower() == name), None)
        if not tpl:
            print(f"   unknown indexer '{name}', skipped")
            continue
        tpl.update(enable=True, appProfileId=1, tags=[tag])
        try:
            api("POST", "/indexer", tpl)
        except RuntimeError as e:  # public trackers often fail the connection test (Cloudflare etc.)
            print(f"   indexer '{name}' not added: {e}")


def emby():
    base = "http://emby:8096"
    wait(base + "/System/Info/Public")
    client = 'MediaBrowser Client="arr-setup", Device="arr-setup", DeviceId="arr-setup", Version="1"'
    login = lambda: call("POST", base + "/Users/AuthenticateByName", {"Username": USER, "Pw": PASS},
                         {"X-Emby-Authorization": client})["AccessToken"]
    try:
        token = login()
    except RuntimeError:  # first boot: run the startup wizard
        call("GET", base + "/Startup/User")
        call("POST", base + "/Startup/User", {"Name": USER, "Password": PASS})
        call("POST", base + "/Startup/Complete")
        token = login()
    h = {"X-Emby-Authorization": f'{client}, Token="{token}"'}
    have = {lib["Name"] for lib in call("GET", base + "/Library/VirtualFolders", headers=h)}
    for name, kind, path in (("Movies", "movies", "/movies"), ("Shows", "tvshows", "/tv"), ("Music", "music", "/music")):
        if name not in have:
            q = urllib.parse.urlencode({"name": name, "collectionType": kind, "paths": path, "refreshLibrary": "true"})
            call("POST", f"{base}/Library/VirtualFolders?{q}", {"LibraryOptions": {}}, h)
    # Windows bind mounts don't forward file events, so the *arrs tell Emby to rescan after each import
    keys = lambda: [k["AccessToken"] for k in call("GET", base + "/Auth/Keys", headers=h)["Items"]
                    if k.get("AppName") == "arr-stack"]
    if not keys():
        call("POST", base + "/Auth/Keys?App=arr-stack", {}, h)
    key = keys()[0]
    for app, (port, ver, *_) in ARRS.items():
        api = servarr(app, port, ver)
        if any(n["implementation"] == "MediaBrowser" for n in api("GET", "/notification")):
            continue
        tpl = next(s for s in api("GET", "/notification/schema") if s["implementation"] == "MediaBrowser")
        set_fields(tpl, {"host": "emby", "port": 8096, "apiKey": key, "updateLibrary": True, "notify": False})
        for k, v in list(tpl.items()):  # onDownload, onUpgrade, onRename, on...Delete, onTrackRetag, ...
            if k.startswith("supportsOn") and v and re.search("Download|Upgrade|Rename|Import|Delete|Retag", k):
                tpl["on" + k[len("supportsOn"):]] = True
        tpl["name"] = "Emby"
        api("POST", "/notification", tpl)


def bazarr():
    base = "http://bazarr:6767/api"
    conf = open("/config/bazarr/config/config.yaml").read()
    h = {"X-API-KEY": re.search(r"^auth:\n(?:  .+\n)*?  apikey: '?(\w+)", conf, re.M)[1]}
    post = lambda form: call("POST", base + "/system/settings", form, h, form=True)
    if not wait(base + "/system/settings", h)["general"]["enabled_providers"]:
        post([("settings-general-enabled_providers", p) for p in SUB_PROVIDERS]
             + [("settings-subf2m-user_agent", "Mozilla/5.0")])
    if not call("GET", base + "/system/languages/profiles", headers=h):
        items = [{"id": i, "language": lang, "hi": "False", "forced": "False", "audio_exclude": "False",
                  "audio_only_include": "False"} for i, lang in enumerate(SUB_LANGS, 1)]
        profile = {"profileId": 1, "name": "+".join(SUB_LANGS), "cutoff": 1, "items": items,
                   "mustContain": [], "mustNotContain": [], "originalFormat": False, "tag": None}
        post([*(("languages-enabled", lang) for lang in SUB_LANGS), ("languages-profiles", json.dumps([profile])),
              *((f"settings-general-{k}_default_{f}", v) for k in ("serie", "movie")
                for f, v in (("enabled", "true"), ("profile", "1")))])


def seerr():
    base = "http://seerr:5055/api/v1"
    if wait(base + "/settings/public")["initialized"]:
        return
    # first Emby login becomes the Seerr admin; the session cookie authorizes the calls below
    call("POST", base + "/auth/jellyfin", {"username": USER, "password": PASS, "hostname": "emby", "port": 8096,
                                           "useSsl": False, "urlBase": "", "email": f"{USER}@local", "serverType": 3})
    for lib in call("POST", base + "/settings/jellyfin/library/sync"):
        call("PUT", f"{base}/settings/jellyfin/library/{lib['id']}", {"enabled": True})
    for app in ("radarr", "sonarr"):
        port, ver, root, _ = ARRS[app]
        profile = servarr(app, port, ver)("GET", "/qualityprofile")[0]
        body = dict(name=app.title(), hostname=app, port=port, apiKey=apikey(app), useSsl=False, baseUrl="",
                    activeProfileId=profile["id"], activeProfileName=profile["name"], activeDirectory=root,
                    is4k=False, isDefault=True, syncEnabled=True, preventSearch=False, tags=[], externalUrl="")
        if app == "radarr":
            body["minimumAvailability"] = "released"
        else:
            body.update(seriesType="standard", animeSeriesType="anime", activeAnimeProfileId=profile["id"],
                        activeAnimeDirectory=root, animeTags=[], enableSeasonFolders=True)
        call("POST", f"{base}/settings/{app}", body)
    call("POST", base + "/settings/initialize")


def remove_containers(*names):
    """Delete finished one-shot containers so they don't linger in Docker Desktop."""
    class Docker(HTTPConnection):
        def connect(self):
            self.sock = socket.socket(socket.AF_UNIX)
            self.sock.connect("/var/run/docker.sock")
    for name in names:
        with contextlib.suppress(OSError):  # deleting our own container kills us mid-request
            conn = Docker("localhost")
            conn.request("DELETE", f"/containers/{name}?force=true")
            conn.getresponse()


def main():
    if sys.argv[1:] == ["seed"]:
        return seed()
    steps = [("qbittorrent", qbittorrent), *((a, lambda a=a: arr(a)) for a in ARRS),
             ("prowlarr", prowlarr), ("bazarr", bazarr), ("emby", emby), ("seerr", seerr)]
    failed = []
    for name, fn in steps:  # one broken app must not block the rest
        print(f"-> {name}", flush=True)
        try:
            fn()
        except Exception as e:
            print(f"!! {name}: {e}", flush=True)
            failed.append(name)
    print(f"done, failed: {', '.join(failed)}" if failed else "done", flush=True)
    if not failed:  # on failure keep arr-setup around so `docker logs arr-setup` shows what broke
        remove_containers("arr-seed", "arr-setup")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
