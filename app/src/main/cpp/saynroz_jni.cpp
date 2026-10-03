#include <jni.h>
#include <string>

extern const char* get_canon_quote(int index);
extern bool is_blocked(const std::string& url);

extern "C" {

JNIEXPORT jstring JNICALL
Java_org_saynroz_browser_SaynrozBridge_getCanonQuote(JNIEnv* env, jobject, jint index) {
    return env->NewStringUTF(get_canon_quote(index));
}

JNIEXPORT jboolean JNICALL
Java_org_saynroz_browser_SaynrozBridge_isUrlBlocked(JNIEnv* env, jobject, jstring url) {
    const char* urlStr = env->GetStringUTFChars(url, nullptr);
    bool blocked = is_blocked(std::string(urlStr));
    env->ReleaseStringUTFChars(url, urlStr);
    return blocked ? JNI_TRUE : JNI_FALSE;
}

}