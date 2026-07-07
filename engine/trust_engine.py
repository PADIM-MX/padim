"""
BACKBONE — Sistema de Inteligencia y Confianza de Datos (Data Trust Engine)
v1.0.0

NO es un sistema de calidad de datos tradicional.
Es un sistema de SEÑALES que aprende, evoluciona y se adapta.

Filosofía:
- Todos los datos son señales, ninguna es verdad absoluta
- La confianza se gana, no se asigna
- El fraude, listings fantasma, y datos corruptos se detectan por patrón, no por regla
- El sistema madura con el tiempo: más datos = mejores decisiones

Factores que el sistema debe considerar (según análisis del fundador):
1. Una propiedad listada 5 años NO es relevante
2. Muchas interacciones NO garantizan relevancia
3. Existen fraudes publicados online
4. Remates hipotecarios en litigio alteran precios
5. No podemos saber si ya se vendió (vendedores no bajan anuncios)
6. Algunos vendedores DEJAN anuncios viejos para generar llamadas
7. Cada canal (Vivanuncios, EasyBroker) tiene distinta calidad
8. El tiempo es el factor más importante, pero no el único
"""
import logging
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib

logger = logging.getLogger("padim.trust_engine")

# ═══════════════════════════════════════════════════════════════
# MODELO DE SEÑALES
# ═══════════════════════════════════════════════════════════════

class SignalType(Enum):
    """Tipos de señales que el sistema puede identificar"""
    LISTING_ACTIVE = "listing_active"        # Propiedad listada como activa
    LISTING_UPDATED = "listing_updated"      # Propiedad con fecha de actualización reciente
    PRICE_CHANGED = "price_changed"           # Cambio de precio detectado
    PRICE_ANOMALY = "price_anomaly"           # Precio sospechoso (muy bajo/alto)
    MULTI_SOURCE = "multi_source"             # Aparece en múltiples fuentes
    CROSS_CONFIRMED = "cross_confirmed"       # Fuentes confirman datos entre sí
    SOURCE_TRUST_DECAY = "source_trust_decay" # La fuente perdió confianza por inactividad
    GHOST_LISTING = "ghost_listing"           # Propiedad que nunca se actualiza
    FRAUD_SUSPECTED = "fraud_suspected"       # Patrón de fraude detectado
    VENDOR_STRATEGY = "vendor_strategy"       # Vendedor deja anuncio por llamadas
    SOLD_LIKELY = "sold_likely"              # Probablemente ya se vendió
    PRICE_MANIPULATION = "price_manipulation" # Precio manipulado (remates, litigios)
    AGENT_BEHAVIOR = "agent_behavior"         # Patrón de comportamiento del agente/vendedor


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
    estimated_real_price: Optional[float] = None  # Precio estimado REAL
    listing_price_deviation: Optional[float] = None  # Desviación del precio listado vs real
    last_verified: Optional[datetime] = None
    
    def add_signal(self, signal: Signal):
        self.signals.append(signal)
        self._recalculate()
    
    def _recalculate(self):
        """Recalcula el score basado en todas las señales"""
        # Sin señales negativas = confianza base alta (0.7)
        # El score empieza en 0.7 por defecto (confianza asumida)
        base_score = 0.7
        
        if not self.signals:
            self.trust_score = base_score
            self.is_relevant = True  # Sin señales negativas, es relevante
            self.is_suspicious = False
            return
        
        # Señales positivas (aumentan confianza)
        positive_strength = sum(
            s.weight for s in self.signals 
            if s.type in (SignalType.LISTING_UPDATED, SignalType.CROSS_CONFIRMED, 
                         SignalType.PRICE_CHANGED, SignalType.MULTI_SOURCE,
                         SignalType.LISTING_ACTIVE)
        )
        
        # Señales negativas (disminuyen confianza)
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
# DETECTORES DE SEÑALES ESPECÍFICOS
# ═══════════════════════════════════════════════════════════════

class GhostListingDetector:
    """
    Detecta propiedades FANTASMA: anuncios que nunca se actualizan.
    
    Patrón:
    - Misma propiedad aparece en 1+ fuentes
    - Ninguna fuente la ha actualizado en >90 días
    - El precio no ha cambiado
    - El agente/vendedor tiene otras propiedades similares
    
    Esto es diferente de "stale". Stale = no actualizada.
    Ghost = probablemente ya no existe pero el vendedor la deja.
    """
    
    STALE_DAYS = 90       # 3 meses sin actualizar = ghost
    GHOST_THRESHOLD = 180  # 6 meses = ghost confirmado
    
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
    """
    Detecta anomalías de precio.
    
    Patrones de fraude/engaño:
    - Precio sospechosamente bajo (remate, litigio, "herencia")
    - Precio muy por debajo del promedio de la colonia
    - Precio que cambia drásticamente (sube/baja >50%)
    - Misma propiedad publicada a diferentes precios en distintas fuentes
    
    Referencia: precio promedio por m² en CDMX (2024-2025)
    - Económica: $5,000-10,000/m²
    - Popular: $10,000-18,000/m²  
    - Media: $18,000-35,000/m²
    - Residencial: $35,000-60,000/m²
    - Premium: $60,000+/m²
    """
    
    # Precios mínimos y máximos por m² por tipo (CDMX 2025)
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
        
        # 1. Detectar precio extremadamente bajo (posible fraude/remate)
        if price_m2 and property_type in PriceAnomalyDetector.PRICE_RANGES:
            min_m2, max_m2 = PriceAnomalyDetector.PRICE_RANGES[property_type]
            if price_m2 < min_m2 * 0.3:  # 70% por debajo del mínimo
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
            
            if price_m2 > max_m2 * 1.5:  # 50% por encima del máximo
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
        
        # 2. Detectar desviación del mercado local
        if colony_market_price_m2 and price_m2:
            deviation = abs(price_m2 - colony_market_price_m2) / colony_market_price_m2
            if deviation > 0.5:  # >50% de desviación
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
    """
    Detecta patrones de comportamiento de vendedores/agentes.
    
    Estrategias conocidas:
    1. "Siempre disponible": agente con 100+ listings, todos marcados como activos
    2. "Nunca actualiza": agente cuyas propiedades nunca tienen updated_at reciente
    3. "Re-publicador": misma propiedad aparece con diferentes IDs en el tiempo
    4. "Multi-listador": misma propiedad en múltiples fuentes a diferentes precios
    5. "Lead collector": propiedades con precios irreales para generar llamadas
    """
    
    @staticmethod
    def detect_lead_collector(
        agent_name: Optional[str],
        properties_count: int,
        avg_price_m2: Optional[float],
        market_price_m2: Optional[float],
    ) -> Optional[Signal]:
        """
        Detecta si un agente usa propiedades viejas para generar leads.
        
        Patrón: el agente NO baja propiedades vendidas porque 
        más anuncios = más llamadas = más oportunidad de venta cruzada.
        
        Señales:
        - Muchas propiedades del mismo agente
        - Precios por debajo del mercado (para atraer llamadas)
        - Propiedades con 6+ meses sin actualizar
        """
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
    """
    Detecta posibles fraudes.
    
    Patrones:
    1. Misma propiedad, mismo agente, mismo precio, MUCHAS fuentes
    2. Propiedad con descripción genérica ("oportunidad", "herencia", "remate")
    3. Precio irreal vs mercado (demasiado bajo para ser verdad)
    4. Dueño directo (sin agente) con precio muy bajo
    5. Fotos de catálogo / genéricas
    6. Propiedad "en litigio" o "remate bancario"
    """
    
    FRAUD_KEYWORDS = [
        "remate", "litigio", "herencia", "herederos",
        "urge vender", "precio remate", "oportunidad única",
        "dueño directo", "sin intermediarios", "precio negociable",
        "remate bancario", "adjudicado", "juicio",
    ]
    
    @staticmethod
    def detect(title: str, description: str, price_m2: float, market_m2: float) -> List[Signal]:
        signals = []
        
        # Buscar keywords de fraude
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
        
        # Precio muy bajo + keywords = alta probabilidad de fraude
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
    2. Ejecutar detectores en paralelo
    3. Recolectar señales
    4. Calcular trust score
    5. Decidir: usable / sospechosa / fraude
    
    El motor APRENDE con el tiempo:
    - Si un agente tiene muchas propiedades marcadas como ghost, todas sus propiedades
      futuras empiezan con trust reducido
    - Si detectamos que una propiedad "fantasma" fue confirmada como vendida por otra fuente,
      el detector de ghost mejora su precisión
    """
    
    def __init__(self):
        self.detectores = {
            "ghost": GhostListingDetector(),
            "price": PriceAnomalyDetector(),
            "vendor": VendorBehaviorDetector(),
            "fraud": FraudDetector(),
        }
        # Memoria del sistema (aprende con el tiempo)
        self.agent_trust: Dict[str, float] = {}  # agent_name -> trust score
        self.colony_market: Dict[str, float] = {}  # "colony,municipio" -> avg price_m2
    
    async def analyze(
        self,
        property_id: str,
        source: str,
        title: str,
        description: str,
        price: Optional[float],
        price_m2: Optional[float],
        property_type: str,
        last_updated: Optional[datetime],
        days_on_market: Optional[int],
        price_changes: int,
        source_count: int,
        colony: Optional[str],
        municipality: Optional[str],
        agent_name: Optional[str],
        agent_properties_count: int,
    ) -> PropertyIntelligence:
        
        intelligence = PropertyIntelligence(property_id=property_id)
        
        # 1. Ghost listing detection
        signal = self.detectores["ghost"].detect(last_updated, days_on_market, price_changes, source_count)
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
        market_m2_val = market_m2 or 50000  # default
        for signal in self.detectores["fraud"].detect(title, description, price_m2 or 0, market_m2_val):
            intelligence.add_signal(signal)
        
        # 5. Source trust adjustment
        source_trust = SOURCE_TRUST_WEIGHTS.get(source, 0.5)
        if not intelligence.is_suspicious:
            intelligence.trust_score *= source_trust
        
        # Asegurar recálculo incluso sin señales
        intelligence._recalculate()
        
        return intelligence


# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE CONFIANZA POR FUENTE (ajustable con el tiempo)
# ═══════════════════════════════════════════════════════════════

SOURCE_TRUST_WEIGHTS = {
    "vivanuncios": 0.60,      # Portal abierto, riesgo medio
    "easybroker": 0.30,       # Red B2B, listings muertos confirmados
    "inmuebles24": 0.55,      # Similar a Vivanuncios
    "propiedades_com": 0.50,  # Portal con mezcla de datos
    "mls": 0.40,              # Sintético
    "metroscubicos": 0.45,    # Absorbido por ML
    "shf": 0.98,              # Transacciones REALES (cuando se integre)
    "catastro": 0.95,         # Registro oficial
}


# ═══════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════

async def demo():
    """Demo del Trust Engine con casos reales"""
    engine = TrustEngine()
    
    # Caso 1: EasyBroker property (2 años sin actualizar)
    print("=== CASO 1: EasyBroker property (2 años sin update) ===")
    result = await engine.analyze(
        property_id="EB-123",
        source="easybroker",
        title="Hermoso departamento en Polanco",
        description="Oportunidad única, remate bancario",
        price=3500000,
        price_m2=25000,
        property_type="departamento",
        last_updated=datetime.now(timezone.utc) - timedelta(days=730),
        days_on_market=730,
        price_changes=0,
        source_count=1,
        colony="Polanco",
        municipality="Miguel Hidalgo",
        agent_name="José Pérez",
        agent_properties_count=50,
    )
    print(f"  Trust score: {result.trust_score:.2f}")
    print(f"  Relevante: {result.is_relevant}")
    print(f"  Sospechosa: {result.is_suspicious}")
    print(f"  Señales: {[s.type.value for s in result.signals]}")
    print()
    
    # Caso 2: Vivanuncios property (recién actualizada)
    print("=== CASO 2: Vivanuncios property (2 días) ===")
    result = await engine.analyze(
        property_id="VV-456",
        source="vivanuncios",
        title="Casa en renta en Lomas de Chapultepec",
        description="Casa de 3 recámaras con jardín, lista para habitar",
        price=45000,
        price_m2=35000,
        property_type="casa",
        last_updated=datetime.now(timezone.utc) - timedelta(days=2),
        days_on_market=15,
        price_changes=0,
        source_count=2,
        colony="Lomas de Chapultepec",
        municipality="Miguel Hidalgo",
        agent_name="María López",
        agent_properties_count=3,
    )
    print(f"  Trust score: {result.trust_score:.2f}")
    print(f"  Relevante: {result.is_relevant}")
    print(f"  Sospechosa: {result.is_suspicious}")
    print(f"  Señales: {[s.type.value for s in result.signals]}")
    print()
    
    # Caso 3: Fraude potencial (precio bajo + keywords de remate)
    print("=== CASO 3: Posible fraude ===")
    result = await engine.analyze(
        property_id="FR-789",
        source="vivanuncios",
        title="Remate bancario, urge vender, oportunidad única",
        description="Herencia, remate judicial, precio increíble, dueño directo",
        price=500000,
        price_m2=3000,
        property_type="departamento",
        last_updated=datetime.now(timezone.utc) - timedelta(days=180),
        days_on_market=180,
        price_changes=0,
        source_count=1,
        colony="Condesa",
        municipality="Cuauhtémoc",
        agent_name="Luis Martínez",
        agent_properties_count=30,
    )
    print(f"  Trust score: {result.trust_score:.2f}")
    print(f"  Relevante: {result.is_relevant}")
    print(f"  Sospechosa: {result.is_suspicious}")
    print(f"  Señales: {[s.type.value for s in result.signals]}")
    print()
    
    print("=== RESUMEN ===")
    print("El Trust Engine puede ejecutarse:")
    print("1. On-write: al insertar cada propiedad (tiempo real)")
    print("2. Batch: cada hora para propiedades existentes")
    print("3. API: endpoint GET /v1/market/trust/{property_id}")


if __name__ == "__main__":
    asyncio.run(demo())
