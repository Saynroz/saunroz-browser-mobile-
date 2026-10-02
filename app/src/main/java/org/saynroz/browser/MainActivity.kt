package org.saynroz.browser

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                if (url == null) return false

                if (url.startsWith("saynroz://")) {
                    when {
                        url == "saynroz://home" -> {
                            view?.loadDataWithBaseURL("saynroz://", getHomeHtml(), "text/html", "UTF-8", null)
                        }
                        url == "saynroz://vpn" -> {
                            view?.loadDataWithBaseURL("saynroz://", getVpnHtml(), "text/html", "UTF-8", null)
                        }
                        url.startsWith("saynroz://vpn-connect") -> {
                            val country = url.substringAfter("country=")
                            val result = SaynrozBridge.vpnConnect(country)
                            view?.loadDataWithBaseURL("saynroz://", getVpnHtml(result), "text/html", "UTF-8", null)
                        }
                        else -> return false
                    }
                    return true
                }

                if (SaynrozBridge.isUrlBlocked(url)) {
                    view?.loadDataWithBaseURL("saynroz://", getBlockedHtml(), "text/html", "UTF-8", null)
                    return true
                }

                return false
            }
        }

        webView.loadDataWithBaseURL("saynroz://", getHomeHtml(), "text/html", "UTF-8", null)
    }

    private fun getHomeHtml(): String {
        val quote = SaynrozBridge.getCanonQuote((0..9).random())
        return """
            <!DOCTYPE html>
            <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <style>
                body { background:#0a0a0f; color:#fff; font-family:Arial; text-align:center; padding:40px; }
                h1 { color:#e94560; font-size:36px; }
                .quote { color:#ffd700; font-style:italic; margin:20px 0; }
                a { color:#e94560; display:block; margin:10px; }
            </style></head><body>
            <h1>SAYNROZ</h1>
            <div class="quote">$quote</div>
            <a href="saynroz://vpn">VPN</a>
            <a href="https://github.com/Saynroz">GitHub</a>
            </body></html>
        """.trimIndent()
    }

    private fun getVpnHtml(status: String = ""): String {
        return """
            <!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <style>body { background:#0a0a0f; color:#fff; font-family:Arial; padding:20px; }</style>
            </head><body>
            <h1 style="color:#e94560;">VPN</h1>
            <div style="color:#00cc44;">$status</div>
            <a href="saynroz://vpn-connect?country=DE" style="color:#fff;display:block;padding:15px;background:#1a1a2e;margin:10px 0;">Германия</a>
            <a href="saynroz://vpn-connect?country=RU" style="color:#fff;display:block;padding:15px;background:#1a1a2e;margin:10px 0;">Россия</a>
            <a href="saynroz://vpn-connect?country=UA" style="color:#fff;display:block;padding:15px;background:#1a1a2e;margin:10px 0;">ЗОНА</a>
            </body></html>
        """.trimIndent()
    }

    private fun getBlockedHtml(): String {
        return """
            <!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <style>body { background:#0a0a0f; color:#e94560; text-align:center; padding:100px 20px; font-family:Arial; }</style>
            </head><body>
            <h1>ЗАБЛОКИРОВАНО</h1>
            <p style="color:#888;">ХУЙНЯ!</p>
            </body></html>
        """.trimIndent()
    }
}