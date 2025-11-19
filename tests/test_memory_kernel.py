"""
Tests for Memory Kernel
"""

import os
import tempfile
import pytest
from src.memory_kernel import MemoryKernel, EncryptionEngine


class TestEncryptionEngine:
    """Tests for the encryption engine."""

    def test_encrypt_decrypt_string(self):
        """Test string encryption and decryption."""
        engine = EncryptionEngine("test-password")
        original = "Hello, World!"

        encrypted = engine.encrypt_string(original)
        decrypted = engine.decrypt_string(encrypted)

        assert decrypted == original
        assert encrypted != original

    def test_different_passwords_fail(self):
        """Test that wrong password fails decryption."""
        engine1 = EncryptionEngine("password1")
        engine2 = EncryptionEngine("password2")

        encrypted = engine1.encrypt_string("secret")

        with pytest.raises(ValueError):
            engine2.decrypt_string(encrypted)


class TestMemoryKernel:
    """Tests for the memory kernel."""

    @pytest.fixture
    def kernel(self):
        """Create a temporary memory kernel."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        kernel = MemoryKernel(db_path, "test-password")
        yield kernel

        kernel.close()
        os.unlink(db_path)

    def test_store_retrieve(self, kernel):
        """Test storing and retrieving data."""
        kernel.store('key1', {'data': 'value'})
        result = kernel.retrieve('key1')

        assert result == {'data': 'value'}

    def test_retrieve_nonexistent(self, kernel):
        """Test retrieving non-existent key."""
        result = kernel.retrieve('nonexistent')
        assert result is None

    def test_preferences(self, kernel):
        """Test preference management."""
        kernel.set_preference('theme', 'dark')
        result = kernel.get_preference('theme')

        assert result == 'dark'

    def test_preference_default(self, kernel):
        """Test preference default value."""
        result = kernel.get_preference('missing', 'default')
        assert result == 'default'

    def test_event_logging(self, kernel):
        """Test event logging."""
        event_id = kernel.log_event('test_event', {'key': 'value'})
        events = kernel.get_history(event_type='test_event')

        assert len(events) == 1
        assert events[0]['data']['key'] == 'value'

    def test_delete(self, kernel):
        """Test deleting data."""
        kernel.store('to_delete', 'data')
        assert kernel.retrieve('to_delete') == 'data'

        kernel.delete('to_delete')
        assert kernel.retrieve('to_delete') is None
