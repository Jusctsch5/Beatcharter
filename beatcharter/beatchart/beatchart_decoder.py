from beatchart.aubio_wrapper import AubioWrapper
from beatchart.beatchart import Beatchart

class BeatchartDecoder:

    """
     BeatchartDecoder - perform decoding of beats and audio to generate an object that can be handled by the StepBuilder
    """

    def __init__(self):
        self.wrapper = AubioWrapper()

    def decode_song(self, song_file, bpm):
        if bpm == 0:
            bpm = self.wrapper.calculate_bpm(song_file)

        return Beatchart(song_file, bpm)

    """
     * Regarding methods of finding BPM
     *
     * Tactus and Tatum:
     *  Finding BPM is about finding tactus level of events in music. This often requires identifying and converting tatums or sub-tatums to the tactus.
     *  A tactus defines the rate at which the beat is measured. It is usually given the same rate as quarter note in X/4 time. It would be given the same rate as an eighth note in X/8 time.
     *  The tactus might be undetectable when looking at the music, as there may not be any note played at that frequency.
     *  A tatum defines the fastest rate of any note in the music. As an example, this could be the eighth notes on a cymbal.
     *  A sub-tatum will be defined as any other rate of note in the music.
     *
     * A collection of the tatum and other sub-tatum can be used to constitute the tactus. It is not an exact science.
     * If you have a piece with only eighth notes in 4/4 time, how do you know the difference between the tatum (eighth note) and the tactus (quarter note)?
     * You don't. Another way of expressing this is that the BPM may be some multiple or fraction of a whole number from what was calculated.
     * It might not even be a whole number multiple, as triplets and other notations can cause relationship between tactus and tatum to be even weirder.
     *
     * One method to remove some ambiguity here is to assume that BPM is always between 100-199 BPMs or different range most commonly observed in music.
     *
     * See reference "Tempo and Beat Tracking"
     * https://www.youtube.com/watch?v=FmwpkdcAXl0
     *
     * Converting Tactus to BPM:
     * Finding the Tactus result in us finding an interval of seconds between each beat. This can be converted into BPM, note the units:
     * 60 (seconds / minute)  / Tactus (seconds / beat) = BPM ( beats / minute)
     */
    """
    def calculate_bpm(self, song_file):
        return self.wrapper.find_bpm(song_file)
