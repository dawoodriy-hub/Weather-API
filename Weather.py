"""
Weather App
===========
Automatically detects your location using your IP address
and shows real-time weather — no API key or sign-up required.

Usage:
    python weather.py                  # auto-detects your location
    python weather.py London           # override with a specific city
    python weather.py "New York"       # use quotes for multi-word cities
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


# ── Constants ─────────────────────────────────────────────────────────────────
WEATHER_API_URL  = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relativehumidity_2m,apparent_temperature,visibility&daily=weathercode,temperature_2m_max,temperature_2m_min,uv_index_max&forecast_days=7&timezone=auto"
GEOCODE_API_URL = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q={query}"
LOCATION_API_URL = "https://ipapi.co/json/"
TIMEOUT_SECONDS  = 8

# ── Weather condition descriptions ────────────────────────────────────────────
WEATHER_DESCRIPTIONS = {
    "0":   ("☀️",  "Clear sky"),
    "1":   ("🌤️", "Mainly clear"),
    "2":   ("⛅",  "Partly cloudy"),
    "3":   ("☁️",  "Overcast"),
    "45":  ("🌫️", "Fog"),
    "48":  ("🌫️", "Depositing rime fog"),
    "51":  ("🌦️", "Light drizzle"),
    "53":  ("🌦️", "Moderate drizzle"),
    "55":  ("🌧️", "Dense drizzle"),
    "56":  ("🌧️", "Freezing drizzle"),
    "57":  ("🌧️", "Freezing drizzle"),
    "61":  ("🌧️", "Slight rain"),
    "63":  ("🌧️", "Moderate rain"),
    "65":  ("🌧️", "Heavy rain"),
    "66":  ("🌧️", "Freezing rain"),
    "67":  ("🌧️", "Freezing rain"),
    "71":  ("❄️",  "Slight snow"),
    "73":  ("❄️",  "Moderate snow"),
    "75":  ("❄️",  "Heavy snow"),
    "77":  ("❄️",  "Snow grains"),
    "80":  ("🌧️", "Slight rain showers"),
    "81":  ("🌧️", "Moderate rain showers"),
    "82":  ("🌧️", "Violent rain showers"),
    "85":  ("❄️",  "Slight snow showers"),
    "86":  ("❄️",  "Heavy snow showers"),
    "95":  ("⛈️",  "Thunderstorm"),
    "96":  ("⛈️",  "Thunderstorm with hail"),
    "99":  ("⛈️",  "Thunderstorm with hail"),
}


# ══════════════════════════════════════════════════════════════════════════════
#  LOCATION DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def fetch_json(url: str) -> dict:
    """Generic helper to fetch and parse JSON from a URL."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "WeatherApp/1.0 (Python)"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def detect_location() -> dict:
    """
    Detect the user's current location using their public IP address.
    Returns a dict with city, region, country, latitude, longitude.
    Raises ConnectionError if location cannot be detected.
    """
    try:
        data = fetch_json(LOCATION_API_URL)
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        return {
            "city":      data.get("city", "Unknown"),
            "region":    data.get("region", ""),
            "country":   data.get("country_name", ""),
            "latitude":  latitude,
            "longitude": longitude,
            "query":     f"{latitude},{longitude}" if latitude is not None and longitude is not None else data.get("city", "Unknown"),
        }
    except Exception:
        raise ConnectionError(
            "Could not detect your location automatically.\n"
            "Please check your internet connection or provide a city name."
        )


# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER FETCHING
# ══════════════════════════════════════════════════════════════════════════════

def geocode_city(city: str) -> dict:
    url = GEOCODE_API_URL.format(query=urllib.parse.quote(city))
    try:
        results = fetch_json(url)
        if not results:
            raise ValueError(f"City '{city}' not found. Please check the spelling.")
        place = results[0]
        return {
            "latitude": float(place["lat"]),
            "longitude": float(place["lon"]),
            "display_name": place.get("display_name", city),
        }
    except urllib.error.URLError:
        raise ConnectionError(
            "Could not connect to the geocoding service.\n"
            "Please check your internet connection and try again."
        )
    except (ValueError, KeyError):
        raise ValueError(f"City '{city}' not found. Please check the spelling.")


def fetch_weather_data_by_coordinates(latitude: float, longitude: float, display_name: str | None = None) -> dict:
    url = WEATHER_API_URL.format(lat=latitude, lon=longitude)
    try:
        data = fetch_json(url)
        data["location"] = {
            "latitude": latitude,
            "longitude": longitude,
            "display_name": display_name or f"{latitude},{longitude}",
        }
        return data
    except urllib.error.URLError:
        raise ConnectionError(
            "Could not connect to the weather service.\n"
            "Please check your internet connection and try again."
        )
    except json.JSONDecodeError:
        raise ValueError("Received unexpected data from the weather service.")


def fetch_weather_data(city: str) -> dict:
    """
    Fetch weather JSON from Open-Meteo for the given city.
    Raises ValueError if city is not found.
    Raises ConnectionError if there is no internet.
    """
    location = geocode_city(city)
    url = WEATHER_API_URL.format(lat=location["latitude"], lon=location["longitude"])
    try:
        data = fetch_json(url)
        data["location"] = location
        return data
    except urllib.error.URLError:
        raise ConnectionError(
            "Could not connect to the weather service.\n"
            "Please check your internet connection and try again."
        )
    except json.JSONDecodeError:
        raise ValueError("Received unexpected data from the weather service.")


# ══════════════════════════════════════════════════════════════════════════════
#  DATA PARSING
# ══════════════════════════════════════════════════════════════════════════════

def get_condition(weather_code: str) -> tuple[str, str]:
    """Return (emoji, description) for a weather condition code."""
    return WEATHER_DESCRIPTIONS.get(str(weather_code), ("🌡️", "Unknown"))


def _wind_direction_from_degrees(degrees: float) -> str:
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    index = int((degrees + 11.25) / 22.5) % 16
    return directions[index]


def _get_current_hour_index(data: dict) -> int:
    current_time = data.get("current_weather", {}).get("time")
    hourly_times = data.get("hourly", {}).get("time", [])
    try:
        return hourly_times.index(current_time)
    except ValueError:
        return 0


def parse_current_weather(data: dict) -> dict:
    """Extract current weather conditions from the Open-Meteo response."""
    current = data["current_weather"]
    location = data.get("location", {})
    display_name = location.get("display_name", "Unknown")
    country = display_name.split(",")[-1].strip() if "," in display_name else ""

    index = _get_current_hour_index(data)
    humidity = data.get("hourly", {}).get("relativehumidity_2m", [None])[index]
    visibility_m = data.get("hourly", {}).get("visibility", [None])[index]
    apparent_temp = data.get("hourly", {}).get("apparent_temperature", [current["temperature"]])[index]
    uv_index = data.get("daily", {}).get("uv_index_max", [None])[0]

    emoji, description = get_condition(current["weathercode"])
    temp_c = round(current["temperature"])
    temp_f = round(temp_c * 9 / 5 + 32)
    visibility_km = round(visibility_m / 1000) if visibility_m is not None else None

    return {
        "city":         display_name,
        "country":      country,
        "temp_c":       str(temp_c),
        "temp_f":       str(temp_f),
        "feels_like_c": str(round(apparent_temp)) if apparent_temp is not None else str(temp_c),
        "feels_like_f": str(round(round(apparent_temp) * 9 / 5 + 32)) if apparent_temp is not None else str(temp_f),
        "humidity":     str(humidity) if humidity is not None else "N/A",
        "wind_kmph":    str(round(current["windspeed"])),
        "wind_dir":     _wind_direction_from_degrees(current["winddirection"]),
        "visibility":   str(visibility_km) if visibility_km is not None else "N/A",
        "uv_index":     str(uv_index) if uv_index is not None else "N/A",
        "description":  description,
        "emoji":        emoji,
    }


def parse_forecast(data: dict) -> list[dict]:
    """Extract the 7-day forecast from the Open-Meteo response."""
    forecast = []
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weathercode", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])

    for index, date_str in enumerate(dates[:7]):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A, %d %b")
        emoji, desc = get_condition(codes[index] if index < len(codes) else 0)

        forecast.append({
            "day":   day_name,
            "max_c": str(round(highs[index])) if index < len(highs) and highs[index] is not None else "N/A",
            "min_c": str(round(lows[index])) if index < len(lows) and lows[index] is not None else "N/A",
            "emoji": emoji,
            "desc":  desc,
        })
    return forecast


# ══════════════════════════════════════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def divider(char: str = "─", width: int = 50) -> None:
    print(char * width)


def print_banner() -> None:
    print()
    divider("═")
    print("         🌤️   W E A T H E R   A P P")
    divider("═")


def print_current_weather(weather: dict, auto: bool = False, detected_place: str | None = None) -> None:
    """Display current weather conditions."""
    print()
    divider("═")
    detected = "  📍 Auto-detected location" if auto else "  🔍 Searched location"
    print(detected)
    if auto and detected_place:
        print(f"     {detected_place}")
        location_line = detected_place
    else:
        location_line = f"{weather['city']}, {weather['country']}"
    print(f"  {weather['emoji']}  {location_line}")
    print(f"     {weather['description']}")
    divider("═")
    print(f"  🌡️  Temperature    {weather['temp_c']}°C  /  {weather['temp_f']}°F")
    print(f"  🤔  Feels Like     {weather['feels_like_c']}°C  /  {weather['feels_like_f']}°F")
    print(f"  💧  Humidity       {weather['humidity']}%")
    print(f"  💨  Wind           {weather['wind_kmph']} km/h {weather['wind_dir']}")
    print(f"  👁️  Visibility     {weather['visibility']} km")
    print(f"  ☀️  UV Index       {weather['uv_index']}")
    divider()


def print_forecast(forecast: list[dict]) -> None:
    """Display the 7-day forecast."""
    print("\n  📅  7-Day Forecast")
    divider()
    print(f"  {'Day':<24} {'Condition':<20} {'High':>5}  {'Low':>5}")
    divider()
    for day in forecast:
        print(
            f"  {day['day']:<24}"
            f"{day['emoji']} {day['desc']:<18}"
            f"{day['max_c']:>4}°C  {day['min_c']:>4}°C"
        )
    divider()


def format_weather_report(
    weather: dict,
    forecast: list[dict],
    auto: bool = False,
    detected_place: str | None = None,
) -> str:
    lines = []
    if auto:
        lines.append("Auto-detected location")
        if detected_place:
            lines.append(detected_place)
    else:
        lines.append(f"{weather['city']}, {weather['country']}")

    lines.append(f"{weather['emoji']}  {weather['description']}")
    lines.append("")
    lines.append(f"Temperature: {weather['temp_c']}°C / {weather['temp_f']}°F")
    lines.append(f"Feels Like:  {weather['feels_like_c']}°C / {weather['feels_like_f']}°F")
    lines.append(f"Humidity:    {weather['humidity']}%")
    lines.append(f"Wind:        {weather['wind_kmph']} km/h {weather['wind_dir']}")
    lines.append(f"Visibility:  {weather['visibility']} km")
    lines.append(f"UV Index:    {weather['uv_index']}")
    lines.append("")
    lines.append("7-Day Forecast")
    lines.append("────────────────────────────────────────")
    for day in forecast:
        lines.append(
            f"{day['day']}: {day['emoji']} {day['desc']} | High {day['max_c']}°C | Low {day['min_c']}°C"
        )
    return "\n".join(lines)


def get_weather_report(city: str | None = None, latitude: float | None = None, longitude: float | None = None, auto: bool = False, detected_place: str | None = None) -> str:
    if latitude is not None and longitude is not None:
        raw_data = fetch_weather_data_by_coordinates(latitude, longitude, display_name=detected_place)
    elif city is not None:
        raw_data = fetch_weather_data(city)
    else:
        raise ValueError("A city name or coordinates are required to fetch weather.")

    current = parse_current_weather(raw_data)
    forecast = parse_forecast(raw_data)
    return format_weather_report(current, forecast, auto=auto, detected_place=detected_place)


def update_report_text(text_widget: tk.Text, content: str) -> None:
    text_widget.configure(state="normal")
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", content)

    text_widget.tag_configure("header", foreground="#1d4ed8", font=("Consolas", 13, "bold"))
    text_widget.tag_configure("label", foreground="#0f766e", font=("Consolas", 12, "bold"))
    text_widget.tag_configure("value", foreground="#9333ea", font=("Consolas", 12, "normal"))
    text_widget.tag_configure("forecast", foreground="#d41111", font=("Consolas", 12, "bold"))
    text_widget.tag_configure("emoji", foreground="#f97316", font=("Consolas", 12, "bold"))
    text_widget.tag_configure("section", foreground="#0f172a", font=("Consolas", 12, "bold"))

    for line_index, line in enumerate(content.splitlines(), start=1):
        start = f"{line_index}.0"
        end = f"{line_index}.end"
        if line.startswith("Auto-detected location") or ("," in line and ":" not in line and not line.startswith("7-Day Forecast")):
            text_widget.tag_add("header", start, end)
        if line.startswith("Temperature") or line.startswith("Feels Like") or line.startswith("Humidity") or line.startswith("Wind") or line.startswith("Visibility") or line.startswith("UV Index"):
            colon_index = line.index(":") + 1
            label_end = f"{line_index}.{colon_index}"
            text_widget.tag_add("label", start, label_end)
            text_widget.tag_add("value", label_end, end)
        if line.startswith("7-Day Forecast"):
            text_widget.tag_add("section", start, end)
        if line.startswith("────────────────────────────────────────"):
            text_widget.tag_add("forecast", start, end)

        for icon in ["☀️", "⛅", "☁️", "🌧️", "🌨️", "⛈️", "❄️", "🌫️"]:
            if icon in line:
                icon_start = line.index(icon)
                icon_end = icon_start + len(icon)
                text_widget.tag_add("emoji", f"{line_index}.{icon_start}", f"{line_index}.{icon_end}")
                break

    text_widget.configure(state="disabled")


def build_weather_app() -> None:
    root = tk.Tk()
    root.title("Weather App")
    root.geometry("740x680")
    root.configure(bg="#eef4ff")
    root.resizable(False, False)

    header = tk.Frame(root, bg="#2b5fa8", padx=16, pady=14)
    header.pack(fill="x")

    title = tk.Label(header, text="Weather App", font=("Segoe UI", 20, "bold"), bg="#2b5fa8", fg="white")
    title.pack(side="left")

    frame = tk.Frame(root, bg="#eef4ff", padx=16, pady=12)
    frame.pack(fill="x")

    city_label = tk.Label(frame, text="City:", font=("Segoe UI", 12, "bold"), bg="#eef4ff", fg="#1f2937")
    city_label.grid(row=0, column=0, sticky="w")

    city_var = tk.StringVar()
    city_entry = tk.Entry(frame, textvariable=city_var, font=("Segoe UI", 12), width=26, bd=2, relief="solid")
    city_entry.grid(row=0, column=1, sticky="w", padx=(8, 0))
    city_entry.focus()

    button_bg = "#4f7ded"
    button_fg = "white"

    search_button = tk.Button(frame, text="Search", command=lambda: on_search(), font=("Segoe UI", 11), bg=button_bg, fg=button_fg, activebackground="#3a61c2", activeforeground="white", bd=0, padx=14, pady=8)
    search_button.grid(row=0, column=2, padx=(14, 0))

    detect_button = tk.Button(frame, text="Auto Detect", command=lambda: on_auto_detect(), font=("Segoe UI", 11), bg="#10b981", fg=button_fg, activebackground="#0f9e6a", activeforeground="white", bd=0, padx=14, pady=8)
    detect_button.grid(row=0, column=3, padx=(10, 0))

    refresh_button = tk.Button(frame, text="Refresh", command=lambda: on_refresh(), font=("Segoe UI", 11), bg="#f59e0b", fg=button_fg, activebackground="#d97706", activeforeground="white", bd=0, padx=14, pady=8)
    refresh_button.grid(row=0, column=4, padx=(10, 0))

    clear_button = tk.Button(frame, text="Clear", command=lambda: on_clear(), font=("Segoe UI", 11), bg="#ef4444", fg=button_fg, activebackground="#dc2626", activeforeground="white", bd=0, padx=14, pady=8)
    clear_button.grid(row=0, column=5, padx=(10, 0))

    exit_button = tk.Button(frame, text="Exit", command=root.destroy, font=("Segoe UI", 11), bg="#6b7280", fg=button_fg, activebackground="#4b5563", activeforeground="white", bd=0, padx=14, pady=8)
    exit_button.grid(row=0, column=6, padx=(10, 0))

    status_label = tk.Label(frame, text="Enter a city or click Auto Detect.", font=("Segoe UI", 10), bg="#eef4ff", fg="#374151")
    status_label.grid(row=1, column=0, columnspan=7, pady=(10, 0), sticky="w")

    report_frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
    report_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    report_text = tk.Text(report_frame, wrap="word", padx=16, pady=16, font=("Consolas", 12), bg="#f8fbff", fg="#111827", bd=0, state="disabled")
    report_text.pack(expand=True, fill="both")

    last_search = {
        "city": "",
        "auto": False,
        "detected_place": None,
    }

    def fetch_and_show(city_name: str | None = None, auto: bool = False):
        try:
            status_label.configure(text="Fetching weather…", fg="#2563eb")
            root.update_idletasks()

            if auto or not city_name:
                location = detect_location()
                detected_place = format_detected_place(location)
                report = get_weather_report(
                    latitude=location["latitude"],
                    longitude=location["longitude"],
                    auto=True,
                    detected_place=detected_place,
                )
                last_search.update({"city": "", "auto": True, "detected_place": detected_place})
            else:
                report = get_weather_report(city=city_name)
                last_search.update({"city": city_name, "auto": False, "detected_place": None})

            update_report_text(report_text, report)
            status_label.configure(text=f"Showing weather for {city_name or 'your detected location'}.", fg="#065f46")
        except Exception as error:
            messagebox.showerror("Weather App", str(error))
            status_label.configure(text="Failed to load weather. Try again.", fg="#b91c1c")

    def on_search() -> None:
        city_name = city_var.get().strip()
        if not city_name:
            messagebox.showinfo("Weather App", "Please enter a city name or use Auto Detect.")
            return
        fetch_and_show(city_name, auto=False)

    def on_auto_detect() -> None:
        fetch_and_show(auto=True)

    def on_refresh() -> None:
        if not last_search["city"]:
            messagebox.showinfo("Weather App", "No weather result to refresh yet.")
            return
        fetch_and_show(last_search["city"], auto=last_search["auto"])

    def on_clear() -> None:
        update_report_text(report_text, "")
        status_label.configure(text="Enter a city or click Auto Detect.", fg="#374151")
        city_var.set("")

    city_entry.bind("<Return>", lambda event: on_search())
    root.mainloop()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def show_weather(
    city: str,
    auto: bool = False,
    detected_place: str | None = None,
    quiet: bool = False,
    gui: bool = False,
) -> None:
    """Fetch and display full weather report for a city."""
    try:
        raw_data = fetch_weather_data(city)
        current  = parse_current_weather(raw_data)
        forecast = parse_forecast(raw_data)

        if gui:
            show_weather_app(current, forecast, auto=auto, detected_place=detected_place)
            return

        if not quiet:
            print(f"\n  ⏳ Fetching weather for '{city}'...\n")
        print_current_weather(current, auto=auto, detected_place=detected_place)
        print_forecast(forecast)
    except ValueError as error:
        if gui:
            messagebox.showerror("Weather App", str(error))
        else:
            print(f"\n  ❌  {error}\n")
    except ConnectionError as error:
        if gui:
            messagebox.showerror("Weather App", str(error))
        else:
            print(f"\n  📡  {error}\n")


def format_detected_place(location: dict) -> str:
    return ", ".join(
        part for part in [
            location.get("city", ""),
            location.get("region", ""),
            location.get("country", ""),
        ] if part
    )


def run() -> None:
    build_weather_app()


if __name__ == "__main__":
    run()