"""
Tests for application configuration and sport definitions.
"""

import pytest

from app.config import Settings
from app.sports.registry import SportRegistry


class TestSportRegistry:
    def test_snowboard_available(self):
        assert SportRegistry.has_sport("snowboard")

    def test_skiing_available(self):
        assert SportRegistry.has_sport("skiing")

    def test_disabled_sports_not_available(self):
        # These sports are disabled for now (future versions)
        assert not SportRegistry.has_sport("running")
        assert not SportRegistry.has_sport("golf")
        assert not SportRegistry.has_sport("yoga")
        assert not SportRegistry.has_sport("home_workout")

    def test_invalid_sport_not_available(self):
        assert not SportRegistry.has_sport("cricket")

    def test_list_sports_returns_active(self):
        sports = SportRegistry.list_sports()
        sport_ids = [s["sport_id"] for s in sports]
        assert "snowboard" in sport_ids
        assert "skiing" in sport_ids
        assert len(sport_ids) == 2

    def test_all_sports_have_required_fields(self):
        for sport in SportRegistry.list_sports():
            assert "sport_id" in sport
            assert "display_name" in sport
            assert "emoji" in sport
            assert "description" in sport


class TestSettings:
    def test_default_settings(self):
        s = Settings()
        assert s.backend_host == "0.0.0.0"
        assert s.backend_port == 8000
        assert s.max_upload_size_mb == 500
        assert s.inference_batch_size == 8

    def test_origins_list(self):
        s = Settings()
        origins = s.origins_list
        assert isinstance(origins, list)
        assert len(origins) >= 1

    def test_jwt_secret_default(self):
        s = Settings()
        assert s.jwt_secret == "change-me-in-production"
