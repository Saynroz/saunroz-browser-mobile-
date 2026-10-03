package org.saynroz.browser

object SaynrozBridge {
    init {
        System.loadLibrary("saynroz")
    }

    external fun getCanonQuote(index: Int): String
    external fun isUrlBlocked(url: String): Boolean
} 