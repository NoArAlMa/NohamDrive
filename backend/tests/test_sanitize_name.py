import pytest
from fastapi import HTTPException
from app.utils.minio_utils import MinioUtils  # Remplace par ton import réel


def test_sanitize_name_with_accents():
    assert MinioUtils.sanitize_name("écouté moi.mp3") == "écouté moi.mp3"


def test_sanitize_name_with_spaces():
    assert MinioUtils.sanitize_name("mon fichier.txt") == "mon fichier.txt"


def test_sanitize_name_with_forbidden_chars():
    with pytest.raises(HTTPException) as excinfo:
        MinioUtils.sanitize_name("fichier/*.txt")
    assert excinfo.value.status_code == 400
    assert "Nom invalide" in str(excinfo.value.detail)


def test_sanitize_name_with_relative_path():
    with pytest.raises(HTTPException) as excinfo:
        MinioUtils.sanitize_name("../secret.txt")
    assert excinfo.value.status_code == 400
    assert "Nom invalide" in str(excinfo.value.detail)


def test_sanitize_name_empty():
    with pytest.raises(HTTPException) as excinfo:
        MinioUtils.sanitize_name("")
    assert excinfo.value.status_code == 400
    assert "Nom invalide" in str(excinfo.value.detail)


def test_sanitize_name_too_long():
    with pytest.raises(HTTPException) as excinfo:
        MinioUtils.sanitize_name("a" * 31)
    assert excinfo.value.status_code == 400
    assert "Nom trop long" in str(excinfo.value.detail)


def test_sanitize_name_reserved_names():
    assert MinioUtils.sanitize_name("CON.txt") == "CON.txt"
