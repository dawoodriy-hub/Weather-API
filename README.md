# 🌤️ Weather App

A Python command-line app that fetches **real-time weather data** for any city in the world — with no API key or sign-up required.

Built by **Dawood Riyazi** as a Python beginner project.

---

## 📸 Example Output

```
════════════════════════════════════════════════
        🌤️   W E A T H E R   A P P
════════════════════════════════════════════════

  ⛅  London, United Kingdom
     Partly Cloudy
════════════════════════════════════════════════
  🌡️  Temperature   14°C  /  57°F
  🤔  Feels Like    12°C  /  54°F
  💧  Humidity      72%
  💨  Wind          18 km/h W
  👁️  Visibility    10 km
  ☀️  UV Index      2
────────────────────────────────────────────────

  📅  7-Day Forecast
────────────────────────────────────────────────
  Day                    Condition         High    Low
────────────────────────────────────────────────
 Sunday, 03 May: ☁️ Overcast | High 20°C | Low 13°C
Monday, 04 May: ☁️ Overcast | High 18°C | Low 13°C
Tuesday, 05 May: 🌦️ Light drizzle | High 17°C | Low 10°C
Wednesday, 06 May: 🌦️ Light drizzle | High 14°C | Low 9°C
Thursday, 07 May: ☁️ Overcast | High 15°C | Low 10°C
Friday, 08 May: ☁️ Overcast | High 18°C | Low 9°C
Saturday, 09 May: ☁️ Overcast | High 21°C | Low 10°C
────────────────────────────────────────────────
```

---

## 🚀 How to Install

**1. Make sure Python 3.10+ is installed**
```bash
python --version
```

**2. Clone this repository**
```bash
git clone https://github.com/YourUsername/WeatherApp.git
cd WeatherApp
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

> ℹ️ This project only uses Python's built-in libraries — no packages need installing!

---

## ▶️ How to Run

**Prompt for a city:**
```bash
python Weather.py
```

**Pass a city directly:**
```bash
python Weather.py London
python Weather.py "New York"
python Weather.py Tokyo
python Weather.py Karachi
```

**Run without interactive prompts:**
```bash
python Weather.py --noconsole
python Weather.py "New York" --noconsole
```

---

## ✨ Features

- ✅ **No API key needed** — uses the free [wttr.in](https://wttr.in) service
- ✅ **Any city in the world** — just type the name
- ✅ **Current conditions** — temperature, feels like, humidity, wind, UV index
- ✅ **3-day forecast** — high/low temps and condition for each day
- ✅ **Weather emojis** — 40+ weather condition icons
- ✅ **Search again** — look up multiple cities without restarting
- ✅ **Error handling** — clear messages for bad city names or no internet
- ✅ **Command-line argument** — pass city as argument or type it when prompted

---

## 🛠️ How It Works

1. Takes a city name from the user
2. Sends a request to `https://wttr.in/{city}?format=j1`
3. Parses the JSON response
4. Extracts temperature, humidity, wind, UV index and 3-day forecast
5. Displays everything in a clean formatted layout

---

## 🌐 API Used

[wttr.in](https://github.com/chubin/wttr.in) — a free, open-source weather service that requires no authentication.

---

## 🛠️ Built With

- **Python 3.10+**
- `urllib` — built-in HTTP requests
- `json` — built-in JSON parsing
- `datetime` — built-in date formatting

---

## 📄 License

MIT License — free to use, modify and share.

---

## 👤 Author

**Dawood Riyazi**
- GitHub: [@DawoodRiyazi](https://github.com/DawoodRiyazi)
