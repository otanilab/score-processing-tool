"""
Mock external dependencies that may not be installed in the test environment.
Import this module before importing main in each test file.
"""
import sys
from unittest.mock import MagicMock

MOCK_MODULES = [
    'music21', 'music21.converter',
    'PIL', 'PIL.Image',
    'pdf2image',
    'google', 'google.oauth2', 'google.oauth2.service_account',
    'googleapiclient', 'googleapiclient.discovery', 'googleapiclient.http',
]

for mod_name in MOCK_MODULES:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

# Now we need PIL.Image to behave like the real one for tests that use it
# Re-create a proper Image mock with open/new/save
from PIL import Image as _MockImage

class _FakeImage:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.size = (width, height)

    def paste(self, im, box=None):
        pass

    def save(self, fp, format=None):
        pass

_MockImage.new = staticmethod(lambda mode, size, color='white': _FakeImage(size[0], size[1]))
_MockImage.open = staticmethod(lambda fp: _FakeImage())
