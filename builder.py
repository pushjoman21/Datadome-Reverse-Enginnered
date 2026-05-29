"""
If U SKID Please give me creds xd
"""

import json
import math
import random
import time
import hashlib
import struct
from collections import OrderedDict


# ─── DJB2 hash (matches tags.js S() function, line 1170) ───

def djb2_hash(s):
    """
    S = function(n) {
      for (var t=0, c=0, e=n.length; c<e;)
        t = (t << 5) - t + n.charCodeAt(c++) | 0;
      return t + 2147483647 + 1;
    }
    """
    t = 0
    for ch in s:
        t = ((t << 5) - t + ord(ch)) & 0xFFFFFFFF
        if t >= 0x80000000:
            t -= 0x100000000
    return t + 2147483648


# ─── Browser profiles ───

CHROME_WIN10_PROFILE = {
    "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "pf": "Win32",
    "hc": 8,
    "dvm": 8,
    "mob": False,
    "ts_mtp": 0,
    "wbd": False,
    "lg": "en-US",
    "lgs": '["en-US","en"]',
    "vnd": "Google Inc.",
    "bid": "NA",
    "glvd": "Google Inc. (NVIDIA)",
    "glrd": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 (0x00002484) Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "rs_w": 1920,
    "rs_h": 1080,
    "rs_cd": 24,
    "ars_w": 1920,
    "ars_h": 1040,
    "br_oh": 1040,
    "br_ow": 1920,
    "br_w": 1920,
    "br_h": 929,
    "br_iw": 1920,
    "br_ih": 929,
    "pr": 1,
    "cg_w": 1920,
    "cg_h": 0,
    "sg_w": 0,
    "sg_h": 48,
    "so": "landscape-primary",
    "plu": "PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF",
    "plg": 5,
    "plgne": True,
    "plgre": True,
    "plgof": False,
    "plggt": False,
    "plgod": False,
    "mmt": "application/pdf,text/pdf",
    "med": "defined",
    "tz": -60,
    "k_lyts": 48,
    "k_lytk": "qwertyuiopasdfghjklzxcvbnm1234567890-=[];'#,./\\` ",
    "nhi": "x86,64,false,,Windows,14.0.0,148.0.7778.179,false",
    "eva": 40,
    "cokys": ",loadTimes,csi,app,runtime",
    "stqe": 10737418240,
    "stqu": 0,
    "cssS": "4.93,13.26,9.01,0.22,4.57,2.12,14.38,6.39,7.07",
    "css0": "33, 4, 4",
    "css1": "0.218751, 0.0134708, -0.0191417, 0.00133113, -0.160945, 4.09828, 1.04485, -0.0726597, 0.28419, -1.99897, 1.84097, -0.128023, 4.08665, -28.7452, 26.4731, -0.840966",
    "cssH": "0px",
    "csssp": "",
    "niet": "4g",
    "nid": 10,
    "nisd": False,
    "nt_nhp": "h2",
}

CHROME_WIN10_PROFILE_DE = {
    **CHROME_WIN10_PROFILE,
    "lg": "de-DE",
    "lgs": '["de-DE","de","en-US","en"]',
    "tz": -120,
    "k_lyts": 48,
    "k_lytk": "kg20va^l<Ã¤w8mh.71pdfoqcnÃ¼yz365x-#,ÃŸ4bt9siuÂ´jÃ¶r+e",
    "glvd": "Google Inc. (NVIDIA)",
    "glrd": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 (0x00001B80) Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "hc": 8,
    "dvm": 32,
    "rs_w": 2560,
    "rs_h": 1440,
    "rs_cd": 32,
    "ars_w": 2560,
    "ars_h": 1392,
    "br_oh": 1392,
    "br_ow": 2560,
    "cg_w": 1711,
    "cg_h": 87,
    "br_w": 849,
    "br_h": 1305,
    "br_iw": 849,
    "br_ih": 1305,
}

PROFILES = {
    "chrome_win10": CHROME_WIN10_PROFILE,
    "chrome_win10_de": CHROME_WIN10_PROFILE_DE,
}


# ─── bchk API list (from tags.js line 1913) ───

BCHK_APIS = [
    "AppBannerPromptResult", "webkitRTCPeerConnection", "webkitAudioContext",
    "webkitRequestAnimationFrame", "chrome.runtime", "chrome.webstore",
    "console.context", "InputMethodContext", "SVGAnimationElement",
    "SVGPathSegList", "PasswordCredential", "ViewTransition",
    "VisualViewport.prototype.segments", "DeprecationReportBody",
    "MathMLElement", "opr", "CSS2Properties.prototype.colorScheme",
    "WebKitCSSMatrix", "SVGTextPositioningElement",
    "XMLHttpRequestEventTarget", "TextDecoderStream", "onloadend",
    "WritableStream", "TransformStream", "TextTrackCue", "WeakRef",
    "VisualViewport", "StyleSheet", "RTCDtlsTransport", "Atomics",
    "StaticRange", "UIEvent", "VideoStreamTrack", "OfflineResourceList",
    "SVGGeometryElement", "RTCDataChannel", "VTTRegion", "AbortController",
    "Controllers", "onanimationcancel", "SVGDocument", "IIRFilterNode",
    "RTCStatsReport", "MediaStreamTrack",
    "CSS2Properties.prototype.MozOsxFontSmoothing", "CropTarget",
    "BatteryManager", "LaunchQueue", "CSSFontPaletteValuesRule",
    "PushSubscriptionOptions", "DOMSettableTokenList", "RTCTrackEvent",
    "MozSmsMessage", "ServiceWorkerContainer",
    "CanvasCaptureMediaStream", "DeviceStorage", "XPathNSResolver",
    "SmartCardEvent", "WeakSet", "MozMobileMessageManager",
    "External.prototype.getHostEnvironmentValue", "WindowUtils",
    "XPathNamespace", "SVGFEDropShadowElement", "SharedWorker",
    "WorkerMessageEvent", "CSS2Properties.prototype.MozOSXFontSmoothing",
    "AudioSinkInfo", "Notification.prototype.image",
    "ContentVisibilityAutoStateChangeEvent",
    "PerformanceResourceTiming.prototype.renderBlockingStatus",
    "console.createTask", "PerformanceServerTiming", "CanvasFilter",
    "structuredClone", "onslotchange", "EyeDropper", "URLPattern",
    "VideoFrame", "WritableStreamDefaultController", "SharedArrayBuffer",
    "CSSCounterStyleRule", "CustomStateSet",
    "ReadableStreamDefaultController",
    "XMLDocument.prototype.hasStorageAccess", "CryptoKey", "SubmitEvent",
    "MediaMetadata", "VideoPlaybackQuality",
    "ReadableStreamDefaultReader", "UserActivation", "FragmentDirective",
    "WebKitMediaKeyError", "RTCRtpTransceiver.prototype.stop",
    "Scheduling", "EventCounts", "VideoTrackList", "SourceBuffer",
    "RTCError", "FontFaceSet", "CSSCharsetRule", "MediaDeviceInfo",
    "RTCPeerConnectionIceErrorEvent", "RTCSctpTransport",
    "MediaSessionCoordinator", "XULPopupElement", "MediaSourceHandle",
    "RTCEncodedAudioFrame", "__REACT_DEVTOOLS_GLOBAL_HOOK__",
    "ShadowRealm", "HTMLSlotElement", "DetachedViewControlEvent",
    "GeolocationPosition", "SiteBoundCredential", "MediaSource",
    "WebTransport", "GPUSupportedLimits", "ToggleEvent",
]

BCHK_FOUND  = "52738db37a1ea50137e79e8181193ac872cd325ba5cacfbe7aab5b36b9c9879e7c0018dbd31a1832a8dc6528387b67451719dcd8b784a518904e3f07c69b9d30"
BCHK_ABSENT = "3829ae9642df0d791e41d2159da28bd18d056afadf1bd70fc9222a473eaf58e860ff950e7bf35b66e4aa90b156c80c96913dbd9c23c7262e4adbc3ddd77ff263"

# Chrome 148 on Windows — which APIs exist
CHROME_148_APIS_PRESENT = {
    "webkitRTCPeerConnection",
    "webkitRequestAnimationFrame", "chrome.runtime",
    "console.context",
    "SVGAnimationElement", "PasswordCredential",
    "ViewTransition", "MathMLElement",
    "WebKitCSSMatrix", "SVGTextPositioningElement",
    "XMLHttpRequestEventTarget", "TextDecoderStream",
    "WritableStream", "TransformStream", "TextTrackCue", "WeakRef",
    "VisualViewport", "StyleSheet", "RTCDtlsTransport", "Atomics",
    "StaticRange", "UIEvent", "SVGGeometryElement", "RTCDataChannel",
    "AbortController", "onanimationcancel",
    "IIRFilterNode", "RTCStatsReport", "MediaStreamTrack",
    "CropTarget", "BatteryManager", "LaunchQueue",
    "CSSFontPaletteValuesRule", "PushSubscriptionOptions",
    "RTCTrackEvent", "ServiceWorkerContainer",
    "WeakSet",
    "SVGFEDropShadowElement", "SharedWorker",
    "AudioSinkInfo", "Notification.prototype.image",
    "ContentVisibilityAutoStateChangeEvent",
    "PerformanceResourceTiming.prototype.renderBlockingStatus",
    "console.createTask", "PerformanceServerTiming",
    "structuredClone", "onslotchange", "EyeDropper", "URLPattern",
    "VideoFrame", "WritableStreamDefaultController",
    "CSSCounterStyleRule", "CustomStateSet",
    "ReadableStreamDefaultController",
    "XMLDocument.prototype.hasStorageAccess", "CryptoKey", "SubmitEvent",
    "MediaMetadata", "VideoPlaybackQuality",
    "ReadableStreamDefaultReader", "UserActivation", "FragmentDirective",
    "RTCRtpTransceiver.prototype.stop", "Scheduling", "EventCounts",
    "SourceBuffer", "RTCError", "MediaDeviceInfo",
    "RTCPeerConnectionIceErrorEvent", "RTCSctpTransport",
    "MediaSourceHandle", "RTCEncodedAudioFrame",
    "HTMLSlotElement", "GeolocationPosition",
    "MediaSource", "WebTransport", "GPUSupportedLimits", "ToggleEvent",
}


# ─── Video/Audio codec support (Chrome defaults) ───

CHROME_VIDEO_CODECS = {
    "vco": "",      "vcots": False,
    "vch": "probably", "vchts": True,
    "vcw": "probably", "vcwts": True,
    "vc3": "maybe",    "vc3ts": False,
    "vcmp": "",        "vcmpts": False,
    "vc1": "probably", "vc1ts": True,
    "vcmk": "maybe",  "vcmkuts": False,
    "vcq": "",         "vcqts": False,
}

CHROME_AUDIO_CODECS = {
    "aco": "probably", "acots": False,
    "acmp": "probably","acmpts": True,
    "acmpu": "maybe",  "acmputs": False,
    "acw": "probably", "acwts": False,
    "acma": "maybe",   "acmats": False,
    "acaa": "probably","acaats": True,
    "ac3": "",         "ac3ts": False,
    "acf": "probably", "acfts": False,
    "acmp4": "maybe",  "acmp4ts": False,
    "acmp3": "probably","acmp3ts": False,
    "acwm": "maybe",   "acwmts": False,
}

# ─── Feature detection booleans (Chrome 148 defaults) ───

CHROME_FEATURES = {
    "pro_t": True,   # Promise.prototype.then
    "wglo": True,    # WebGL supported
    "prso": True,    # Performance.prototype.setResourceTimingBufferSize
    "wbst": True,    # WebSocket
    "psn": True,     # PushSubscription
    "edp": True,     # EventTarget.prototype.dispatchEvent
    "addt": True,    # AudioContext.prototype.decodeAudioData
    "wsdc": True,    # WritableStreamDefaultController
    "ccsr": True,    # CSS.supports
    "nuad": True,    # navigator.userAgentData
    "bcda": False,   # BarcodeDetector (not in Chrome desktop)
    "idn": True,     # Intl.DisplayNames
    "capi": False,   # captureEvents (deprecated)
    "svde": False,   # SVGDefsElement (not standard)
    "vpbq": True,    # VideoPlaybackQuality
}

CHROME_BOT_CHECKS = {
    "awe": False,    # awesomium
    "phe": False,    # phantomjs
    "dat": False,    # domAutomation
    "nm": False,     # nightmare
    "geb": False,    # webdriver (gecko)
    "sqt": False,    # selenium
    "spwn": False,   # spawn
    "emt": False,    # emit
}


# ─── Navigation timing generator ───

def generate_nav_timing(page_size_bytes=200000):
    """
    Generate realistic navigation timing values.
    These come from performance.getEntriesByType("navigation")[0].
    """
    dns = round(random.uniform(0, 3), 1)
    tcp = round(random.uniform(0, 5), 1)
    tls = round(random.uniform(3, 15), 6)
    request_start_offset = round(random.uniform(0, 5), 6)
    response_time = round(random.uniform(80, 600), 6)
    first_interim = round(random.uniform(-10, 5), 6)
    sw_time = round(random.uniform(0, 5), 6)

    encoded_size = page_size_bytes
    decoded_size = page_size_bytes + random.randint(50000, 300000)
    compression_diff = decoded_size - encoded_size

    dom_interactive = round(random.uniform(500, 2000), 6)
    dcl_start = dom_interactive + random.uniform(0, 50)
    dcl_duration = round(random.uniform(0.2, 5), 6)
    load_event_duration = round(random.uniform(0, 2), 1)

    dom_complete_offset = round(random.uniform(0, 100), 1)

    connect_end = tcp + tls
    secure_diff = connect_end - tcp if connect_end > 0 else 0
    nt_esc = round(random.uniform(0, 2), 6) if secure_diff > 0 else 0

    ttrd_denom = connect_end - tcp if (connect_end - tcp) > 0 else 1
    ttrd_numer = response_time - ttrd_denom
    nt_ttrd = round(ttrd_numer / ttrd_denom, 6) if ttrd_denom != 0 else None

    return {
        "nt_tcp": round(tcp, 1),
        "nt_dns": round(dns, 1),
        "nt_rd": 0,
        "nt_irt": round(first_interim, 6),
        "nt_rt": round(response_time, 6),
        "nt_tls": round(tls, 6),
        "nt_ttf": round(response_time + sw_time + 10, 6),
        "nt_swt": round(sw_time, 6),
        "nt_csd": compression_diff,
        "nt_nhp": "h2",
        "nt_rdc": 0,
        "nt_it": "navigation",
        "nt_prs": round(request_start_offset, 6),
        "nt_esc": round(nt_esc, 6),
        "nt_ttrd": nt_ttrd,
        "nt_le": round(load_event_duration, 1),
        "nt_dcle": round(dcl_duration, 6),
        "nt_di": round(dom_interactive, 6),
        "nt_dc": round(dom_complete_offset, 1),
    }


# ─── trrd generator (tags.js line 1447) ───

def generate_trrd():
    """
    Complex trig formula using Math.random() from iframe's contentWindow.
    Result is atan2(e, c) where both involve random noise.
    Output range: roughly 0.3 to 1.5 (observed).
    """
    sqrt2 = math.sqrt(2)
    r1 = random.random()
    r2 = random.random()
    r3 = random.random()
    r4 = random.random()

    e = math.sqrt(abs(
        math.sin(math.pi / 90 * 100 - 40 * r1 * (math.pi / 180) / 2) +
        math.cos(100 * sqrt2 * (math.pi / 180)) *
        math.sin(math.pi / 180 * 40 - 100 * r2 * (math.pi / 75) / 2)
    ))

    c_val = r3 * math.sqrt(abs(
        1 - math.sin(40 * r4 * (math.pi / 90) - 100 * sqrt2 * (math.pi / 180) / 2) +
        math.cos(3.7055555555555557) * random.random() *
        math.sin(math.pi / 180 * 60 - math.pi / 45 * 100 / 2)
    ))

    return math.atan2(e, c_val)


# ─── bchk generator ───

def generate_bchk(apis_present=None):
    """Generate the browser compatibility check hash (142 chars)."""
    if apis_present is None:
        apis_present = CHROME_148_APIS_PRESENT
    result = []
    for i, api in enumerate(BCHK_APIS):
        if api in apis_present:
            result.append(BCHK_FOUND[i % len(BCHK_FOUND)])
        else:
            result.append(BCHK_ABSENT[i % len(BCHK_ABSENT)])
    return "".join(result)


# ─── Error stack generator (ccsT, ccsB, ccsH, ccsV) ───

def generate_error_stacks(url="https://www.etsy.com/include/tags.js"):
    """
    Generate Chrome-style error stacks for the CSS canvas fingerprint.
    The error is thrown inside tags.js and captured.
    """
    line = 2
    col_t = random.randint(99000, 101000)
    col_b1 = random.randint(77000, 79000)
    col_b2 = random.randint(98000, 100000)
    col_b3 = random.randint(105000, 107000)

    full_stack = (
        f"Error\n"
        f"at y1 ({url}:{line}:{col_t})\n"
        f"at {url}:{line}:{col_b1}\n"
        f"at {url}:{line}:{col_b2}\n"
        f"at {url}:{line}:{col_b3}"
    )

    ccsT = full_stack[:150]
    ccsB = full_stack[-150:]
    ccsH = djb2_hash(full_stack)
    ccsV_raw = hashlib.sha256(full_stack.encode()).hexdigest()

    return {
        "ccsT": ccsT,
        "ccsB": ccsB,
        "ccsH": ccsH,
        "ccsV": ccsV_raw,
    }


# ─── Fingerprint hash (fph) ───

def compute_fph(profile, extra_fields=None):
    """
    fph = S(join of [glrd, glvd, ua, hc, lgs, mtp, pf, br_oh, br_ow, D, h, R, k, dvm])
    D = timezone signal, h = MIME types, R = deprecated features, k = bchk
    """
    parts = [
        str(profile.get("glrd", "")),
        str(profile.get("glvd", "")),
        str(profile.get("ua", "")),
        str(profile.get("hc", "")),
        str(profile.get("lgs", "")),
        str(profile.get("ts_mtp", 0)),
        str(profile.get("pf", "")),
        str(profile.get("br_oh", "")),
        str(profile.get("br_ow", "")),
    ]
    if extra_fields:
        parts.extend([str(v) for v in extra_fields])
    else:
        parts.extend(["", "", "", "", str(profile.get("dvm", ""))])

    joined = "".join(parts)
    return djb2_hash(joined)


# ─── Signal group checksums (sgb, sgd, sgc) ───

def compute_signal_checksums(payload):
    """
    Compute XOR checksum accumulators.
    sgb (L) = XOR of T() calls (browser signals hashed)
    sgd (P) = XOR of S() calls (static properties hashed)
    sgc (j) = XOR of all (T + S + m calls)

    These track which signals were collected and in what order.
    """
    L = 0  # sgb
    P = 0  # sgd
    j = 0  # sgc

    def T(val):
        nonlocal L, j
        h = djb2_hash(str(val))
        L ^= h
        j ^= h

    def S(val):
        nonlocal P, j
        h = djb2_hash(str(val))
        P ^= h
        j ^= h

    def m(val):
        nonlocal j
        h = djb2_hash(str(val))
        j ^= h

    # Reproduce the signal collection order from tags.js
    # Lines 2524+ and signal collection functions

    # H1 function signals (line 2515)
    T(payload.get("lgs", ""))
    S(payload.get("pf", ""))
    S(str(payload.get("ts_mtp", 0)) + "a")
    m(str(payload.get("mob", False)) + "bb")
    m(str(payload.get("hc", 8)) + "ccc")
    m(str(payload.get("dvm", 8)) + "dddd")

    # Timezone
    S(payload.get("tz", -60))

    # eva
    T(payload.get("eva", 40))

    # wdifpnh
    T(payload.get("wdifpnh", ""))

    # Various feature detection signals contribute too
    # These are approximate — exact order depends on execution

    return {
        "sgb": str(L & 0xFFFFFFFF),
        "sgd": str(P & 0xFFFFFFFF),
        "sgc": str(j & 0xFFFFFFFF),
    }


# ─── r3n / _hsv generator ───

def generate_r3n(server_hash=None):
    """
    r3n uses window._hsv which combines:
    - Random hex string (8 chars)
    - Last 4 chars of server hash inserted at random position
    If no server hash available, returns 33 (default).
    """
    if server_hash and len(server_hash) >= 4:
        hash_suffix = server_hash[-4:]
        rand_hex = format(random.randint(0, 0xFFFFFFFF), '08X')
        pos = random.randint(0, 8)
        hsv = rand_hex[:pos] + hash_suffix + rand_hex[pos:]
        return hsv
    return 33


# ─── wdifpnh generator ───

def generate_wdifpnh():
    """Window DIF pseudo-nonce hash — random per session."""
    return str(random.randint(1000000000, 4294967295))


# ─── Main payload builder ───

def build_payload(
    profile="chrome_win10",
    url="https://www.etsy.com/",
    tags_js_url=None,
    server_hash=None,
    bpc=1,
    custom_overrides=None,
):
    """
    Build a complete DataDome fingerprint payload with 190 signals.

    Args:
        profile: Browser profile name or dict with static values
        url: Target website URL
        tags_js_url: URL of tags.js (for error stacks)
        server_hash: Server hash from dd.hsh (for r3n)
        bpc: Payload counter (increments per send)
        custom_overrides: Dict of values to override

    Returns:
        OrderedDict with all signals in correct order
    """
    if tags_js_url is None:
        domain = url.rstrip("/").split("//")[-1].split("/")[0]
        tags_js_url = f"https://{domain}/include/tags.js"

    # Load profile
    if isinstance(profile, dict):
        prof = profile.copy()
    else:
        prof = PROFILES.get(profile, CHROME_WIN10_PROFILE).copy()

    # ─── Dynamic values ───
    now_ms = int(time.time() * 1000)
    jset = now_ms // 1000
    trrd = generate_trrd()
    nav_timing = generate_nav_timing()
    error_stacks = generate_error_stacks(tags_js_url)
    wdifpnh = generate_wdifpnh()
    r3n = generate_r3n(server_hash)
    bchk = generate_bchk()

    # ─── Detected fonts (site-specific, use realistic Etsy fonts) ───
    dffls = "Guardian-EgypTT,Graphik Webfont,ABCOtto,ABCDiatype"

    # ─── Browser window dimensions with slight randomization ───
    br_w = prof["br_w"] + random.randint(-50, 50)
    br_h = prof["br_h"] + random.randint(-50, 50)
    br_iw = br_w
    br_ih = br_h

    # ─── Build payload in exact signal order (matches tags.js collection) ───
    payload = OrderedDict()

    # --- Phase 1: log2 (which async signals completed) ---
    payload["log2"] = "gl,tzp"

    # --- Phase 2: r3n (first signal added, includes _hsv check) ---
    payload["r3n"] = r3n

    # --- Phase 3: WebGL signals ---
    payload["glvd"] = prof["glvd"]
    payload["glrd"] = prof["glrd"]

    # --- Phase 4: Cookie/session state ---
    payload["nddc"] = 1
    payload["exp8"] = 0

    # --- Phase 5: Plugins ---
    payload["plu"] = prof["plu"]
    payload["plgod"] = prof["plgod"]
    payload["plg"] = prof["plg"]
    payload["plgne"] = prof["plgne"]
    payload["plgre"] = prof["plgre"]
    payload["plgof"] = prof["plgof"]
    payload["plggt"] = prof["plggt"]

    # --- Phase 6: Visibility / Window ---
    payload["bfr"] = False
    payload["hdn"] = False
    payload["br_w"] = br_w
    payload["br_h"] = br_h
    payload["br_iw"] = br_iw
    payload["br_ih"] = br_ih

    # --- Phase 7: Screen ---
    payload["ars_w"] = prof["ars_w"]
    payload["ars_h"] = prof["ars_h"]
    payload["rs_w"] = prof["rs_w"]
    payload["rs_h"] = prof["rs_h"]
    payload["rs_cd"] = prof["rs_cd"]

    # --- Phase 8: CSS client geometry ---
    payload["cg_w"] = prof["cg_w"]
    payload["cg_h"] = prof["cg_h"]
    payload["sg_w"] = prof["sg_w"]
    payload["sg_h"] = prof["sg_h"]

    # --- Phase 9: Pixel ratio & orientation ---
    payload["pr"] = prof["pr"]
    payload["so"] = prof["so"]

    # --- Phase 10: trrd (Math trig fingerprint) ---
    payload["trrd"] = trrd

    # --- Phase 11: Override detection ---
    payload["ucdv"] = False
    payload["dp0"] = False
    payload["hcovdr"] = False
    payload["plovdr"] = False
    payload["ftsovdr"] = False

    # --- Phase 12: Fonts ---
    payload["orf"] = ""
    payload["dffls"] = dffls

    # --- Phase 13: Network information ---
    payload["niet"] = prof["niet"]
    payload["nid"] = prof["nid"]
    payload["nisd"] = prof["nisd"]

    # --- Phase 14: Navigation timing ---
    for k, v in nav_timing.items():
        payload[k] = v

    # --- Phase 15: Language ---
    payload["lg"] = prof["lg"]

    # --- Phase 16: Iframe detection ---
    payload["isb"] = False
    payload["idp"] = True

    # --- Phase 17: requestIdleCallback ---
    payload["crt"] = 0

    # --- Phase 18: Vendor/bid ---
    payload["vnd"] = prof["vnd"]
    payload["bid"] = prof["bid"]

    # --- Phase 19: MediaDevices ---
    payload["med"] = prof["med"]

    # --- Phase 20: Permission/override checks ---
    payload["pltod"] = False
    payload["wdifrm"] = False
    payload["npmtm"] = False
    payload["wdif"] = False

    # --- Phase 21: Error stacks (CSS canvas) ---
    payload["ccsT"] = error_stacks["ccsT"]
    payload["ccsB"] = error_stacks["ccsB"]
    payload["ccsH"] = error_stacks["ccsH"]
    payload["ccsV"] = error_stacks["ccsV"]

    # --- Phase 22: MIME types ---
    payload["mmt"] = prof["mmt"]

    # --- Phase 23: wdifpnh ---
    payload["wdifpnh"] = wdifpnh

    # --- Phase 24: Video codecs ---
    payload["vco"] = ""
    payload["vcots"] = False
    for k, v in CHROME_VIDEO_CODECS.items():
        payload[k] = v

    # --- Phase 25: CSS fingerprint ---
    payload["cssS"] = prof["cssS"]
    payload["css0"] = prof["css0"]
    payload["css1"] = prof["css1"]
    payload["cssH"] = prof["cssH"]
    payload["csssp"] = prof["csssp"]

    # --- Phase 26: Mouse events ---
    payload["muev"] = False

    # --- Phase 27: Feature detection ---
    for k, v in CHROME_FEATURES.items():
        payload[k] = v

    # --- Phase 28: bchk ---
    payload["bchk"] = bchk

    # --- Phase 29: Timezone ---
    payload["tz"] = prof["tz"]

    # --- Phase 30: Hidden/Focus state ---
    payload["ihdn"] = False
    payload["cdhf"] = False

    # --- Phase 31: eva (XMLDocument.toString().length) ---
    payload["eva"] = prof["eva"]

    # --- Phase 32: Chrome keys ---
    payload["cokys"] = prof["cokys"]

    # --- Phase 33: Process/opener ---
    payload["ecpc"] = False
    payload["wop"] = False

    # --- Phase 34: Navigator/UA data ---
    payload["pf"] = prof["pf"]
    payload["hc"] = prof["hc"]
    payload["br_oh"] = prof["br_oh"]
    payload["br_ow"] = prof["br_ow"]
    payload["ua"] = prof["ua"]
    payload["wbd"] = prof["wbd"]
    payload["ts_mtp"] = prof["ts_mtp"]
    payload["mob"] = prof["mob"]
    payload["lgs"] = prof["lgs"]
    payload["dvm"] = prof["dvm"]

    # --- Phase 35: Cookie writing ---
    payload["ckwa"] = True

    # --- Phase 36: Audio codecs ---
    for k, v in CHROME_AUDIO_CODECS.items():
        payload[k] = v

    # --- Phase 37: Permissions ---
    payload["ocpt"] = False

    # --- Phase 38: Media queries ---
    payload["mq"] = "aptr:fine, ahvr:hover"
    payload["mq2"] = "cg:srgb, dr:standard, dm:browser"

    # --- Phase 39: Bot detection ---
    for k, v in CHROME_BOT_CHECKS.items():
        payload[k] = v

    # --- Phase 40: Navigator hardware info ---
    payload["nhi"] = prof["nhi"]

    # --- Phase 41: Keyboard layout ---
    payload["k_lyts"] = prof["k_lyts"]
    payload["k_lytk"] = prof["k_lytk"]

    # --- Phase 42: Barcode detection ---
    payload["bci"] = True
    payload["bcl"] = 1
    payload["bct"] = 0
    payload["bdt"] = None

    # --- Phase 43: Storage quota ---
    payload["stqe"] = prof["stqe"]
    payload["stqu"] = prof["stqu"]

    # --- Phase 44: Iframe detection flags ---
    payload["isf"] = False
    payload["isf2"] = False

    # --- Phase 45: Automation detection ---
    payload["pw"] = False
    payload["pcb"] = False
    payload["arc"] = False
    payload["fai"] = False
    payload["gai"] = False
    payload["bbs3"] = False

    # --- Phase 46: DevTools detection ---
    payload["dt"] = True

    # --- Phase 47: Fingerprint hash ---
    payload["fph"] = compute_fph(prof)

    # --- Phase 48: Signal group checksums ---
    checksums = compute_signal_checksums(payload)
    payload["sgb"] = checksums["sgb"]
    payload["sgd"] = checksums["sgd"]
    payload["sgc"] = checksums["sgc"]

    # --- Phase 49: JS execution timestamp ---
    payload["jset"] = jset

    # --- Phase 50: Payload counter ---
    payload["bpc"] = bpc

    # Apply custom overrides
    if custom_overrides:
        payload.update(custom_overrides)

    return payload


# ─── CLI ───

def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="DataDome fingerprint payload builder")
    parser.add_argument("--profile", "-p", default="chrome_win10", help="Browser profile")
    parser.add_argument("--url", "-u", default="https://www.etsy.com/", help="Target URL")
    parser.add_argument("--hash", default=None, help="Server hash (dd.hsh) for r3n")
    parser.add_argument("--output", "-o", default=None, help="Output JSON file")
    parser.add_argument("--encrypt", "-e", action="store_true", help="Encrypt to jspl")
    parser.add_argument("--key", "-k", default=None, help="ddjskey for encryption")
    parser.add_argument("--cid", "-c", default=None, help="Session CID for encryption")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of payloads")

    args = parser.parse_args()

    for i in range(args.count):
        payload = build_payload(
            profile=args.profile,
            url=args.url,
            server_hash=args.hash,
            bpc=i + 1,
        )

        if args.encrypt and args.key:
            from crypto import encrypt
            jspl = encrypt(payload, args.key, cid=args.cid)
            print(f"[Payload {i+1}] jspl ({len(jspl)} chars):")
            print(jspl)
            print()
        else:
            out = json.dumps(payload, indent=2, ensure_ascii=False)
            if args.output:
                fname = args.output if args.count == 1 else f"{args.output.rsplit('.', 1)[0]}_{i+1}.json"
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(out)
                print(f"[Payload {i+1}] Saved to {fname} ({len(payload)} signals)")
            else:
                print(out)


if __name__ == "__main__":
    main()
