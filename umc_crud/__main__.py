from .login import login
from .config import config
import argparse

def main(args):
    if args['config']:
        config()
    else:
        login()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sistema CRUD de campus UMC.')
    parser.add_argument('--config', action='store_true')
    args = parser.parse_args()
    main(vars(args))
