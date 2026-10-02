import os
import random
from urllib.parse import urlparse, parse_qs, unquote

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import platform

try:
    from kivy_garden.webview import WebView
except ImportError:
    try:
        from kivy.garden.webview import WebView
    except ImportError:
        WebView = None

SEARCH_ENGINES = {
    "DuckDuckGo": "https://duckduckgo.com/?q=",
    "Яндекс": "https://yandex.ru/search/?text=",
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
}

BLOCKED_DOMAINS = ["yandex.ru", "ya.ru", "yandex.com", "edge.microsoft", "microsoft-edge"]

THEMES = {
    "Чёрная": {"bg": (0.04, 0.04, 0.06, 1), "panel": (0.10, 0.10, 0.18, 1), "accent": (0.91, 0.27, 0.38, 1)},
    "Красная": {"bg": (0.10, 0.0, 0.0, 1), "panel": (0.16, 0.0, 0.0, 1), "accent": (1.0, 0.0, 0.0, 1)},
    "Сталкер": {"bg": (0.10, 0.10, 0.04, 1), "panel": (0.16, 0.16, 0.08, 1), "accent": (0.55, 0.55, 0.0, 1)},
    "Зелёная": {"bg": (0.04, 0.10, 0.04, 1), "panel": (0.06, 0.16, 0.06, 1), "accent": (0.0, 0.80, 0.27, 1)},
    "Синяя": {"bg": (0.04, 0.04, 0.10, 1), "panel": (0.06, 0.06, 0.16, 1), "accent": (0.0, 0.53, 1.0, 1)},
}

VPN_COUNTRIES = {
    "🇩🇪 Германия":   {"code": "DE", "ip": "185.220.101.", "ping": (18, 45)},
    "🇳🇱 Нидерланды": {"code": "NL", "ip": "89.234.157.",  "ping": (22, 55)},
    "🇺🇸 США":        {"code": "US", "ip": "104.244.72.",  "ping": (90, 150)},
    "🇯🇵 Япония":     {"code": "JP", "ip": "103.152.220.", "ping": (120, 200)},
    "🇷🇺 Россия":     {"code": "RU", "ip": "95.163.200.",  "ping": (5, 25)},
    "🇰🇿 Казахстан":  {"code": "KZ", "ip": "178.89.100.",  "ping": (15, 40)},
    "☢️ ЗОНА":        {"code": "UA", "ip": "1986.4.26.",   "ping": (1, 3)},
    "🇬🇩 Гондурас":   {"code": "HN", "ip": "185.42.11.",   "ping": (150, 250)},
}


class SaynrozMobile(BoxLayout):
    vpn_active = BooleanProperty(False)
    current_engine = StringProperty("DuckDuckGo")
    theme_name = StringProperty("Чёрная")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.vpn_country = None
        self.vpn_ip = None
        self.vpn_ping = 0
        self._build_ui()

    def _build_ui(self):
        t = THEMES[self.theme_name]
        Window.clearcolor = t["bg"]

        self.toolbar = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(2), padding=dp(4))

        def mkbtn(text, cb, width=dp(40)):
            b = Button(text=text, size_hint_x=None, width=width,
                       background_color=t["panel"], color=(1, 1, 1, 1), font_size=dp(18))
            b.bind(on_press=cb)
            return b

        self.toolbar.add_widget(mkbtn("←", self.on_back))
        self.toolbar.add_widget(mkbtn("→", self.on_forward))
        self.toolbar.add_widget(mkbtn("↻", self.on_reload))

        self.url_input = TextInput(
            text="saynroz://home", multiline=False,
            background_color=t["bg"], foreground_color=(1, 1, 1, 1),
            cursor_color=t["accent"], font_size=dp(14), padding=[dp(10), dp(12)]
        )
        self.url_input.bind(on_text_validate=self.on_go)
        self.toolbar.add_widget(self.url_input)

        self.toolbar.add_widget(mkbtn("GO", self.on_go, width=dp(50)))
        self.toolbar.add_widget(mkbtn("VPN", self.open_vpn_page, width=dp(60)))
        self.toolbar.add_widget(mkbtn("MENU", self.open_menu, width=dp(70)))

        self.add_widget(self.toolbar)

        if WebView is None:
            self.add_widget(Label(
                text="WebView не установлен.\nНа Android будет работать.",
                halign="center", color=(1, 0.3, 0.3, 1)
            ))
            self.web = None
        else:
            self.web = WebView()
            if hasattr(self.web, "bind"):
                self.web.bind(url=self._on_url_change)
            self.add_widget(self.web)
            Clock.schedule_once(lambda dt: self._load_html(self.get_homepage()), 0.5)

    def on_back(self, *a):
        if self.web and hasattr(self.web, "go_back"):
            try: self.web.go_back()
            except Exception: pass

    def on_forward(self, *a):
        if self.web and hasattr(self.web, "go_forward"):
            try: self.web.go_forward()
            except Exception: pass

    def on_reload(self, *a):
        if self.web and hasattr(self.web, "reload"):
            try: self.web.reload()
            except Exception: pass

    def on_go(self, *a):
        url = self.url_input.text.strip()
        if not url:
            return
        if url.startswith("saynroz://"):
            self._handle_internal(url)
            return
        low = url.lower()
        for d in BLOCKED_DOMAINS:
            if d in low:
                self._load_html(self.blocked_html("ЗАБЛОКИРОВАНО", d + " - ХУЙНЯ!"))
                return
        if " " in url or ("." not in url and not url.startswith("http")):
            full = SEARCH_ENGINES.get(self.current_engine, SEARCH_ENGINES["DuckDuckGo"]) + url.replace(" ", "+")
        else:
            full = url if url.startswith("http") else "https://" + url
        if self.web:
            try:
                self.web.url = full
            except Exception as e:
                print("[NAV ERROR] " + str(e))

    def _handle_internal(self, url):
        if url == "saynroz://home":
            self._load_html(self.get_homepage())
        elif url == "saynroz://vpn":
            self.open_vpn_page()
        elif url == "saynroz://vpn-disconnect":
            self.vpn_disconnect()
        elif url.startswith("saynroz://vpn-connect"):
            qs = parse_qs(urlparse(url).query)
            country = unquote(qs.get("country", [""])[0])
            self.vpn_connect(country)
        elif url == "saynroz://mod":
            self.open_mod_links()
        elif url == "saynroz://news":
            self.open_news()

    def _on_url_change(self, instance, url):
        if url and url.startswith("saynroz://"):
            self._handle_internal(url)
            return
        self.url_input.text = url or ""

    def _load_html(self, html):
        if not self.web:
            return
        if platform == "android":
            try:
                native = self.web._webview if hasattr(self.web, "_webview") else None
                if native:
                    native.loadDataWithBaseURL("saynroz://", html, "text/html", "UTF-8", None)
                    return
            except Exception as e:
                print("[ANDROID HTML ERROR] " + str(e))
        try:
            self.web.load_html(html)
        except AttributeError:
            import base64
            b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
            self.web.url = "data:text/html;base64," + b64

    def open_menu(self, *a):
        box = BoxLayout(orientation="vertical", spacing=dp(6), padding=dp(10))
        t = THEMES[self.theme_name]

        def mk(text, cb):
            b = Button(text=text, size_hint_y=None, height=dp(50),
                       background_color=t["panel"], color=(1, 1, 1, 1))
            b.bind(on_press=lambda x: (cb(), popup.dismiss()))
            box.add_widget(b)

        mk("Домой", lambda: self._load_html(self.get_homepage()))
        mk("Мод ЛЮТЫЕ ПОЦЫ", self.open_mod_links)
        mk("Новости игр", self.open_news)
        mk("VPN", self.open_vpn_page)
        mk("Поисковик: " + self.current_engine, self._cycle_engine)
        mk("Тема: " + self.theme_name, self._cycle_theme)

        popup = Popup(title="Saynroz", content=box, size_hint=(0.9, 0.7))
        popup.open()

    def _cycle_engine(self):
        keys = list(SEARCH_ENGINES.keys())
        i = (keys.index(self.current_engine) + 1) % len(keys)
        self.current_engine = keys[i]

    def _cycle_theme(self):
        keys = list(THEMES.keys())
        i = (keys.index(self.theme_name) + 1) % len(keys)
        self.theme_name = keys[i]
        t = THEMES[self.theme_name]
        Window.clearcolor = t["bg"]

    def get_homepage(self):
        engine_url = SEARCH_ENGINES.get(self.current_engine, SEARCH_ENGINES["DuckDuckGo"])
        if self.vpn_active:
            vpn_badge = '<div class="badge green">VPN: ' + str(self.vpn_country) + ' | ' + str(self.vpn_ip) + '</div>'
        else:
            vpn_badge = '<div class="badge red">VPN выкл</div>'
        return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a0f;color:#fff;font-family:-apple-system,Arial,sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
.container{text-align:center;width:100%;max-width:500px}
.logo{font-size:72px;margin-bottom:10px}
.title{font-size:36px;font-weight:bold;background:linear-gradient(45deg,#e94560,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:6px}
.subtitle{font-size:14px;color:#888;margin-bottom:20px}
.search-box{width:100%;background:#1a1a2e;border:2px solid #e94560;border-radius:25px;padding:14px 20px;font-size:16px;color:#fff;margin-bottom:12px;outline:none}
.badge{display:inline-block;padding:6px 14px;border-radius:15px;font-size:12px;margin:4px 3px}
.green{background:#0f3a1f;border:1px solid #00cc44;color:#00cc44}
.red{background:#2a0a0f;border:1px solid #e94560;color:#e94560}
.shortcuts{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:24px}
.sc{background:#1a1a2e;border:2px solid #e94560;border-radius:12px;padding:18px 10px;color:#fff;text-decoration:none;display:block}
.sc-i{font-size:32px;margin-bottom:8px}
.sc-n{font-size:13px;font-weight:bold}
.footer{color:#555;font-size:11px;margin-top:24px;line-height:1.6}
</style></head><body>
<div class="container">
<div class="logo">SAYNROZ</div>
<div class="title">SAYNROZ</div>
<div class="subtitle">Тёмный. Мощный. Свой.</div>
<input class="search-box" type="text" id="q" placeholder="Поиск или адрес...">
<div>""" + vpn_badge + """<span class="badge" style="background:#1a1a2e;color:#ffd700;border:1px solid #ffd700">""" + self.current_engine + """</span></div>
<div class="shortcuts">
<a class="sc" href="saynroz://vpn"><div class="sc-i">VPN</div><div class="sc-n">VPN</div></a>
<a class="sc" href="saynroz://mod"><div class="sc-i">MOD</div><div class="sc-n">МОД</div></a>
<a class="sc" href="saynroz://news"><div class="sc-i">NEWS</div><div class="sc-n">НОВОСТИ</div></a>
<a class="sc" href="https://www.gog.com"><div class="sc-i">GOG</div><div class="sc-n">GOG</div></a>
</div>
<div class="footer">ГОНИ СЕМКИ. НАЛИВАЙ ЖИГУЛЬ. ГРЫЗИ КИРИЕШКИ.<br>ЮХУ. ТОВАРИЩ.</div>
</div>
<script>
document.getElementById('q').addEventListener('keypress',function(e){
if(e.key==='Enter'){
var v=this.value.trim();if(!v)return;
if(v.indexOf(' ')===-1 && v.indexOf('.')!==-1){
if(v.indexOf('http')!==0)v='https://'+v;
window.location.href=v;
} else {
window.location.href='""" + engine_url + """'+encodeURIComponent(v);
}
}});
</script>
</body></html>"""

    def blocked_html(self, name, message):
        return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#0a0a0f;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;margin:0;text-align:center;padding:20px}
.emoji{font-size:80px}
.title{font-size:28px;color:#e94560;font-weight:bold;margin:16px 0}
.msg{font-size:15px;color:#888;line-height:1.5;white-space:pre-line}
</style></head><body><div>
<div class="emoji">X</div>
<div class="title">""" + name + """</div>
<div class="msg">""" + message + """</div>
</div></body></html>"""

    def open_vpn_page(self, *a):
        cards = ""
        for name, data in VPN_COUNTRIES.items():
            active = "active" if (self.vpn_active and self.vpn_country == name) else ""
            cname = name.split(" ", 1)[1] if " " in name else name
            cards += '<div class="card ' + active + '" onclick="location.href=\'saynroz://vpn-connect?country=' + name + '\'"><div class="cname">' + cname + '</div><div class="code">' + data["code"] + '</div></div>'
        if self.vpn_active:
            status = '<div class="s-on">VPN АКТИВЕН - ' + str(self.vpn_country) + '<br><span class="sm">IP: ' + str(self.vpn_ip) + ' | Ping: ' + str(self.vpn_ping) + 'ms</span><br><button class="dc" onclick="location.href=\'saynroz://vpn-disconnect\'">Отключить</button></div>'
        else:
            status = '<div class="s-off">VPN отключён<br><span class="sm">Выбери страну ниже</span></div>'
        html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#0a0a0f;color:#fff;font-family:Arial;padding:20px;margin:0}
h1{color:#e94560;font-size:26px;margin:0 0 6px}
.sub{color:#888;font-size:13px;margin-bottom:18px}
.s-on{background:linear-gradient(135deg,#0f3a1f,#1a5a2f);border:2px solid #00cc44;border-radius:12px;padding:16px;margin-bottom:16px;font-size:15px;text-align:center}
.s-off{background:#1a1a2e;border:2px solid #e94560;border-radius:12px;padding:16px;margin-bottom:16px;font-size:15px;text-align:center}
.sm{font-size:11px;color:#aaa}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.card{background:#1a1a2e;border:2px solid #333;border-radius:12px;padding:14px;text-align:center;cursor:pointer}
.card.active{border-color:#00cc44;background:#0f2a1a}
.cname{font-size:13px;font-weight:bold}
.code{font-size:10px;color:#888;letter-spacing:2px;margin-top:4px}
.dc{background:#e94560;color:#fff;border:none;border-radius:8px;padding:10px 22px;font-size:14px;font-weight:bold;margin-top:10px}
.foot{color:#555;text-align:center;margin-top:24px;font-size:11px}
</style></head><body>
<h1>SAYNROZ VPN</h1>
<div class="sub">Виртуальный туннель. Пентагон одобряет.</div>
""" + status + """
<div class="grid">""" + cards + """</div>
<div class="foot">AES-256 | Kill Switch | Цена: 0 руб</div>
</body></html>"""
        self._load_html(html)

    def vpn_connect(self, country_name):
        if country_name not in VPN_COUNTRIES:
            return
        data = VPN_COUNTRIES[country_name]
        self.vpn_active = True
        self.vpn_country = country_name
        self.vpn_ip = data["ip"] + str(random.randint(2, 254))
        self.vpn_ping = random.randint(data["ping"][0], data["ping"][1])
        self.open_vpn_page()

    def vpn_disconnect(self):
        self.vpn_active = False
        self.vpn_country = None
        self.vpn_ip = None
        self.vpn_ping = 0
        self.open_vpn_page()

    def open_mod_links(self, *a):
        html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#0a0a0f;color:#fff;font-family:Arial;padding:20px;margin:0}
h1{color:#e94560;font-size:28px;margin:0 0 6px}
.sub{color:#888;font-size:13px;margin-bottom:20px}
a{display:block;background:#1a1a2e;border:2px solid #e94560;border-radius:12px;padding:16px 20px;margin:10px 0;color:#fff;text-decoration:none;font-size:15px;font-weight:bold}
.foot{color:#666;margin-top:24px;text-align:center;font-size:11px;line-height:1.6}
</style></head><body>
<h1>ЛЮТЫЕ ПОЦЫ</h1>
<div class="sub">Мод для S.T.A.L.K.E.R.: Зов Припяти. 18+.</div>
<a href="https://github.com/Saynroz/Lyutye-Potsy-mod-stalker-call-of-pripyat">GitHub (исходник)</a>
<a href="https://falcon-lair.com/files/file/4252-stalker-zov-pripyatilyutye-pocy/">Falcon-Lair (основная)</a>
<a href="https://sharemods.com/lmqqid042bi2/S.T.A.L.K.E.R_Lyutye-Potsy.zip.html">ShareMods (зеркало)</a>
<a href="https://playground.ru/stalker_call_of_pripyat/humor/mod_lyutye_potsy_na_stalker_zov_pripyati-1876226">PlayGround</a>
<a href="https://t.me/saynroz">Telegram</a>
<div class="foot">ГОНИ СЕМКИ. НАЛИВАЙ ЖИГУЛЬ. ГРЫЗИ КИРИЕШКИ.</div>
</body></html>"""
        self._load_html(html)

    def open_news(self, *a):
        html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{background:#0a0a0f;color:#fff;font-family:Arial;padding:20px;margin:0}
h1{color:#e94560;font-size:26px;margin:0 0 6px}
h2{color:#ffd700;font-size:17px;margin:20px 0 8px}
a{color:#e94560;text-decoration:none;font-size:14px;display:block;margin:8px 0;padding:8px 0;border-bottom:1px solid #1a1a2e}
.foot{color:#555;margin-top:24px;text-align:center;font-size:11px}
</style></head><body>
<h1>НОВОСТИ</h1>
<h2>Основные</h2>
<a href="https://stopgame.ru/news">StopGame</a>
<a href="https://dtf.ru/games">DTF</a>
<a href="https://www.igromania.ru/news/">Игромания</a>
<h2>Мировые</h2>
<a href="https://www.pcgamer.com/news/">PC Gamer</a>
<a href="https://www.ign.com/games">IGN</a>
<h2>Сталкер и моды</h2>
<a href="https://ap-pro.ru">AP-PRO</a>
<a href="https://falcon-lair.com">Falcon-Lair</a>
<div class="foot">ЮХУ. ТОВАРИЩ. ДЕГТЯРЁВ ИЗ БУДУЩЕГО.</div>
</body></html>"""
        self._load_html(html)


class SaynrozMobileApp(App):
    def build(self):
        self.title = "Saynroz Browser"
        return SaynrozMobile()


if __name__ == "__main__":
    SaynrozMobileApp().run()