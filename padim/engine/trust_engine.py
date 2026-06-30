"""
PADIM — Sistema de Inteligencia y Confianza de Datos (Data Trust Engine) v2.0.0

NO es un sistema de calidad de datos tradicional.
Es un sistema de SEÑALES que aprende, evoluciona y se adapta.

Filosofía:
- Todos los datos son señales, ninguna es verdad absoluta
- La confianza se gana, no se asigna
- El fraude, listings fantasma, y datos corruptos se detectan por patrón, no por regla
- El sistema madura con el tiempo: más datos = mejores decisiones
"""
import logging
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("padim.trust_engine")

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN UNIFICADA DE CONFIANZA POR FUENTE
# ═══════════════════════════════════════════════════════════════

SOURCE_TRUST_WEIGHTS: Dict[str, float] = {
    "vivanuncios": 0.60,       # Portal abierto, datos públicos, actualización regular
    "inmuebles24": 0.55,       # Similar a Vivanuncios
    "propiedades_com": 0.50,   # Portal con mezcla de datos
    "metroscubicos": 0.45,     # Absorbido por ML
    "easybroker": 0.30,        # Red B2B agente-agente, listings muertos CONFIRMADO
    "mls": 0.40,               # Sintético
    "shf": 0.95,               # SHF = Sociedad Hipotecaria Federal (transacciones REALES)
    "catastro": 0.90,          # Registro público de propiedad
    "notarias": 0.85,          # Escrituras
    "avu": 0.98,               # Avalúos bancarios (realmente verificados)
    "inegi": 0.85,             # INEGI (datos censales)
    "contribucion_directa": 0.70,  # Contribución directa de la comunidad
}


# ═══════════════════════════════════════════════════════════════
# MODELO DE SEÑALES
# ═══════════════════════════════════════════════════════════════

class SignalType(Enum):
    """Tipos de señales que el sistema puede identificar"""
    LISTING_ACTIVE = "listing_active"
    LISTING_UPDATED = "listing_updated"
    PRICE_CHANGED = "price_changed"
    PRICE_ANOMALY = "price_anomaly"
    MULTI_SOURCE = "multi_source"
    CROSS_CONFIRMED = "cross_confirmed"
    SOURCE_TRUST_DECAY = "source_trust_decay"
    GHOST_LISTING = "ghost_listing"
    FRAUD_SUSPECTED = "fraud_suspected"
    VENDOR_STRATEGY = "vendor_strategy"
    SOLD_LIKELY = "sold_likely"
    PRICE_MANIPULATION = "price_manipulation"
    AGENT_BEHAVIOR = "agent_behavior"


@dataclass
class Signal:
    """Una señal individual detectada por el sistema"""
    type: SignalType
    strength: float                # 0-1: qué tan fuerte es la señal
    confidence: float              # 0-1: qué tan seguros estamos
    source: str                    # Qué lo generó
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: Dict[str, Any] = field(default_factory=dict)

    @property
    def weight(self) -> float:
        """Peso combinado de la señal"""
        return self.strength * self.confidence


@dataclass
class PropertyIntelligence:
    """Perfil de inteligencia para una propiedad"""
    property_id: str
    signals: List[Signal] = field(default_factory=list)
    trust_score: float = 0.0       # 0-1: score compuesto de confianza
    is_relevant: bool = False      # Si debe mostrarse en búsquedas
    is_suspicious: bool = False    # Si hay señales de fraude/engaño
    estimated_real_price: Optional[float] = None
    listing_price_deviation: Optional[float] = None
    last_verified: Optional[datetime] = None

    def add_signal(self, signal: Signal):
        self.signals.append(signal)
        self._recalculate()

    def _recalculate(self):
        """Recalcula el score basado en todas las señales"""
        base_score = 0.7

        if not self.signals:
            self.trust_score = base_score
            self.is_relevant = True
            self.is_suspicious = False
            return

        positive_strength = sum(
            s.weight for s in self.signals
            if s.type in (SignalType.LISTING_UPDATED, SignalType.CROSS_CONFIRMED,
                         SignalType.PRICE_CHANGED, SignalType.MULTI_SOURCE,
                         SignalType.LISTING_ACTIVE)
        )

        negative_strength = sum(
            s.weight for s in self.signals
            if s.type in (SignalType.GHOST_LISTING, SignalType.FRAUD_SUSPECTED,
                         SignalType.VENDOR_STRATEGY, SignalType.PRICE_ANOMALY,
                         SignalType.PRICE_MANIPULATION)
        )

        positive_boost = positive_strength * 0.3
        negative_penalty = negative_strength * 1.0

        self.trust_score = max(0.0, min(1.0, base_score + positive_boost - negative_penalty))
        self.is_relevant = self.trust_score > 0.3 and not any(
            s.type == SignalType.FRAUD_SUSPECTED for s in self.signals
        )
        self.is_suspicious = any(
            s.type in (SignalType.FRAUD_SUSPECTED, SignalType.PRICE_MANIPULATION)
            for s in self.signals
        )


# ═══════════════════════════════════════════════════════════════
# DETECTORES DE SEÑALES
# ═══════════════════════════════════════════════════════════════

class GhostListingDetector:
    """Detecta propiedades FANTASMA: anuncios que nunca se actualizan."""
    STALE_DAYS = 90
    GHOST_THRESHOLD = 180

    @staticmethod
    def detect(
        last_updated: Optional[datetime],
        days_on_market: Optional[int],
        price_changes: int,
        source_count: int,
    ) -> Optional[Signal]:
        if not last_updated:
            return None

        now = datetime.now(timezone.utc)
        if last_updated.tzinfo is None:
            last_updated = last_updated.replace(tzinfo=timezone.utc)

        days_since = (now - last_updated).total_seconds() / 86400.0

        if days_since < GhostListingDetector.STALE_DAYS:
            return None

        strength = min(1.0, days_since / GhostListingDetector.GHOST_THRESHOLD)

        return Signal(
            type=SignalType.GHOST_LISTING,
            strength=strength,
            confidence=0.8 if days_since > GhostListingDetector.GHOST_THRESHOLD else 0.5,
            source="ghost_detector",
            evidence={
                "days_since_update": round(days_since, 1),
                "price_changes": price_changes,
                "sources": source_count,
            }
        )


class PriceAnomalyDetector:
    """Detecta anomalías de precio."""
    PRICE_RANGES = {
        "departamento": (5000, 120000),
        "casa": (3000, 80000),
        "terreno": (500, 50000),
        "local": (5000, 80000),
        "oficina": (5000, 70000),
        "bodega": (1000, 30000),
    }

    @staticmethod
    def detect(
        price: Optional[float],
        price_m2: Optional[float],
        property_type: str,
        colony_market_price_m2: Optional[float],
    ) -> List[Signal]:
        signals = []

        if not price or price <= 0:
            return signals

        if price_m2 and property_type in PriceAnomalyDetector.PRICE_RANGES:
            min_m2, max_m2 = PriceAnomalyDetector.PRICE_RANGES[property_type]
            if price_m2 < min_m2 * 0.3:
                signals.append(Signal(
                    type=SignalType.PRICE_ANOMALY,
                    strength=0.7,
                    confidence=0.6,
                    source="price_anomaly_detector",
                    evidence={
                        "reason": "price_below_minimum",
                        "price_m2": price_m2,
                        "expected_min_m2": min_m2,
                        "deviation_pct": round((1 - price_m2 / min_m2) * 100, 1),
                    }
                ))

            if price_m2 > max_m2 * 1.5:
                signals.append(Signal(
                    type=SignalType.PRICE_ANOMALY,
                    strength=0.4,
                    confidence=0.5,
                    source="price_anomaly_detector",
                    evidence={
                        "reason": "price_above_maximum",
                        "price_m2": price_m2,
                        "expected_max_m2": max_m2,
                    }
                ))

        if colony_market_price_m2 and price_m2:
            deviation = abs(price_m2 - colony_market_price_m2) / colony_market_price_m2
            if deviation > 0.5:
                signals.append(Signal(
                    type=SignalType.PRICE_ANOMALY,
                    strength=min(1.0, deviation),
                    confidence=0.5,
                    source="market_deviation",
                    evidence={
                        "reason": "market_deviation",
                        "listing_price_m2": price_m2,
                        "market_avg_m2": colony_market_price_m2,
                        "deviation_pct": round(deviation * 100, 1),
                    }
                ))

        return signals


class VendorBehaviorDetector:
    """Detecta patrones de comportamiento de vendedores/agentes."""

    @staticmethod
    def detect_lead_collector(
        agent_name: Optional[str],
        properties_count: int,
        avg_price_m2: Optional[float],
        market_price_m2: Optional[float],
    ) -> Optional[Signal]:
        if not agent_name or properties_count < 5:
            return None

        if avg_price_m2 and market_price_m2 and avg_price_m2 < market_price_m2 * 0.7:
            return Signal(
                type=SignalType.VENDOR_STRATEGY,
                strength=0.6,
                confidence=0.5,
                source="vendor_behavior_detector",
                evidence={
                    "agent": agent_name,
                    "properties_count": properties_count,
                    "avg_price_m2": avg_price_m2,
                    "market_price_m2": market_price_m2,
                    "pattern": "lead_collector_low_prices",
                }
            )

        return None


class FraudDetector:
    """Detecta posibles fraudes."""
    FRAUD_KEYWORDS = [
        "remate", "litigio", "herencia", "herederos",
        "urge vender", "precio remate", "oportunidad única",
        "dueño directo", "sin intermediarios", "precio negociable",
        "remate bancario", "adjudicado", "juicio",
    ]

    @staticmethod
    def detect(title: str, description: str, price_m2: float, market_m2: float) -> List[Signal]:
        signals = []

        text = f"{title} {description}".lower()
        found_keywords = [kw for kw in FraudDetector.FRAUD_KEYWORDS if kw in text]

        if found_keywords:
            signals.append(Signal(
                type=SignalType.FRAUD_SUSPECTED,
                strength=min(1.0, len(found_keywords) * 0.15),
                confidence=0.4,
                source="fraud_detector",
                evidence={"keywords_found": found_keywords}
            ))

        if found_keywords and price_m2 and market_m2 and price_m2 < market_m2 * 0.3:
            signals.append(Signal(
                type=SignalType.FRAUD_SUSPECTED,
                strength=0.9,
                confidence=0.6,
                source="fraud_detector",
                evidence={
                    "reason": "low_price_with_fraud_keywords",
                    "price_m2": price_m2,
                    "market_m2": market_m2,
                    "keywords": found_keywords,
                }
            ))

        return signals


# ═══════════════════════════════════════════════════════════════
# ORQUESTADOR DE INTELIGENCIA
# ═══════════════════════════════════════════════════════════════

class TrustEngine:
    """
    Motor de confianza que orquesta todos los detectores.

    Pipeline:
    1. Recibir propiedad (con todos sus metadatos)
    2. Ejecutar detectores
    3. Recolectar señales
    4. Calcular trust score
    5. Decidir: usable / sospechosa / fraude
    """

    def __init__(self):
        self.detectores = {
            "ghost": GhostListingDetector(),
            "price": PriceAnomalyDetector(),
            "vendor": VendorBehaviorDetector(),
            "fraud": FraudDetector(),
        }
        # Memoria del sistema (aprende con el tiempo)
        self.agent_trust: Dict[str, float] = {}
        self.colony_market: Dict[str, float] = {}

    def analyze(
        self,
        property_id: str,
        source: str,
        title: str,
        description: str,
        price: Optional[float] = None,
        price_m2: Optional[float] = None,
        property_type: str = "otro",
        last_updated: Optional[datetime] = None,
        days_on_market: Optional[int] = None,
        price_changes: int = 0,
        source_count: int = 1,
        colony: Optional[str] = None,
        municipality: Optional[str] = None,
        agent_name: Optional[str] = None,
        agent_properties_count: int = 0,
    ) -> PropertyIntelligence:

        intelligence = PropertyIntelligence(property_id=property_id)

        # 1. Ghost listing detection
        signal = self.detectores["ghost"].detect(
            last_updated, days_on_market, price_changes, source_count
        )
        if signal:
            intelligence.add_signal(signal)

        # 2. Price anomaly detection
        colony_key = f"{colony},{municipality}" if colony and municipality else None
        market_m2 = self.colony_market.get(colony_key, None)

        for signal in self.detectores["price"].detect(price, price_m2, property_type, market_m2):
            intelligence.add_signal(signal)

        # 3. Vendor behavior detection
        signal = self.detectores["vendor"].detect_lead_collector(
            agent_name, agent_properties_count, price_m2, market_m2
        )
        if signal:
            intelligence.add_signal(signal)

        # 4. Fraud detection
        market_m2_val = market_m2 or 50000
        for signal in self.detectores["fraud"].detect(
            title, description, price_m2 or 0, market_m2_val
        ):
            intelligence.add_signal(signal)

        # 5. Source trust adjustment
        source_trust = SOURCE_TRUST_WEIGHTS.get(source, 0.5)
        if not intelligence.is_suspicious:
            intelligence.trust_score *= source_trust

        # Asegurar recálculo incluso sin señales
        intelligence._recalculate()

        return intelligence


def compute_trust_score(
    property_id: str,
    source: str = "unknown",
    title: str = "",
    description: str = "",
    price: Optional[float] = None,
    **kwargs
) -> float:
    """Función helper de un solo llamado para calcular trust score."""
    engine = TrustEngine()
    result = engine.analyze(
        property_id=property_id,
        source=source,
        title=title,
        description=description,
        price=price,
        **kwargs
    )
    return result.trust_score


def demo():
    """Ejecuta una demo del Trust Engine."""
    engine = TrustEngine()

    test_cases = [
        {
            "name": "EasyBroker ghost (2 años sin update)",
            "property_id": "EB-123",
            "source": "easybroker",
            "title": "Hermoso departamento en Polanco",
            "description": "Oportunidad única, remate bancario",
            "price": 3500000,
            "price_m2": 25000,
            "property_type": "departamento",
            "last_updated": datetime.now(timezone.utc) - timedelta(days=730),
            "days_on_market": 730,
            "source_count": 1,
            "colony": "Polanco",
            "municipality": "Miguel Hidalgo",
            "agent_name": "José Pérez",
            "agent_properties_count": 50,
        },
        {
            "name": "Vivanuncios fresca (2 días)",
            "property_id": "VV-456",
            "source": "vivanuncios",
            "title": "Casa en renta en Lomas de Chapultepec",
            "description": "Casa de 3 recámaras con jardín, lista para habitar",
            "price": 45000,
            "price_m2": 35000,
            "property_type": "casa",
            "last_updated": datetime.now(timezone.utc) - timedelta(days=2),
            "days_on_market": 15,
            "source_count": 2,
            "colony": "Lomas de Chapultepec",
            "municipality": "Miguel Hidalgo",
            "agent_name": "María López",
            "agent_properties_count": 3,
        },
        {
            "name": "Posible fraude (precio bajo + keywords)",
            "property_id": "FR-789",
            "source": "vivanuncios",
            "title": "Remate bancario, urge vender, oportunidad única",
            "description": "Herencia, remate judicial, precio increíble, dueño directo",
            "price": 500000,
            "price_m2": 3000,
            "property_type": "departamento",
            "last_updated": datetime.now(timezone.utc) - timedelta(days=180),
            "days_on_market": 180,
            "source_count": 1,
            "colony": "Condesa",
            "municipality": "Cuauhtémoc",
            "agent_name": "Luis Martínez",
            "agent_properties_count": 30,
        },
    ]

    print(f"{'CASO':<30} | {'TRUST':>6} | {'RELEVANTE':>9} | {'SOSPECHA':>8} | SEÑALES")
    print("=" * 100)
    for tc in test_cases:
        result = engine.analyze(**tc)
        signals = ", ".join(s.type.value for s in result.signals) or "ninguna"
        print(f"{tc['name'][:28]:<30} | {result.trust_score:>5.2f} | {str(result.is_relevant):>9} | {str(result.is_suspicious):>8} | {signals[:30]}")

    print()
    print("=== Trust Score Helper ===")
    score = compute_trust_score(
        property_id="test-1",
        source="vivanuncios",
        title="Casa en Condesa",
        description="Hermosa casa remodelada",
        price=8500000,
        price_m2=45000,
        property_type="casa",
    )
    print(f"Trust score: {score:.2f}")

    return engine


if __name__ == "__main__":
    demo()
