from unittest import TestCase
import os


from beatchart.aubio_wrapper import AubioWrapper


class TestBeatchartDecoder(TestCase):

    def test_decode_song(self):
        self.wrapper =  AubioWrapper()

    def test_find_bpm(self):
        self.wrapper =  AubioWrapper()
        print("current working directory:%s", os.getcwd());

        self.check_bpm_of_file("../../samples/sample1.mp3",     184.1)
        self.check_bpm_of_file("../../samples/dixieland.mp3",   114.0);
        self.check_bpm_of_file("../../samples/batleh.mp3",      111.0);
        self.check_bpm_of_file("../../samples/evelina.mp3",     120.0);
        self.check_bpm_of_file("../../samples/grandfather.mp3", 115.0);
        self.check_bpm_of_file("../../samples/tenting.mp3",     144.0);

    def check_bpm_of_file(self, file_name, correct_bpm):
        self.check_if_bpm_within_offset(self.wrapper.calculate_bpm(file_name), correct_bpm, 2.0)

    def check_if_bpm_within_offset(self, found_bpm, correct_bpm, offset_bpm):
        self.assertGreater(found_bpm, correct_bpm - offset_bpm)
        self.assertLess(found_bpm, correct_bpm + offset_bpm)