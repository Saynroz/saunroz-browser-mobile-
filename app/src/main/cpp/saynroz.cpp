#include <string>
#include <vector>

static const char* CANON_QUOTES[] = {
    "ГОНИ СЕМКИ. НАЛИВАЙ ЖИГУЛЬ. ГРЫЗИ КИРИЕШКИ.",
    "СИДИ У КОСТРА.",
    "ЮХУ. ТОВАРИЩ.",
    "ЛЮТЫЕ ПОЦЫ НЕ УМИРАЮТ. ОНИ ПОХМЕЛЯЮТСЯ.",
    "ДЕГТЯРЁВ ИЗ БУДУЩЕГО.",
    "ПЕТРУШКА УЖЕ ЗДЕСЬ.",
    "ЧЕЛОВЕК ИЗ 1986.",
    "БЕЛАРУСКАЯ МОВА."
};

extern const char* get_canon_quote(int index) {
    if (index < 0 || index > 7) return CANON_QUOTES[0];
    return CANON_QUOTES[index];
}

extern bool is_blocked(const std::string& url) {
    const std::vector<std::string> blocked = {
        "yandex.ru", "ya.ru", "yandex.com",
        "edge.microsoft", "microsoft-edge"
    };
    for (const auto& domain : blocked) {
        if (url.find(domain) != std::string::npos) return true;
    }
    return false;
}