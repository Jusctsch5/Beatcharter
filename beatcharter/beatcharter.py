#!python3
import argparse
import os

from beatchart.beatchart_decoder import BeatchartDecoder


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input", help="provide an input file ")
    parser.add_argument(
        "-e", "--argparse", help="type of encoding to perform (e.g., sm, ssc, beatmania"
    )
    parser.add_argument(
        "-d",
        "--default",
        type=float,
        default=0.0,
        help="optional duration to generate steps for in the song. default - whole duration",
    )
    parser.add_argument(
        "-b",
        "--bpm",
        type=float,
        default=0.0,
        help="optional manual bpm to set, otherwise will attempt to figure it out",
    )
    args = parser.parse_args()
    print("Launching Beatcharer with arguments: " + str(args))

    input_filename = os.path.join("samples", args.input)
    input_file = open(input_filename, "r")

    output_filename = os.path.splitext(args.input)[0] + ".sm"
    output_dir = "./"

    decoder = BeatchartDecoder()
    chart = decoder.decode_song(input_filename, args.bpm)

    print("Generating SM for " + input_filename + " to " + output_dir + output_filename)


if __name__ == "__main__":
    main()
