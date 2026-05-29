# Datadome Solver für OpenBullet2 - Installationsanleitung

## 🚀 Schnellstart (5 Minuten)

### Schritt 1: Abhängigkeiten installieren

```bash
cd openbullet2
pip install -r requirements.txt
```

### Schritt 2: Solver-Service starten

```bash
python solver_service.py
```

Expected output:
```
============================================================
 Datadome Solver Service for OpenBullet2
============================================================

[*] Starting service...
[*] Available endpoints:
    GET  /health          - Health check
    POST /solve           - Solve Datadome challenge
    POST /build           - Build fingerprint (debug)
    POST /encrypt         - Encrypt payload (debug)

[*] Listening on http://localhost:5000
[*] Press CTRL+C to stop
```

### Schritt 3: Plugin in OpenBullet2 installieren

#### Option A: Vorkompilierte DLL verwenden
1. `DatadomeSolver.dll` in OpenBullet2 `plugins` Ordner kopieren
2. OpenBullet2 neu starten

#### Option B: Aus Source kompilieren
1. `DatadomeSolver.cs` in dein Visual Studio Projekt kopieren
2. Abhängigkeiten hinzufügen:
   - Newtonsoft.Json (NuGet)
   - RuriLib
3. Kompilieren
4. DLL in OpenBullet2 `plugins` Ordner kopieren

### Schritt 4: In OpenBullet2 Config verwenden

```
BLOCK Datadome Solver
  TargetUrl = "https://www.etsy.com/"
  DdJsKey = "D013AA612AB2224D03B2318D0F5B19"
  Cid = ""
  Profile = "chrome_win10"
  ServiceUrl = "http://localhost:5000"
  TimeoutSeconds = 30

SET @cookie = <DatadomeCookie>
```

## 📋 Verwendungsbeispiele

### Einfaches Beispiel: Etsy Cookie holen

```
[BLOCK]
  DATADOME SOLVER
    TargetUrl = "https://www.etsy.com/"
    DdJsKey = "D013AA612AB2224D03B2318D0F5B19"
    Cid = ""
    Profile = "chrome_win10"
  
  CVAR @datadome_cookie = <DatadomeCookie>
  LOG @datadome_cookie
```

### Advanced: Mit Custom Headers

```
[REQUEST]
  GET https://www.etsy.com/
  COOKIES 0
  HEADERS
    User-Agent = "Mozilla/5.0..."
  
  DATA
    Content = @responseBody

[PARSE]
  LRS @cid "name=\"dd-cid\" value=\"" "\"" 0

[BLOCK]
  DATADOME SOLVER
    TargetUrl = "https://www.etsy.com/"
    DdJsKey = "D013AA612AB2224D03B2318D0F5B19"
    Cid = @cid
    Profile = "chrome_win10"
  
  CVAR @datadome_cookie = <DatadomeCookie>
  COOKIE ADD x @datadome_cookie

[OUTPUT]
  @datadome_cookie
```

### Multi-Site: Verschiedene Seiten

```
[DATADOME SOLVER]
  TargetUrl = "https://www.amazon.com/"
  DdJsKey = "<KEY_FOR_AMAZON>"
  Cid = ""
  Profile = "chrome_win10"
```

## 🔧 Konfiguration

### Verfügbare Profile

| Profile | Beschreibung | Browser |
|---------|-------------|----------|
| `chrome_win10` | Chrome 148 Windows 10 | Chrome |
| `chrome_win10_de` | Chrome 148 Windows 10 (Deutsch) | Chrome |

### Ddjskey finden

Auch als `DD_JSKEY` in den Website-Quellen:

```javascript
// In der Browser-Konsole:
window.DD_JSKEY  // Zeigt den aktuellen Key
```

Oder aus der Netzwerk-Response:
```
GET /api/some_endpoint
Response header: x-datadome-jskey: D013AA612AB2224D03B2318D0F5B19
```

### Challenge ID (CID)

Kan aus verschiedenen Quellen kommen:
- Cookie: `dd-cid`
- Query Parameter: `?cid=...`
- Response Header: `x-datadome-cid`
- Oft auch leer lassen: `Cid = ""`

## 🐛 Fehlersuche

### "Connection refused" - Service läuft nicht

```bash
# Terminal 1: Service starten
python solver_service.py

# Terminal 2: Test
curl http://localhost:5000/health
```

### "Challenge failed with status 403"

**Ursachen:**
- Falscher `DdJsKey` → Überprüfen Sie den aktuellen Key der Website
- Falscher `Cid` → Versuchen Sie mit leerem String
- Website hat Updates → Key könnte sich geändert haben

**Lösung:**
```bash
# Debuggen mit curl
curl -X POST http://localhost:5000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.etsy.com/",
    "ddjskey": "D013AA612AB2224D03B2318D0F5B19",
    "cid": "",
    "profile": "chrome_win10"
  }'
```

### "Missing dependency" - Python Fehler

```bash
# Abhängigkeiten installieren
pip install -r openbullet2/requirements.txt

# Oder einzeln:
pip install flask flask-cors tls-client requests
```

### Service hängt / antwortet nicht

```bash
# Service mit Debug Info starten
python solver_service.py

# Service neu starten (CTRL+C)
# Dann:
python solver_service.py
```

## 📊 Performance

- **Durchschnittliche Zeit pro Challenge**: 2-5 Sekunden
- **Abhängig von**: Netzwerk, Website-Response-Zeit, Profil
- **Session wird wiederverwendet**: Nach 5 Minuten neu erstellt

## 🔐 Sicherheit

⚠️ **Wichtig**: Nur mit Genehmigung verwenden!

1. **Service nur lokal** - Standard `localhost:5000`
2. **Rate Limiting** - Verwenden Sie Verzögerungen in OpenBullet2
3. **Proxy Rotation** - Empfohlen für große Mengen
4. **Legal** - Beachten Sie Website Terms of Service

```
[BLOCK]
  DATADOME SOLVER
    ... (wie oben)
  
  DELAY 2000  // 2 Sekunden zwischen Requests
```

## 🆘 Support

Falls Probleme auftreten:

1. Check `solver_service.py` logs in Terminal
2. Test mit `curl` oder Postman
3. Verifizieren Sie `DdJsKey` und `Cid` Werte
4. Prüfen Sie ob Website noch gegen Datadome schützt

## 📝 Lizenz

Bildungs- und Forschungszwecke nur.

Siehe [DISCLAIMER](../README.md) im Haupt-Repository.
