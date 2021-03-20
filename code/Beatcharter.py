import argparse
import os

from code.beatchart.BeatchartDecoder import BeatchartDecoder


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('input', help="provide an input file ")
    parser.add_argument("encoding", "type of encoding to perform (e.g., sm, ssc, beatmania")
    parser.add_argument("-d", "duration", type=float, default=0.0, help="optional duration to generate steps for in the song. default - whole duration")
    parser.add_argument("-b", "bpm", type=float, default=0.0, help="optional manual bpm to set, otherwise will attempt to figure it out")
    args = parser.parse_args()

    input_file = open(parser.input, 'r')

    output_filename = os.path.splitext(parser.input)[0] + ".sm";
    output_dir = "./";

    decoder = BeatchartDecoder();
    chart = decoder.decode_song(parser.inputFile, parser.bpm);

    print("Generating SM for " + parser.input +   " to "  + output_dir + output_filename);
