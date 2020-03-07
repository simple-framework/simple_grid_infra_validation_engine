import argparse
import testinfra
import yaml

from stages.install import Install
from utils import get_lightweight_component_hosts


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename')
    parser.add_argument('--config_master_host')
    parser.add_argument('-s', '--stages')
    args = parser.parse_args()
    return {
        'filename': args.filename,
        'config_master_host': args.config_master_host,
        'stages': args.stages
    }


def test_cm_git_install(cm):
    if cm.package('git').is_installed:
        return True
    else:
        return False


def execution_pipeline(config_master_host, lightweight_component_hosts, stages):
    if "install" in stages:
        install_stage = Install(config_master_host, lightweight_component_hosts)
        install_stage.execute()


if __name__ == "__main__":
    args = parse_args()
    site_level_config_file = args['filename']
    config_master_host = args['config_master_host']
    stages = args['stages'].split(',')
    if config_master_host is not None:
        config_master_host = testinfra.get_host(config_master_host)
    else:
        config_master_host = testinfra.get_host('local://')

    config_master_host = {
        'fqdn': 'localhost',
        'host': config_master_host,
        'ip_address': '127.0.0.1'
    }

    # output = test_cm_git_install(config_master_host['host'])

    augmented_site_level_config = yaml.safe_load(open('./.temp/augmented_site_level_config_file.yaml', 'r'))
    lc_hosts = get_lightweight_component_hosts(augmented_site_level_config)

    print(lc_hosts)
    for lc_host in lc_hosts:
        lc_host['host'] = testinfra.get_host(lc_host['host'])
        git_test = test_cm_git_install(lc_host['host'])
        print "Git Test on {fqdn}: {git_test}".format(fqdn=lc_host['fqdn'], git_test=git_test)
    execution_pipeline(config_master_host, lc_hosts, stages)