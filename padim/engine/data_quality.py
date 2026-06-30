"""
PADIM — Sistema de Frescura y Calidad de Datos v2.0.0
Convierte datos basura (listings muertos) en información útil mediante:
1. Freshness scoring con decaimiento exponencial
2. Cross-source confirmation scoring
3. Source trust decay (usa SOURCE_TRUST_WEIGHTS unificado)
4. Estimación de confianza por propiedad
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Usar weights unificados del trust_engine
from padim.engine.trust_engine import SOURCE_TRUST_WEIGHTS

logger = logging.getLogger("padim.data_quality")

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

# Si una fuente no actualiza en X días, su trust se penaliza
SOURCE_STALE_DAYS: Dict[str, int] = {
    "vivanuncios": 7,
    "easybroker": 14,
    "inmuebles24": 7,
    "propiedades_com": 7,
    "mls": 30,
}

# Decaimiento: media vida en días para una propiedad no revisitada
FRESHNESS_HALF_LIFE_DAYS = 14

# Scoring
QualityGrade = Enum("QualityGrade", ["EXCELLENT", "GOOD", "FAIR", "POOR", "STALE", "TRASH"])


@dataclass
class PropertyQuality:
    """Score de calidad para una propiedad"""
    property_id: str
    source: str
    source_trust: float
    days_since_update: float
    freshness_score: float
    cross_source_count: int
    cross_source_score: float
    price_consistency_score: float
    overall_quality: float
    grade: QualityGrade
    is_usable: bool
    reason: str = ""


# ═══════════════════════════════════════════════════════════════
# FRESHNESS SCORING
# ═══════════════════════════════════════════════════════════════

def compute_freshness(
    last_updated: Optional[datetime],
    source: str,
    half_life_days: float = FRESHNESS_HALF_LIFE_DAYS
) -> Tuple[float, float]:
    """
    Calcula el freshness score de una propiedad.
    Usa decaimiento exponencial: score = 2^(-dias / half_life)
    """
    if not last_updated:
        return (0.0, 999)

    now = datetime.now(timezone.utc)
    if last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=timezone.utc)

    delta = now - last_updated
    days = delta.total_seconds() / 86400.0

    if days < 0:
        days = 0

    freshness = 2.0 ** (-days / half_life_days)

    stale_days = SOURCE_STALE_DAYS.get(source, 14)
    if days > stale_days and freshness > 0.3:
        freshness *= 0.7

    return (min(freshness, 1.0), days)


def compute_source_trust(source: str, days_since_last_seen: float) -> float:
    """
    Calcula el trust score de una fuente usando SOURCE_TRUST_WEIGHTS unificado.
    """
    base = SOURCE_TRUST_WEIGHTS.get(source, 0.30)

    if days_since_last_seen > 30:
        base *= 0.5
    elif days_since_last_seen > 7:
        base *= 0.8

    return max(0.05, min(base, 1.0))


# ═══════════════════════════════════════════════════════════════
# CROSS-SOURCE CONFIRMATION
# ═══════════════════════════════════════════════════════════════

def compute_cross_source_score(
    total_sources: int,
    active_sources: int,
    price_range: Optional[float] = None
) -> Tuple[float, int]:
    """
    Calcula qué tan confirmada está una propiedad por múltiples fuentes.
    """
    if total_sources == 0:
        return (0.0, 0)

    active_ratio = active_sources / total_sources if total_sources > 0 else 0

    if total_sources >= 3:
        source_count_score = 1.0
    elif total_sources == 2:
        source_count_score = 0.7
    else:
        source_count_score = 0.3

    score = (active_ratio * 0.6 + source_count_score * 0.4)

    if price_range is not None and price_range > 0.3:
        score *= 0.7

    return (min(score, 1.0), active_sources)


# ═══════════════════════════════════════════════════════════════
# OVERALL QUALITY SCORE
# ═══════════════════════════════════════════════════════════════

def compute_overall_quality(
    freshness: float,
    source_trust: float,
    cross_source: float,
    has_price: bool = True,
    has_location: bool = True,
    has_images: bool = False,
) -> PropertyQuality:
    """
    Calcula el score de calidad compuesto.
    Pesos: Freshness 35%, Source trust 25%, Cross-source 25%, Completeness 15%
    """
    completeness = 0.0
    if has_price:
        completeness += 0.5
    if has_location:
        completeness += 0.3
    if has_images:
        completeness += 0.2

    overall = (
        freshness * 0.35 +
        source_trust * 0.25 +
        cross_source * 0.25 +
        completeness * 0.15
    )
    overall = max(0.0, min(overall, 1.0))

    if overall >= 0.8:
        grade = QualityGrade.EXCELLENT
        reason = "Dato fresco, fuente confiable, múltiples fuentes lo confirman"
    elif overall >= 0.6:
        grade = QualityGrade.GOOD
        reason = "Dato aceptable con confirmación parcial"
    elif overall >= 0.4:
        grade = QualityGrade.FAIR
        reason = "Dato usable pero requiere verificación"
    elif overall >= 0.2:
        grade = QualityGrade.POOR
        reason = "Dato probablemente desactualizado o no confirmado"
    elif overall >= 0.05:
        grade = QualityGrade.STALE
        reason = "Dato muy viejo, probablemente ya no es válido"
    else:
        grade = QualityGrade.TRASH
        reason = "Dato inservible sin fecha ni fuente confiable"

    return PropertyQuality(
        property_id="",
        source="",
        source_trust=source_trust,
        days_since_update=0,
        freshness_score=freshness,
        cross_source_count=0,
        cross_source_score=cross_source,
        price_consistency_score=1.0,
        overall_quality=overall,
        grade=grade,
        is_usable=overall > 0.3,
        reason=reason,
    )


# ═══════════════════════════════════════════════════════════════
# ESTIMACIÓN DE PRECIO CON DATOS RUIDOSOS (AVM LITE)
# ═══════════════════════════════════════════════════════════════

def estimate_price_robust(
    prices: List[float],
    confidence_scores: List[float]
) -> Dict:
    """
    Estima el precio de mercado usando solo datos de alta calidad.
    """
    if not prices:
        return {"estimated_price": None, "confidence": 0, "sample_size": 0}

    valid = [(p, c) for p, c in zip(prices, confidence_scores) if c > 0.3 and p > 0]

    if len(valid) < 3:
        return {"estimated_price": None, "confidence": 0, "sample_size": len(valid)}

    valid_prices = [p for p, _ in valid]
    valid_confidence = [c for _, c in valid]

    sorted_prices = sorted(valid_prices)
    n = len(sorted_prices)
    median = sorted_prices[n // 2] if n % 2 == 1 else (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2

    weighted_avg = sum(p * c for p, c in valid) / sum(valid_confidence)

    price_range = (max(valid_prices) - min(valid_prices)) / median if median > 0 else 1
    confidence = sum(valid_confidence) / len(valid_confidence)

    if price_range > 0.5:
        confidence *= 0.7

    return {
        "estimated_price": round(weighted_avg, 2),
        "median_price": round(median, 2),
        "price_range": round(price_range, 2),
        "confidence": round(min(confidence, 1.0), 2),
        "sample_size": len(valid),
        "min_price": min(valid_prices),
        "max_price": max(valid_prices),
    }


def demo():
    """Ejecuta una demo del sistema de calidad"""
    now = datetime.now(timezone.utc)

    test_cases = [
        (now - timedelta(days=2), "vivanuncios", 3, True, True, True),
        (now - timedelta(days=10), "vivanuncios", 2, True, True, False),
        (now - timedelta(days=30), "vivanuncios", 1, True, True, False),
        (now - timedelta(days=90), "easybroker", 1, True, True, True),
        (now - timedelta(days=730), "easybroker", 1, True, False, False),
        (None, "easybroker", 0, False, False, False),
    ]

    print(f"{'FRESCURA':>8} | {'FUENTE':>15} | {'CONF':>5} | {'GRADO':>10} | {'USABLE':>7} | RAZÓN")
    print("-" * 90)

    for last_upd, source, cross, has_p, has_l, has_i in test_cases:
        freshness, days = compute_freshness(last_upd, source)
        source_trust = compute_source_trust(source, days)
        cross_score, _ = compute_cross_source_score(cross, cross, 0.1)
        quality = compute_overall_quality(freshness, source_trust, cross_score, has_p, has_l, has_i)

        print(f"{freshness:>7.2f} | {source:>15} | {quality.overall_quality:>4.2f} | {quality.grade.name:>10} | {str(quality.is_usable):>7} | {quality.reason[:30]}")

    print()
    print("=== ESTIMACIÓN DE PRECIO ===")
    prices = [4500000, 4800000, 4200000, 5500000, 300000]
    confidence = [0.8, 0.7, 0.6, 0.5, 0.1]
    result = estimate_price_robust(prices, confidence)
    print(f"Precios: {prices}")
    print(f"Confianzas: {confidence}")
    print(f"Estimación: ${result['estimated_price']:,.0f}")
    print(f"Mediana: ${result['median_price']:,.0f}")
    print(f"Confianza estimación: {result['confidence']}")
    print(f"Muestras válidas: {result['sample_size']}/{len(prices)}")


if __name__ == "__main__":
    demo()
