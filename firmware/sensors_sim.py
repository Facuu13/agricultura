import math
import time


def _base_t() -> float:
    return time.ticks_ms() / 1000.0 if hasattr(time, "ticks_ms") else time.time() % 10000


def read_simulated() -> tuple[float, float, float, float]:
    """Devuelve soil_moisture %, rain_mm (incremento), wind m/s, radiation W/m²."""
    t = _base_t()
    soil = 42.0 + 8.0 * math.sin(t / 17.0) + (time.ticks_ms() % 97) / 97.0
    soil = max(5.0, min(95.0, soil))
    rain = max(0.0, (math.sin(t / 23.0) + 1.0) * 0.15)
    wind = 3.0 + abs(6.0 * math.sin(t / 11.0))
    radiation = 350.0 + 450.0 * max(0.0, math.sin(t / 40.0))
    return soil, rain, wind, radiation
