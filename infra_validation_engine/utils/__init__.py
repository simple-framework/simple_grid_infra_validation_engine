def get_lightweight_component_hosts(augmented_site_level_config):
    site_infrastructure = augmented_site_level_config['site_infrastructure']
    output = {}
    for node in site_infrastructure:
        output[node['ip_address']] = "ssh://${fqdn}".format(fqdn=node['fqdn'])
    return output


def get_augmented_site_level_config_file(augmented_site_level_config):
    pass