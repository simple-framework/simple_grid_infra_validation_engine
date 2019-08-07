import argparse
import testinfra
import simple_grid_yaml_compiler
import yaml

from utils import get_lightweight_component_hosts


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename')
    parser.add_argument('--config_master_host')
    args = parser.parse_args()
    return {
        'filename': args.filename,
        'config_master_host': args.config_master_host
    }


def test_cm_git_install(cm):
    if cm.package('git').is_installed:
        return True
    else:
        return False


if __name__ == "__main__":
    args = parse_args()
    site_level_config_file = args['filename']
    config_master_host = args['config_master_host']
    if config_master_host is not None:
        config_master_host = testinfra.get_host(config_master_host)
    else:
        config_master_host = testinfra.get_host('local://')

    output = test_cm_git_install(config_master_host)

    simple_grid_yaml_compiler.execute_compiler(open(site_level_config_file, 'r'),
                                               open('./.temp/augmented_site_level_config_file.yaml', 'w'),
                                               './.temp/augmented_site_level_schema.yaml')
    augmented_site_level_config = yaml.safe_load(open('./.temp/augmented_site_level_config_file.yaml', 'r'))
    lc_hosts = get_lightweight_component_hosts(augmented_site_level_config)
    print("*****")
    print(lc_hosts)
    for lc_host in lc_hosts:
        lc_host['host'] = testinfra.get_host(lc_host['host'])
        git_test = test_cm_git_install(lc_host['host'])
        print "Git Test on {fqdn}: {git_test}".format(fqdn=lc_host['fqdn'], git_test=git_test)