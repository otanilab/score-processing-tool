import os
import sys
import tempfile
import unittest
import shutil
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import main
from main import make_score


class TestMakeScoreEdgeCases(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_midi_file(self):
        result = make_score(self.tmpdir)
        self.assertIsNone(result)

    def test_bad_filename_pattern(self):
        mid_path = os.path.join(self.tmpdir, 'nopattern.mid')
        with open(mid_path, 'w') as f:
            f.write('dummy')

        mock_stream = MagicMock()
        mock_stream.write.return_value = mid_path.replace('.mid', '.pdf')

        with patch('main.m2.converter.parse', return_value=mock_stream):
            result = make_score(self.tmpdir)
            self.assertIsNone(result)


class TestMusicXmlEditing(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.musicxml_path = os.path.join(self.tmpdir, 'test.musicxml')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _create_musicxml(self, work_title='Music21 Fragment', creator_text='Music21'):
        root = ET.Element('score-partwise')
        work = ET.SubElement(root, 'work')
        work_title_elem = ET.SubElement(work, 'work-title')
        work_title_elem.text = work_title

        identification = ET.SubElement(root, 'identification')
        creator = ET.SubElement(identification, 'creator', type='composer')
        creator.text = creator_text

        part = ET.SubElement(root, 'part')
        measure = ET.SubElement(part, 'measure')
        direction = ET.SubElement(measure, 'direction')
        ET.SubElement(direction, 'direction-type')

        tree = ET.ElementTree(root)
        tree.write(self.musicxml_path, encoding='unicode', xml_declaration=True)
        return self.musicxml_path

    def test_xml_song_name_replacement(self):
        self._create_musicxml()

        tree = ET.parse(self.musicxml_path)
        root = tree.getroot()

        for elem in root.iter('work-title'):
            if elem.text and 'Music21' in elem.text:
                elem.text = 'TestSong'

        tree.write(self.musicxml_path, encoding='unicode', xml_declaration=True)

        tree2 = ET.parse(self.musicxml_path)
        root2 = tree2.getroot()
        for elem in root2.iter('work-title'):
            self.assertEqual(elem.text, 'TestSong')

    def test_xml_composer_replacement(self):
        self._create_musicxml()

        tree = ET.parse(self.musicxml_path)
        root = tree.getroot()

        for elem in root.iter('creator'):
            if elem.get('type') == 'composer':
                elem.text = 'Test Lab'

        tree.write(self.musicxml_path, encoding='unicode', xml_declaration=True)

        tree2 = ET.parse(self.musicxml_path)
        root2 = tree2.getroot()
        for elem in root2.iter('creator'):
            self.assertEqual(elem.text, 'Test Lab')

    def test_xml_direction_placement(self):
        self._create_musicxml()

        tree = ET.parse(self.musicxml_path)
        root = tree.getroot()

        for elem in root.iter('direction'):
            if elem.get('placement') is None:
                elem.set('placement', 'above')

        tree.write(self.musicxml_path, encoding='unicode', xml_declaration=True)

        tree2 = ET.parse(self.musicxml_path)
        root2 = tree2.getroot()
        for elem in root2.iter('direction'):
            self.assertEqual(elem.get('placement'), 'above')

    def test_xml_preserves_existing_placement(self):
        root = ET.Element('score-partwise')
        part = ET.SubElement(root, 'part')
        measure = ET.SubElement(part, 'measure')
        direction = ET.SubElement(measure, 'direction', placement='below')
        ET.SubElement(direction, 'direction-type')

        tree = ET.ElementTree(root)
        tree.write(self.musicxml_path, encoding='unicode', xml_declaration=True)

        tree = ET.parse(self.musicxml_path)
        root = tree.getroot()

        for elem in root.iter('direction'):
            if elem.get('placement') is None:
                elem.set('placement', 'above')

        tree.write(self.musicxml_path, encoding='unicode', xml_declaration=True)

        tree2 = ET.parse(self.musicxml_path)
        root2 = tree2.getroot()
        for elem in root2.iter('direction'):
            self.assertEqual(elem.get('placement'), 'below')


if __name__ == '__main__':
    unittest.main()
