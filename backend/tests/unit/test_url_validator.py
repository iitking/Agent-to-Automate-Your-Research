from app.tools.validation.url_validator import is_safe_url, normalize_url


def test_safe_url_validation():
    # Valid public URLs
    assert is_safe_url("https://arxiv.org/abs/2301.00001") is True
    assert is_safe_url("https://en.wikipedia.org/wiki/Artificial_intelligence") is True
    assert is_safe_url("http://example.com/research.pdf") is True

    # Blocked SSRF / private targets
    assert is_safe_url("http://localhost:8000") is False
    assert is_safe_url("http://127.0.0.1:5432") is False
    assert is_safe_url("http://0.0.0.0:80") is False
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    assert is_safe_url("ftp://example.com/file.txt") is False
    assert is_safe_url("file:///etc/passwd") is False


def test_url_normalization():
    # Strips tracking query parameters and fragments
    raw = "https://example.com/article?utm_source=twitter&utm_medium=social&id=123#section1"
    normalized = normalize_url(raw)
    assert "utm_source" not in normalized
    assert "utm_medium" not in normalized
    assert "#section1" not in normalized
    assert "id=123" in normalized
