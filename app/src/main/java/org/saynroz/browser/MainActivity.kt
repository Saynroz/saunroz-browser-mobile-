package org.saynroz.browser

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.View
import android.view.inputmethod.EditorInfo
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var urlInput: EditText

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Корневой вертикальный layout
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
        }

        // Панель сверху: адресная строка + GO
        val topBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }

        urlInput = EditText(this).apply {
            hint = "Адрес или поиск..."
            setSingleLine()
            setTextColor(0xFFFFFFFF.toInt())
            setHintTextColor(0xFF888888.toInt())
            setBackgroundColor(0xFF1A1A2E.toInt())
            imeOptions = EditorInfo.IME_ACTION_GO
        }
        urlInput.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_GO) {
                loadUrl(urlInput.text.toString())
                true
            } else false
        }

        val goBtn = Button(this).apply {
            text = "GO"
            setBackgroundColor(0xFFE94560.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener { loadUrl(urlInput.text.toString()) }
        }

        topBar.addView(urlInput, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        topBar.addView(goBtn, LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT))

        // Панель навигации снизу
        val navBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }

        val backBtn = Button(this).apply {
            text = "←"
            setBackgroundColor(0xFF1A1A2E.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener { if (webView.canGoBack()) webView.goBack() }
        }
        val fwdBtn = Button(this).apply {
            text = "→"
            setBackgroundColor(0xFF1A1A2E.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener { if (webView.canGoForward()) webView.goForward() }
        }
        val reloadBtn = Button(this).apply {
            text = "↻"
            setBackgroundColor(0xFF1A1A2E.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener { webView.reload() }
        }
        val homeBtn = Button(this).apply {
            text = "⌂"
            setBackgroundColor(0xFF1A1A2E.toInt())
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener { showHomePage() }
        }

        navBar.addView(backBtn, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        navBar.addView(fwdBtn, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        navBar.addView(reloadBtn, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))
        navBar.addView(homeBtn, LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f))

        // WebView
        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                    if (url == null) return false
                    if (url.startsWith("saynroz://")) {
                        if (url == "saynroz://home") {
                            showHomePage()
                            return true
                        }
                        return false
                    }
                    if (SaynrozBridge.isUrlBlocked(url)) {
                        view?.loadDataWithBaseURL("saynroz://", getBlockedHtml(), "text/html", "UTF-8", null)
                        return true
                    }
                    return false
                }
                override fun onPageFinished(view: WebView?, url: String?) {
                    urlInput.setText(url ?: "")
                }
            }
        }

        // Собираем всё
        root.addView(topBar)
        root.addView(webView, LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f))
        root.addView(navBar)

        setContentView(root)

        // Стартовая страница
        showHomePage()
    }

    private fun loadUrl(input: String) {
        var url = input.trim()
        if (url.isEmpty()) return

        if (url.startsWith("saynroz://")) {
            if (url == "saynroz://home") {
                showHomePage()
                return
            }
        }

        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            if (url.contains(" ") || !url.contains(".")) {
                url = "https://duckduckgo.com/?q=" + url.replace(" ", "+")
            } else {
                url = "https://" + url
            }
        }
        webView.loadUrl(url)
    }

    private fun showHomePage() {
        webView.loadDataWithBaseURL("saynroz://", getHomeHtml(), "text/html", "UTF-8", null)
    }

    private fun getHomeHtml(): String {
        val quote = SaynrozBridge.getCanonQuote((0..9).random())
        return """
            <!DOCTYPE html>
            <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <style>
                body { background:#0a0a0f; color:#fff; font-family:Arial; text-align:center; padding:40px; }
                h1 { color:#e94560; font-size:42px; margin-bottom:20px; }
                .quote { color:#ffd700; font-style:italic; margin:30px 0; font-size:16px; }
                .shortcuts { display:flex; justify-content:center; gap:20px; margin-top:30px; }
                .sc { background:#1a1a2e; border:2px solid #e94560; border-radius:12px; padding:20px; color:#fff; text-decoration:none; font-size:14px; font-weight:bold; }
            </style></head><body>
            <h1>SAYNROZ</h1>
            <div class="quote">$quote</div>
            <div class="shortcuts">
                <a class="sc" href="https://duckduckgo.com">Поиск</a>
                <a class="sc" href="https://github.com/Saynroz">GitHub</a>
                <a class="sc" href="https://t.me/saynroz">Telegram</a>
            </div>
            </body></html>
        """.trimIndent()
    }

    private fun getBlockedHtml(): String {
        return """
            <!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
            <style>body { background:#0a0a0f; color:#e94560; text-align:center; padding:100px 20px; font-family:Arial; }</style>
            </head><body><h1>ЗАБЛОКИРОВАНО</h1><p style="color:#888;">ХУЙНЯ!</p></body></html>
        """.trimIndent()
    }
}