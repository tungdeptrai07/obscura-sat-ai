"""ObscuraSat EarthWatch: Multi-spectral NDVI, NDWI, NDBI & change-detection pipeline."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SpectralBandSample:
    region_id: str
    red: float
    green: float
    nir: float
    swir: float


def safe_ratio(a: float, b: float) -> float:
    denom = a + b
    return round((a - b) / denom, 4) if denom != 0 else 0.0


def compute_indices(sample: SpectralBandSample) -> Dict[str, float]:
    ndvi = safe_ratio(sample.nir, sample.red)
    ndwi = safe_ratio(sample.green, sample.nir)
    ndbi = safe_ratio(sample.swir, sample.nir)
    return {"ndvi": ndvi, "ndwi": ndwi, "ndbi": ndbi}


def classify_change(t1: SpectralBandSample, t2: SpectralBandSample) -> Dict[str, object]:
    i1, i2 = compute_indices(t1), compute_indices(t2)
    d_ndvi = round(i2["ndvi"] - i1["ndvi"], 4)
    d_ndbi = round(i2["ndbi"] - i1["ndbi"], 4)
    alert = "Vegetation Loss / Urbanization" if d_ndvi < -0.15 and d_ndbi > 0.10 else (
        "Vegetation Recovery" if d_ndvi > 0.15 else "Stable Land Cover"
    )
    return {"region": t1.region_id, "t1": i1, "t2": i2, "delta_ndvi": d_ndvi, "delta_ndbi": d_ndbi, "status": alert}


if __name__ == "__main__":
    samples: List[tuple] = [
        (SpectralBandSample("Mekong-Delta-01", 0.12, 0.15, 0.58, 0.22),
         SpectralBandSample("Mekong-Delta-01", 0.21, 0.16, 0.34, 0.38)),
    ]
    for a, b in samples:
        print(classify_change(a, b))
