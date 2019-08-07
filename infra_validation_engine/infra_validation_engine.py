import argparse
import testinfra


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename')
    parser.add_argument('--host')
    args = parser.parse_args()
    return {
        'filename': args.filename,
        'host': args.host
    }


def test_cm_git_install(cm):
    if cm.package('git').is_installed:
        return True
    else:
        return False


if __name__ == "__main__":
    args = parse_args()
    site_level_config_file = args['filename']
    host = args['host']
    if host is not None:
        host = testinfra.get_host(host)
    else:
        host = testinfra.get_host('local://')
    output = test_cm_git_install(host)
    print output