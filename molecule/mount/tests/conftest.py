import pytest
from testinfra.utils.ansible_runner import AnsibleRunner
from testinfra import get_host
import os

# Get testinfra hosts
testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.fixture
def ansible_vars():
    """Fixture providing access to Ansible variables from the playbook"""
    host_name = testinfra_hosts[0]
    host = get_host(f'ansible://{host_name}')

    # Use debug module to get all host variables
    result = host.ansible('debug', 'var=hostvars[inventory_hostname]')
    return result['hostvars[inventory_hostname]']
