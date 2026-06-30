"""
PADIM — Tests de regresión v2.0.0
"""
import pytest
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Asegurar que podemos importar padim
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSchema:
    """Tests contra spec/schema.json"""

    def test_schema_loads(self):
        schema_path = Path(__file__).parent.parent / "padim" / "spec" / "schema.json"
        assert schema_path.exists()
        with open(schema_path) as f:
            schema = json.load(f)
        assert schema["version"] == "2.0.0"
        assert "source" in schema["required"]
        assert "price" in schema["required"]

    def test_valid_property(self):
        """Una propiedad mínima debe pasar validación."""
        import jsonschema
        schema_path = Path(__file__).parent.parent / "padim" / "spec" / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        prop = {
            "source": "vivanuncios",
            "source_id": "test-123",
            "property_type": "casa",
            "business_type": "venta",
            "price": 4500000,
            "currency": "MXN",
            "colony": "Del Valle",
            "municipality": "Benito Juárez",
            "state": "CDMX",
        }
        jsonschema.validate(prop, schema)  # debe no lanzar excepción

    def test_invalid_property_missing_price(self):
        """Propiedad sin price debe fallar."""
        import jsonschema
        schema_path = Path(__file__).parent.parent / "padim" / "spec" / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        prop = {
            "source": "vivanuncios",
            "source_id": "test-456",
            "property_type": "casa",
            "business_type": "venta",
            "currency": "MXN",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(prop, schema)

    def test_all_fuel_sources(self):
        """Todas las fuentes del enum deben ser aceptadas."""
        import jsonschema
        schema_path = Path(__file__).parent.parent / "padim" / "spec" / "schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        sources = schema["properties"]["source"]["enum"]
        expected = [
            "vivanuncios", "inmuebles24", "propiedades_com", "metroscubicos",
            "easybroker", "mls", "shf", "catastro", "notarias", "avu", "inegi",
            "contribucion_directa"
        ]
        for s in expected:
            assert s in sources, f"Fuente {s} no está en el schema"
        assert len(sources) >= 12


class TestTrustEngine:
    """Tests para el Trust Engine."""

    def test_engine_imports(self):
        from padim.engine.trust_engine import TrustEngine, SOURCE_TRUST_WEIGHTS
        assert TrustEngine is not None
        assert "vivanuncios" in SOURCE_TRUST_WEIGHTS
        assert "easybroker" in SOURCE_TRUST_WEIGHTS

    def test_fresh_property_high_trust(self):
        """Propiedad recién actualizada debe tener trust score alto."""
        from padim.engine.trust_engine import TrustEngine
        engine = TrustEngine()
        result = engine.analyze(
            property_id="test-fresh-1",
            source="vivanuncios",
            title="Departamento en Condesa",
            description="Departamento recién remodelado, 2 recámaras",
            price=4500000,
            price_m2=45000,
            property_type="departamento",
            last_updated=datetime.now(timezone.utc) - timedelta(days=1),
            source_count=2,
            colony="Condesa",
            municipality="Cuauhtémoc",
        )
        assert result.trust_score > 0.5, f"Fresh property should have high trust, got {result.trust_score}"
        assert result.is_relevant is True
        assert result.is_suspicious is False

    def test_ghost_listing_low_trust(self):
        """Propiedad sin actualizar por 2 años debe tener trust bajo."""
        from padim.engine.trust_engine import TrustEngine
        engine = TrustEngine()
        result = engine.analyze(
            property_id="test-ghost-1",
            source="easybroker",
            title="Casa en Polanco",
            description="Casa grande",
            price=8500000,
            price_m2=35000,
            property_type="casa",
            last_updated=datetime.now(timezone.utc) - timedelta(days=730),
            source_count=1,
            colony="Polanco",
            municipality="Miguel Hidalgo",
            agent_name="Agente Fantasma",
            agent_properties_count=20,
        )
        assert result.trust_score < 0.5, f"Ghost should have low trust, got {result.trust_score}"
        assert any(s.type.value == "ghost_listing" for s in result.signals)

    def test_fraud_detection(self):
        """Keywords de fraude + precio bajo deben activar alarma."""
        from padim.engine.trust_engine import TrustEngine
        engine = TrustEngine()
        result = engine.analyze(
            property_id="test-fraud-1",
            source="vivanuncios",
            title="Remate bancario, urge vender, oportunidad única",
            description="Herencia, remate judicial, dueño directo",
            price=500000,
            price_m2=3000,
            property_type="departamento",
            last_updated=datetime.now(timezone.utc) - timedelta(days=180),
            colony="Condesa",
            municipality="Cuauhtémoc",
        )
        assert result.is_suspicious is True
        assert any(s.type.value == "fraud_suspected" for s in result.signals)

    def test_source_trust_unified(self):
        """Verificar que SOURCE_TRUST_WEIGHTS está unificado."""
        from padim.engine.trust_engine import SOURCE_TRUST_WEIGHTS as tw1
        from padim.engine.data_quality import compute_source_trust
        # Ambos módulos usan el mismo origen ahora
        assert tw1["easybroker"] == 0.30
        assert tw1["shf"] == 0.95

    def test_compute_trust_score_helper(self):
        from padim.engine.trust_engine import compute_trust_score
        score = compute_trust_score(
            property_id="test-helper",
            source="vivanuncios",
            title="Casa en renta",
            description="Bonita casa",
            price=25000,
            price_m2=20000,
            property_type="casa",
        )
        assert 0.0 <= score <= 1.0


class TestCLI:
    """Tests para el CLI."""

    def test_cli_imports(self):
        from padim.cli.main import main, cmd_scrape, cmd_validate, cmd_quality, cmd_serve, cmd_sources
        assert main is not None
        assert cmd_scrape is not None
        assert cmd_validate is not None

    def test_cli_help(self):
        """El CLI debe mostrar help sin errores."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "padim.cli.main", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0  # argparse returns 0 on help
        assert "PADIM" in result.stdout
        assert "scrape" in result.stdout

    def test_cli_sources(self):
        """Listar fuentes debe funcionar."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "padim.cli.main", "sources"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "vivanuncios" in result.stdout


class TestDataQuality:
    """Tests para el sistema de calidad de datos."""

    def test_freshness_scoring(self):
        from padim.engine.data_quality import compute_freshness
        now = datetime.now(timezone.utc)
        # Recién actualizado
        score, days = compute_freshness(now - timedelta(hours=1), "vivanuncios")
        assert score > 0.9
        assert days < 0.1

        # Muy viejo
        score, days = compute_freshness(now - timedelta(days=365), "vivanuncios")
        assert score < 0.1

    def test_price_estimation(self):
        from padim.engine.data_quality import estimate_price_robust
        result = estimate_price_robust(
            [4500000, 4800000, 4200000],
            [0.8, 0.7, 0.6]
        )
        assert result["estimated_price"] is not None
        assert result["confidence"] > 0
        assert result["sample_size"] == 3

    def test_price_estimation_insufficient_data(self):
        from padim.engine.data_quality import estimate_price_robust
        result = estimate_price_robust([1000000], [0.5])
        assert result["estimated_price"] is None  # < 3 samples
