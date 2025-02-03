from aubio import tempo, source
from pydub import AudioSegment
from numpy import float64, median, diff
from pathlib import Path
from numpy.typing import NDArray

from beatcharter.beatchart.audio_analysis.audio_analysis_wrapper import AudioAnalysisWrapper

class AubioWrapper(AudioAnalysisWrapper):

    def __init__(self):
        self.window_size = 512
        self.hop_size = self.window_size//2
        self.sample_rate_hz = 48000

    def __convert_to_wav(self, path: Path):
        short_name = path.name
        extension = short_name.split('.')[-1]

        if extension == 'mp3':
            name_no_extension = path.name.split('.mp3')[0]

            sound = AudioSegment.from_mp3(path)
            resulting_wav = name_no_extension + ".wav"
            sound.export(resulting_wav, format="wav")
            print("Converted %s to %s (%s)", path, resulting_wav)
            filename = resulting_wav

        return filename

    """
     FindBPM - finds bpm of song
     @return float detected bpm
    """
    def calculate_bpm(self, path: Path) -> NDArray[float64]:

        filename = self.__convert_to_wav(path)
        bpm = self.get_bpm_simple(filename)

        bpm = self.get_bpm_iterative(filename)
        print(bpm)

        return bpm

    def get_bpm_simple(self, filename) -> NDArray[float64]:
        window_size = self.window_size
        hop_size = self.hop_size
        
        # First get the source with native sample rate
        s = source(filename)
        native_sample_rate = s.samplerate
        s.close()
        
        # Then create new source using the file's native sample rate
        s = source(filename, native_sample_rate, hop_size)
        
        o = tempo("default", window_size, hop_size, native_sample_rate)
        
        # tempo detection delay, in samples
        # default to 4 blocks delay to catch up with
        delay = 4. * hop_size

        # list of beats, in samples
        beats = []

        # total number of frames read
        total_frames = 0
        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = int(total_frames - delay + is_beat[0] * hop_size)
                # print("%f" % (this_beat / float(sample_rate)))
                beats.append(this_beat)
            total_frames += read
            if read < hop_size: 
                break

        return beats


    def get_bpm_iterative(self, filename) -> NDArray[float64]:
        """ Calculate the beats per minute (bpm) of a given file.
            filename: filename to the file
            param: dictionary of parameters
        """
        window_size = self.window_size
        hop_size = self.hop_size
        sample_rate = self.sample_rate_hz

        s = source(filename)
        native_sample_rate = s.samplerate
        s.close()

        s = source(filename, native_sample_rate, hop_size)
        sample_rate = s.samplerate
        o = tempo("specdiff", window_size, hop_size, sample_rate)

        # List of beats, in samples
        beats = []
        # Total number of frames read
        total_frames = 0

        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = o.get_last_s()
                beats.append(this_beat)
                # if o.get_confidence() > .2 and len(beats) > 2.:
                #    break
            total_frames += read
            if read < hop_size:
                break

        return beats

    def beats_to_bpm(self, beats, filename):
            # if enough beats are found, convert to periods then to bpm
            if len(beats) > 1:
                if len(beats) < 4:
                    print("few beats found in {:s}".format(filename))
                bpms = 60. / diff(beats)
                return median(bpms)
            else:
                print("not enough beats found in {:s}".format(filename))
                return 0

        return beats_to_bpm(beats, filename)