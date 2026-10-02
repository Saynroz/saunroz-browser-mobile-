#include <jni.h>
#include <string>

// Объявления функций из saynroz.cpp
extern const char* get_canon_quote(int index);
extern std::string vpn_connect(const std::string& country_code);
extern bool is_blocked(const std::string& url);
extern std::string get_search_url(const std::string& engine, const std::string& query);

extern "C" {

JNIEXPORT jstring JNICALL
Java_org_saynroz_browser_SaynrozBridge_getCanonQuote(JNIEnv* env, jobject, jint index) {
    return env->NewStringUTF(get_canon_quote(index));
}

JNIEXPORT jstring JNICALL
Java_org_saynroz_browser_SaynrozBridge_vpnConnect(JNIEnv* env, jobject, jstring countryCode) {
    const char* code = env->GetStringUTFChars(countryCode, nullptr);
    std::string result = vpn_connect(std::string(code));
    env->ReleaseStringUTFChars(countryCode, code);
    return env->NewStringUTF(result.c_str());
}

JNIEXPORT jboolean JNICALL
Java_org_saynroz_browser_SaynrozBridge_isUrlBlocked(JNIEnv* env, jobject, jstring url) {
    const char* urlStr = env->GetStringUTFChars(url, nullptr);
    bool blocked = is_blocked(std::string(urlStr));
    env->ReleaseStringUTFChars(url, urlStr);
    return blocked ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jstring JNICALL
Java_org_saynroz_browser_SaynrozBridge_getSearchUrl(JNIEnv* env, jobject, jstring engine, jstring query) {
    const char* eng = env->GetStringUTFChars(engine, nullptr);
    const char* q = env->GetStringUTFChars(query, nullptr);
    std::string result = get_search_url(std::string(eng), std::string(q));
    env->ReleaseStringUTFChars(engine, eng);
    env->ReleaseStringUTFChars(query, q);
    return env->NewStringUTF(result.c_str());
}

}