import argparse
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename')
    args = parser.parse_args()
    return {
        'filename': args.filename,
    }


if __name__ == "__main__":
    args = parse_args()
    site_level_config_file = args['filename']
    print(site_level_config_file)