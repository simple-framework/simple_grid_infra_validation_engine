# simple_grid_infra_validation_engine
Use TestInfra to validate the actions performed by Central Configuration Manager at every stage of the execution pipeline

# Development Environment Setup Instructions
- For all Infrastructure Tests belonging to INSTALL, CONFIG, PRE_DEPLOY stages, it is easiest to use the simple_grid_puppet_dev_kit containers for developing.
- For infrastructure tests belonging to the DEPLOY stage, it is strongly recommended to use VM configurations available in simple_grid_puppet_dev_kit

## Dev-Kit containers based development environment
1. Create a new directory that will serve as the root of your dev environemnt

    ```
    mkdir simple_grid_infra_validation_engine_dev
    cd simple_grid_infra_validation_engine_dev
    ```

1. Clone this repo, the simple_grid_puppet_module, the simple_grid_yam_compiler and the infra_validation_branch in the simple_grid_puppet_dev_kit in your dev directory

    ```
    git clone https://github.com/WLCG-Lightweight-Sites/simple_grid_yaml_compiler

    git clone https://github.com/WLCG-Lightweight-Sites/simple_grid_puppet_module

    git clone https://github.com/WLCG-Lightweight-Sites/simple_grid_infra_validation_engine 

    git clone -b infra_validation_engine https://github.com/maany/simple_grid_puppet_dev_kit

    ```
1. Build and Start the dev kit containers

    ```
    cd simple_grid_puppet_dev_kit
    docker-compose up --build
    ```
1. Initialize the containers
    ```
    docker exec -it basic_config_master /data/init.sh
    ```
1. Initialize the containers
    ```
    docker exec -it lightweight_component01 /data/init.sh
    ```
1. Initialize the containers
    ```
    docker exec -it lightweight_component02 /data/init.sh
    ```
1. Enter the basic_config_master container
    ```
        docker exec -it basic_config_master bash
    ```
1. Source the bashrc file
    ```
        source ~/.bashrc
    ```
1. Enter the simple_grid_infra_validation_engine directory inside the container.

    ```
    testinfra_dev_dir
    ```
1. To execute the simple_grid_infra_validation_engine
    ```
    testinfra
    ```
## Dev-Kit VM based dev environment
Please contact us to help you set this up. We will provide more concrete instructions once we start DEPLOY stage testing.

# Adding Tests
The tests can be created for a component(yaml_compiler, ccm, puppet_ccm, config_validation_engine, component_repository etc.) or a node (config_master, lightweight_component).
The former test cases are present in infra_validation_engine.components package while the latter reside in the infra_validation_engine.nodes package.

To create a new Test, define a new class in the appropriate file of the node/component package.

For instance, let's test if YAML compiler was executed. The execution of the YAML compiler generates the augmented_site_level_config_file.yaml in the basic_config_master node. Therefore, we wil write a test to check for the presence of this file.

We'd create a new class called YamlCompilerExecutionTest in the infra_validation_engine.components.yaml_compiler file.
The YamlCompilerExecutionTest class must be a subclass of the core.InfraTest class. InfraTest is an abstract class that defines two abstact methods, run() and fail(). In the YamlCompilerExecutionTest class, we must override these methods appropriately. In addition to these methods, the InfraTest class exposes the testinfra host as self.host, decription of the test as self.description, name of the test as self.name and fqdn of the machine where the test will be executed as self.fqdn.

```
class YamlCompilerConstants(Constants):
    YAML_COMPILER_INSTALLATION_DIR = "{SIMPLE_CONFIG_DIR}/simple_grid_yaml_compiler".format(
        SIMPLE_CONFIG_DIR=Constants.SIMPLE_CONFIG_DIR
    )
    AUGMENTED_SITE_LEVEL_CONFIG_FILE = "{SIMPLE_CONFIG_DIR}/site_config/augmented_site_level_config_file.yaml".format(
        SIMPLE_CONFIG_DIR=Constants.SIMPLE_CONFIG_DIR
    )

class YamlCompilerExecutionTest(InfraTest):
    def __init__(self, host, fqdn):
        InfraTest.__init__(self, "Yaml Compiler Execution Status Test",
                           "Check if YAML compiler was executed on {fqdn}".format(fqdn=fqdn),
                           host, fqdn)

    def run(self):
        return self.host.file(YamlCompilerConstants.AUGMENTED_SITE_LEVEL_CONFIG_FILE).is_file

    def fail(self):
        raise Exception("Could not find the augmented_site_level_config_file at {path}".format(
            path=YamlCompilerConstants.AUGMENTED_SITE_LEVEL_CONFIG_FILE
        ))
```

Finally we must register the newly created test case with the stage and assign a node on which it should be executed on.
For the current example, the YamlCompilerExecutionTest must be registered in the install stage and must be executed on the config_master node. Therefore, we add the following line in the register_tests method of the infra_validation_engine.stages.install file
```
self.infra_tests.append(YamlCompilerExecutionTest(self.config_master_host['host'], self.config_master_host['fqdn']))
```
