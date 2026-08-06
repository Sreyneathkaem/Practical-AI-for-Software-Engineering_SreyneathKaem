import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from main import Session


class SessionPersistenceTests(unittest.TestCase):
    def make_session(self) -> Session:
        args = SimpleNamespace(
            persona="default",
            model="test-model",
            temperature=0.7,
            max_tokens=100,
            stream=False,
        )
        return Session(args)

    def test_save_writes_messages_to_json(self) -> None:
        session = self.make_session()
        session.messages.append({"role": "user", "content": "hello"})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chat.json"
            session.save_messages(str(path))
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), session.messages)

    def test_load_replaces_conversation_with_valid_data(self) -> None:
        session = self.make_session()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chat.json"
            payload = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Remember this"},
            ]
            path.write_text(json.dumps(payload), encoding="utf-8")

            self.assertTrue(session.load_messages(str(path)))
            self.assertEqual(session.messages, payload)

    def test_load_rejects_invalid_payload_and_keeps_current_messages(self) -> None:
        session = self.make_session()
        original_messages = list(session.messages)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "chat.json"
            path.write_text(json.dumps([{"role": "user"}]), encoding="utf-8")

            self.assertFalse(session.load_messages(str(path)))
            self.assertEqual(session.messages, original_messages)


if __name__ == "__main__":
    unittest.main()
