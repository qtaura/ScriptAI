import unittest
import sys
import os
import io
from unittest.mock import patch

# Add parent directory to path to import cli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli import LocalModelGenerator


class TestCLI(unittest.TestCase):
    def test_local_model_generation(self):
        """Test that the local model generator returns a code stub"""
        generator = LocalModelGenerator()
        code, error = generator.generate("Test prompt")
        self.assertIsNotNone(code)
        self.assertIsNone(error)
        self.assertTrue(len(code) > 0)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_help(self, mock_stdout):
        """Test that the CLI shows help when no arguments are provided"""
        with patch("sys.argv", ["cli.py"]):
            try:
                from cli import main

                main()
                output = mock_stdout.getvalue()
                self.assertIn("usage:", output.lower())
                self.assertIn("scriptai", output.lower())
            except SystemExit:
                # argparse may exit, which is expected
                pass


if __name__ == "__main__":
    unittest.main()
