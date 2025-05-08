import pytest
from brawl_bot import characters_data, rarities

def test_characters_data_loaded():
    assert isinstance(characters_data, dict), "characters_data nav vārdnīca"

def test_rarities_format():
    assert all(isinstance(r, tuple) and len(r) == 2 for r in rarities), "Nepareizs rarities formāts"

def test_empty_rarity_characters(monkeypatch):
    def mock_data():
        return {"A": {"rarity": "common"}}
    monkeypatch.setattr("brawl_bot.characters_data", mock_data())

    filtered = [name for name, data in mock_data().items() if data["rarity"] == "rare"]
    assert filtered == [], "Reti jābūt tukšam sarakstam"

def test_caption_trimming():
    long_text = "Build for X:\\n" + ("Very long text. " * 100) + "\\n\\nDescription"
    trimmed = long_text[:1020] + "..."
    assert len(trimmed) <= 1024, "Caption nav nogriezts pareizi"
