import pytest
from pathlib import Path
from stashenv.favorite import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
    FavoriteNotFoundError,
)


@pytest.fixture
def store_dir(tmp_path):
    return tmp_path


def test_list_favorites_empty_when_no_file(store_dir):
    assert list_favorites(store_dir) == []


def test_add_favorite_creates_file(store_dir):
    add_favorite(store_dir, "prod")
    assert (store_dir / "favorites.json").exists()


def test_add_favorite_stores_profile(store_dir):
    add_favorite(store_dir, "prod")
    assert "prod" in list_favorites(store_dir)


def test_add_multiple_favorites(store_dir):
    add_favorite(store_dir, "prod")
    add_favorite(store_dir, "staging")
    favs = list_favorites(store_dir)
    assert "prod" in favs
    assert "staging" in favs


def test_add_favorite_is_idempotent(store_dir):
    add_favorite(store_dir, "prod")
    add_favorite(store_dir, "prod")
    assert list_favorites(store_dir).count("prod") == 1


def test_remove_favorite_removes_profile(store_dir):
    add_favorite(store_dir, "prod")
    remove_favorite(store_dir, "prod")
    assert "prod" not in list_favorites(store_dir)


def test_remove_favorite_missing_raises(store_dir):
    with pytest.raises(FavoriteNotFoundError):
        remove_favorite(store_dir, "ghost")


def test_is_favorite_true_when_added(store_dir):
    add_favorite(store_dir, "dev")
    assert is_favorite(store_dir, "dev") is True


def test_is_favorite_false_when_not_added(store_dir):
    assert is_favorite(store_dir, "dev") is False


def test_remove_does_not_affect_other_favorites(store_dir):
    add_favorite(store_dir, "prod")
    add_favorite(store_dir, "staging")
    remove_favorite(store_dir, "prod")
    assert is_favorite(store_dir, "staging") is True
