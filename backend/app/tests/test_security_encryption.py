import pytest
from app.core.security import decrypt_api_key, encrypt_api_key


def test_encrypt_returns_string():
    result = encrypt_api_key("gsk_test1234")
    assert isinstance(result, str)
    assert result != "gsk_test1234"


def test_roundtrip():
    plaintext = "gsk_abcdefghijklmnop1234567890"
    encrypted = encrypt_api_key(plaintext)
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == plaintext


def test_different_inputs_produce_different_ciphertext():
    enc1 = encrypt_api_key("key_one")
    enc2 = encrypt_api_key("key_two")
    assert enc1 != enc2


def test_encrypted_value_is_not_plaintext():
    key = "gsk_mysecretkey"
    encrypted = encrypt_api_key(key)
    assert key not in encrypted
