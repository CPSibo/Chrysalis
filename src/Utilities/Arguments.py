import argparse



parser = argparse.ArgumentParser(description='Wrapper for youtube-dl.')



parser.add_argument(
    '--postprocess', 
    metavar =   'P', 
    type =      str, 
    nargs =     '?',
    help =      'the file to post-process'
)

parser.add_argument(
    '--subscription', 
    type =      str, 
    nargs =     '?',
    help =      'the subscription to process'
)



args = parser.parse_args()