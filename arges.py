import argparse

def main():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="Process some integers.")

    # Add arguments
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    # Parse arguments
    args = parser.parse_args()

    # Use parsed arguments
    result = args.accumulate(args.integers)
    print(result)

def main_main():
    parser = argparse.ArgumentParser(description="Your script description here")

    parser.add_argument('input', help="Input file name")  # Positional argument
    parser.add_argument('--verbose', help="Increase output verbosity", action='store_true')
    parser.add_argument('--output', help="Output file name", default="output.txt")
    parser.add_argument('--count', type=int, help="Number of times to execute")

    args = parser.parse_args()
    print(args)
    print("INPUT :",args.input)
    print("VERBOSE:",args.verbose)

if __name__ == '__main__':
#    main()
    main_main()
