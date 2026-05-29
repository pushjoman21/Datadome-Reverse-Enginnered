# Datadome Solver Block - Verwendungsanleitung

## Block Parameter

### TargetUrl (string)
**Standard:** `https://www.etsy.com/`

Die Ziel-Website, auf der Datadome gelöst werden soll.

```
TargetUrl = "https://www.amazon.com/"
TargetUrl = "https://booking.com/"
TargetUrl = "https://www.example.com/"
```

### DdJsKey (string)
**Standard:** `D013AA612AB2224D03B2318D0F5B19`

Der Datadome JavaScript Key für die Website. Variiert je nach Website.

**Wie man den Key findet:**

```javascript
// In Browser Console:
window.DD_JSKEY

// Oder in der Netzwerk-Anfrage:
// Headers → X-Datadome-JSKey
```

**Bekannte Keys:**
- Etsy: `D013AA612AB2224D03B2318D0F5B19`
- Booking: (variiert)
- Amazon: (variiert)

### Cid (string)
**Standard:** `` (leer)

Challenge ID. Oft vom Server in der Response oder einem Cookie bereitgestellt.

```
// Leer lassen (wird meist nicht benötigt)
Cid = ""

// Oder extrahieren:
LRS @cid "cid=" "&" 0
Cid = @cid
```

### Profile (string)
**Standard:** `chrome_win10`

Browser-Profil für die Fingerprint-Generierung.

**Verfügbare Profile:**

| Profile | Browser | OS | Version |
|---------|---------|----|---------|
| `chrome_win10` | Chrome | Windows 10 | 148 |
| `chrome_win10_de` | Chrome | Windows 10 (DE) | 148 |

### ServiceUrl (string)
**Standard:** `http://localhost:5000`

URL des Solver-Services. Sollte dem Port entsprechen, auf dem `solver_service.py` läuft.

```
ServiceUrl = "http://127.0.0.1:5000"    // Local
ServiceUrl = "http://192.168.1.5:5000"  // Andere Machine
ServiceUrl = "http://solver.example.com" // Remote
```

### TimeoutSeconds (int)
**Standard:** `30`

Timeout für die Challenge-Antwort in Sekunden.

```
TimeoutSeconds = 30  // Standard
TimeoutSeconds = 60  // Länger für langsame Netzwerke
TimeoutSeconds = 10  // Schneller für gutes Netzwerk
```

## Output Variable

### DatadomeCookie (string)

Die gelöste Datadome-Cookie, bereit für weitere Requests.

```
SET @cookie = <DatadomeCookie>
LOG @cookie  // z.B.: x=abcd1234...

// Verwenden in Cookie:
COOKIE ADD x @cookie
```

## Beispiel-Configs

### 1. Minimal-Beispiel

```
[REQUEST]
  GET https://www.etsy.com/

[BLOCK]
  DATADOME SOLVER
    TargetUrl = "https://www.etsy.com/"
    DdJsKey = "D013AA612AB2224D03B2318D0F5B19"

SET @cookie = <DatadomeCookie>
LOG "Success: " @cookie
```

### 2. Mit Fehlerbehandlung

```
[BLOCK]
  IF <LoopState> == "SUCCESS"
    DATADOME SOLVER
      TargetUrl = "https://www.etsy.com/"
      DdJsKey = "D013AA612AB2224D03B2318D0F5B19"
      Cid = ""
      TimeoutSeconds = 60
    
    SET @datadome = <DatadomeCookie>
    LOG @datadome
  ELSE
    LOG "ERROR: Datadome challenge timed out"
  ENDIF
```

### 3. Mit Cookies setzen

```
[BLOCK]
  DATADOME SOLVER
    TargetUrl = "https://www.etsy.com/"
    DdJsKey = "D013AA612AB2224D03B2318D0F5B19"

SET @cookie = <DatadomeCookie>

[REQUEST]
  GET https://www.etsy.com/
  COOKIES
    x = @cookie
```

### 4. Multi-Site Loop

```
[INPUT]
  LINES
    https://www.etsy.com/|D013AA612AB2224D03B2318D0F5B19
    https://www.amazon.com/|AMAZON_KEY_HERE

FOREACH @line IN @INPUT
  PARSE @line
    REGEX @url "^(.*?)\|" 
    REGEX @key "\|(.*?)$"
  
  [BLOCK]
    DATADOME SOLVER
      TargetUrl = @url
      DdJsKey = @key
      Profile = "chrome_win10"
  
  SET @cookie = <DatadomeCookie>
  LOG @url " => " @cookie
  
  DELAY 5000
END
```

### 5. Mit Proxy-Rotation

```
[REQUEST]
  GET https://www.etsy.com/
  PROXY
    "http://proxy1.com:8080"
    "http://proxy2.com:8080"
    "http://proxy3.com:8080"

[BLOCK]
  DATADOME SOLVER
    TargetUrl = "https://www.etsy.com/"
    DdJsKey = "D013AA612AB2224D03B2318D0F5B19"
    TimeoutSeconds = 45

SET @cookie = <DatadomeCookie>
```

### 6. Dynamic DdJsKey Extract

```
[REQUEST]
  GET https://www.etsy.com/

[PARSE]
  // DdJsKey aus HTML extrahieren
  REGEX @key "DD_JSKEY[\s=]+['\"]([^'\"]+)['\"]" 0
  
  IF @key != ""
    LOG "Found DdJsKey: " @key
  ELSE
    LOG "ERROR: Could not find DdJsKey"
  ENDIF

[BLOCK]
  IF @key != ""
    DATADOME SOLVER
      TargetUrl = "https://www.etsy.com/"
      DdJsKey = @key
      Profile = "chrome_win10"
    
    SET @cookie = <DatadomeCookie>
    LOG "Got cookie: " @cookie
  ENDIF
```

## Tipps & Tricks

### Schnellere Ausführung

```
// Nutze schnelle Netzwerk-Verbindung
TimeoutSeconds = 15

// Verzögerungen minimieren
DELAY 1000  // nur 1 Sekunde
```

### Bessere Erfolgsquote

```
// Verwende weniger verdächtiges Profil
Profile = "chrome_win10_de"  // Deutsch, besser für DE Websites

// Längeres Timeout für schlechte Verbindungen
TimeoutSeconds = 60

// Mit Proxy
PROXY "http://proxy:8080"
```

### Debugging

```
// Logge die Cookie
SET @cookie = <DatadomeCookie>
LOG @cookie

// Prüfe ob Cookie gültig
IF @cookie.LENGTH > 10
  LOG "Cookie looks valid"
ELSE
  LOG "ERROR: Invalid cookie"
ENDIF
```

### Rate Limiting

```
// Verzögerung zwischen Requests
[BLOCK]
  DATADOME SOLVER
    ...

DELAY 5000  // 5 Sekunden
DELAY RANDOM 2000 10000  // 2-10 Sekunden random
```

## Häufige Fehler

### "Service not responding"

**Lösung:**
```bash
# Terminal: Service starten
python solver_service.py

# ServiceUrl überprüfen
ServiceUrl = "http://localhost:5000"  // Correct
ServiceUrl = "http://127.0.0.1:5000"  // Alternative
```

### "Challenge failed with status 403"

**Lösung:**
1. `DdJsKey` überprüfen (website-spezifisch)
2. Mit leerem `Cid` versuchen
3. `TimeoutSeconds` erhöhen

### "Invalid profile"

**Lösung:**
Nur diese Profile verwenden:
- `chrome_win10`
- `chrome_win10_de`

## Performance-Optimierung

```
// LANGSAM
TimeoutSeconds = 120
DELAY 10000

// SCHNELL
TimeoutSeconds = 15
DELAY 1000

// BALANCED
TimeoutSeconds = 30
DELAY 3000
```

## Weitere Ressourcen

- [Installations-Guide](INSTALL.md)
- [Haupt-README](../README.md)
- Hauptrepository: https://github.com/Lumbijumbi/Datadome-Reverse-Enginnered
