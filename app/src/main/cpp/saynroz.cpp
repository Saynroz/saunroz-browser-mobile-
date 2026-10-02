#include <string>
#include <vector>
#include <cstdlib>

static const char* CANON_QUOTES[] = {
    "ЛЮТЫЕ ПОЦЫ НЕ УМИРАЮТ. ОНИ ПОХМЕЛЯЮТСЯ.",
    "ГОНИ СЕМКИ. НАЛИВАЙ ЖИГУЛЬ. ГРЫЗИ КИРИЕШКИ.",
    "ТЫ ФРАЕР? - НЕТ. - ГОНИ СЕМКИ.",
    "ПЕТРУШКА УЖЕ ЗДЕСЬ.",
    "ОЛЕГ ПРОРОК ХОЧЕТ СЪЕСТЬ ВСЕЛЕННУЮ 02.",
    "ДЕГТЯРЁВ ИЗ БУДУЩЕГО. ИЗ СТАЛКЕРА 2.",
    "ЮХУ. ТОВАРИЩ. ЧЕЛОВЕК ИЗ 1986.",
    "СЕМКИ, ЖИГУЛЬ, КИРИЕШКИ - ТРИ ВРЕМЕННЫХ ЯКОРЯ.",
    "ТЕБЕ РАСПОРОЛИ КИШКИ. ОХХ ПИЗДЕЦ.",
    "ОДНОНОГИЙ ВСЕГДА УСКАКИВАЕТ."
};

const char* get_canon_quote(int index) {
    if (index < 0 || index > 9) return CANON_QUOTES[0];
    return CANON_QUOTES[index];
}

struct VpnCountry {
    std::string name;
    std::string code;
    std::string ip;
    int ping_min;
    int ping_max;
};

static std::vector<VpnCountry> VPN_COUNTRIES = {
    {"Германия", "DE", "185.220.101.", 18, 45},
    {"Нидерланды", "NL", "89.234.157.", 22, 55},
    {"США", "US", "104.244.72.", 90, 150},
    {"Япония", "JP", "103.152.220.", 120, 200},
    {"Россия", "RU", "95.163.200.", 5, 25},
    {"Казахстан", "KZ", "178.89.100.", 15, 40},
    {"ЗОНА", "UA", "1986.4.26.", 1, 3},
    {"Гондурас", "HN", "185.42.11.", 150, 250},
};

std::string generate_vpn_ip(const std::string& prefix) {
    int last_octet = 2 + (rand() % 252);
    return prefix + std::to_string(last_octet);
}

std::string vpn_connect(const std::string& country_code) {
    for (const auto& country : VPN_COUNTRIES) {
        if (country.code == country_code) {
            std::string ip = generate_vpn_ip(country.ip);
            return "VPN АКТИВЕН: " + country.name + " | IP: " + ip;
        }
    }
    return "ОШИБКА: неизвестная страна";
}

bool is_blocked(const std::string& url) {
    const std::vector<std::string> blocked = {
        "yandex.ru", "ya.ru", "yandex.com",
        "edge.microsoft", "microsoft-edge"
    };
    for (const auto& domain : blocked) {
        if (url.find(domain) != std::string::npos) return true;
    }
    return false;
}

std::string get_search_url(const std::string& engine, const std::string& query) {
    if (engine == "Яндекс") return "https://yandex.ru/search/?text=" + query;
    if (engine == "Google") return "https://www.google.com/search?q=" + query;
    if (engine == "Bing") return "https://www.bing.com/search?q=" + query;
    return "https://duckduckgo.com/?q=" + query;
}