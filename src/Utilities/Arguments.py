import argparse



parser = argparse.ArgumentParser(description='Download and process YouTube videos.')



parser.add_argument(
    '--rename', 
    metavar='R', 
    type=str, 
    nargs='?',
    help='the file to rename'
)

parser.add_argument(
    '--subscription', 
    type=str, 
    nargs='?',
    help='the subscription to process'
)



args = parser.parse_args()