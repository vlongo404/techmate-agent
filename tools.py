import time
import psutil
import requests


def get_system_stats() -> dict:
    """
    Returns current system resource usage: CPU, RAM, disk, and top processes.

    Use when the user asks about:
    - CPU usage or load
    - Memory or RAM usage
    - Disk space or storage
    - System performance or resource consumption
    - Which processes are using most resources

    Returns a dict with:
    - cpu_percent: CPU usage percentage
    - ram_total_gb, ram_used_gb, ram_percent
    - disk_total_gb, disk_used_gb, disk_percent
    - top_processes: 5 processes with highest CPU usage
    """
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    top_procs = sorted(
        processes, key=lambda x: x.get("cpu_percent") or 0, reverse=True
    )[:5]

    return {
        "cpu_percent": cpu,
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_percent": ram.percent,
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_percent": round(disk.percent, 1),
        "top_processes": top_procs,
    }


def get_weather(city: str) -> dict:
    """
    Returns current weather for a city using the Open-Meteo API (no API key needed).

    Use when the user asks about:
    - Weather in any city
    - Current temperature
    - Humidity, wind speed, or weather conditions
    - Whether it is raining or sunny somewhere

    Parameters:
    - city: City name in any language (e.g., "São Paulo", "Tokyo", "London")

    Returns a dict with temperature, feels-like, humidity, wind speed, and condition.
    """
    geo_url = (
        f"https://geocoding-api.open-meteo.com/v1/search"
        f"?name={city}&count=1&language=pt&format=json"
    )

    wmo_descriptions = {
        0: "Céu limpo", 1: "Predominantemente limpo", 2: "Parcialmente nublado",
        3: "Nublado", 45: "Névoa", 48: "Névoa com geada",
        51: "Garoa leve", 53: "Garoa moderada", 55: "Garoa intensa",
        61: "Chuva fraca", 63: "Chuva moderada", 65: "Chuva forte",
        71: "Neve fraca", 73: "Neve moderada", 75: "Neve intensa",
        80: "Pancadas fracas", 81: "Pancadas moderadas", 82: "Pancadas fortes",
        95: "Trovoada", 96: "Trovoada com granizo", 99: "Trovoada intensa",
    }

    try:
        geo_resp = requests.get(geo_url, timeout=10)
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return {"city": city, "error": "Cidade não encontrada"}

        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        country = loc.get("country", "")

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            f"weather_code,wind_speed_10m"
            f"&timezone=auto"
        )

        w_resp = requests.get(weather_url, timeout=10)
        current = w_resp.json().get("current", {})
        code = current.get("weather_code", 0)

        return {
            "city": f"{loc['name']}, {country}",
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "condition": wmo_descriptions.get(code, f"Código WMO {code}"),
        }

    except requests.RequestException as e:
        return {"city": city, "error": str(e)}


def get_crypto_price(symbol: str) -> dict:
    """
    Returns current price and market data for a cryptocurrency via CoinGecko API.

    Use when the user asks about:
    - Price of Bitcoin, Ethereum, Solana, or any cryptocurrency
    - Crypto market data, 24h change, market cap, or volume
    - How much a cryptocurrency costs in USD or BRL

    Parameters:
    - symbol: Coin symbol or name (e.g., "btc", "bitcoin", "eth", "ethereum", "sol")

    Returns price in USD and BRL, 24h change percentage, market cap, and volume.
    """
    aliases = {
        "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
        "bnb": "binancecoin", "xrp": "ripple", "ada": "cardano",
        "doge": "dogecoin", "dot": "polkadot", "avax": "avalanche-2",
        "matic": "matic-network", "link": "chainlink", "ltc": "litecoin",
    }

    coin_id = aliases.get(symbol.lower(), symbol.lower())

    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": coin_id,
                "price_change_percentage": "24h",
            },
            timeout=10,
        )
        data = resp.json()

        if not data:
            return {"symbol": symbol, "error": "Criptomoeda não encontrada. Tente usar o nome completo (ex: 'bitcoin')"}

        coin = data[0]

        brl_resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "brl"},
            timeout=10,
        )
        price_brl = brl_resp.json().get(coin_id, {}).get("brl")

        return {
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "price_usd": coin.get("current_price"),
            "price_brl": price_brl,
            "change_24h_percent": round(coin.get("price_change_percentage_24h") or 0, 2),
            "market_cap_usd": coin.get("market_cap"),
            "volume_24h_usd": coin.get("total_volume"),
            "high_24h_usd": coin.get("high_24h"),
            "low_24h_usd": coin.get("low_24h"),
        }

    except requests.RequestException as e:
        return {"symbol": symbol, "error": str(e)}


def check_website_health(url: str) -> dict:
    """
    Checks if a website or HTTP endpoint is online, measuring response time and status.

    Use when the user asks about:
    - Whether a website or URL is online/accessible
    - HTTP status code of a page
    - Response time or latency of a website
    - If a server is responding correctly

    Parameters:
    - url: Full URL to check (e.g., "https://google.com", "http://example.com")
          If no scheme is provided, https:// is assumed.

    Returns online status, HTTP status code, response time in ms, and server headers.
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        start = time.time()
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": "Spectra AI-HealthCheck/1.0"},
        )
        elapsed_ms = round((time.time() - start) * 1000, 2)

        return {
            "url": url,
            "online": True,
            "status_code": response.status_code,
            "status_ok": response.ok,
            "response_time_ms": elapsed_ms,
            "content_type": response.headers.get("Content-Type", "desconhecido"),
            "server": response.headers.get("Server", "desconhecido"),
            "final_url": response.url if response.url != url else None,
            "size_kb": round(len(response.content) / 1024, 2),
        }

    except requests.ConnectionError:
        return {"url": url, "online": False, "error": "Falha na conexão — host inacessível"}
    except requests.Timeout:
        return {"url": url, "online": False, "error": "Timeout — servidor demorou mais de 10s"}
    except requests.RequestException as e:
        return {"url": url, "online": False, "error": str(e)}
