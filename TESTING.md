# Testing

This collection uses [Molecule](https://molecule.readthedocs.io/) with
[Testinfra](https://testinfra.readthedocs.io/) for comprehensive testing of both
roles.

## Prerequisites

```bash
pip install molecule[default] molecule-plugins testinfra pytest
pip install ansible-core>=2.15 ansible.posix
```

## Test Scenarios

### Config Role Testing

Tests Samba server configuration, user management, and share creation:

```bash
molecule test -s config
```

**Test Coverage:**

- Samba package installation and service configuration
- SMB configuration file generation and validation
- User creation and Samba database management
- Share directory creation with proper permissions
- Custom user script deployment
- Configuration syntax validation using testparm
- Service startup capability testing

### Mount Role Testing

Tests CIFS share mounting, credential management, and persistent configuration:

```bash
molecule test -s mount
```

**Test Coverage:**

- CIFS utilities package installation
- Mount point directory creation
- Secure credential file generation and permissions
- CIFS share mounting with custom options
- Persistent mount configuration via fstab
- Integration testing with full Samba server setup

## Running Individual Test Phases

```bash
# Create test environment
molecule create -s <scenario>

# Run converge (apply the role)
molecule converge -s <scenario>

# Run tests only
molecule verify -s <scenario>

# Clean up
molecule destroy -s <scenario>
```

## Test Structure

```
molecule/
├── config/
│   ├── molecule.yml          # Molecule configuration
│   ├── converge.yml          # Apply config role
│   ├── cleanup.yml           # Test cleanup
│   ├── group_vars/           # Test variables
│   │   └── all/main.yml
│   └── tests/                # Testinfra test files
│       ├── conftest.py       # Test fixtures
│       └── test_default.py   # Config role tests
└── mount/
    ├── molecule.yml          # Molecule configuration
    ├── converge.yml          # Apply mount role
    ├── prepare.yml           # Samba server setup
    ├── cleanup.yml           # Test cleanup
    ├── requirements.yml      # Collection dependencies
    ├── group_vars/           # Test variables
    │   └── all/main.yml
    └── tests/                # Testinfra test files
        ├── conftest.py       # Test fixtures
        └── test_default.py   # Mount role tests
```

## Test Configuration

### Config Scenario

- **Driver**: Default (local execution)
- **Provisioner**: Ansible
- **Verifier**: Testinfra
- **Test Environment**: Local system with Samba installation

### Mount Scenario

- **Driver**: Default (local execution)
- **Provisioner**: Ansible
- **Verifier**: Testinfra
- **Dependencies**: Uses config role to set up test Samba server
- **Integration**: Full server-client testing scenario

## Test Organization

Tests are organized using class-based structure for better organization:

### Config Role Test Classes

- **TestSambaPackageInstallation**: Package installation verification
- **TestSambaConfiguration**: Configuration file and daemon testing
- **TestSambaUserScript**: Custom script deployment testing
- **TestSambaShares**: Share configuration and directory testing
- **TestSambaUsers**: User management and database testing
- **TestSambaServices**: Service functionality testing

### Mount Role Test Classes

- **TestCIFSPackageInstallation**: CIFS utilities installation
- **TestMountDirectories**: Mount point directory creation
- **TestCredentialsFiles**: Credential file security and content
- **TestMountConfiguration**: Mount point and fstab configuration

## Continuous Integration

Tests run automatically on:

- Pull requests
- Pushes to master branch
- Manual workflow dispatch

The CI pipeline runs both scenarios in parallel and includes:

- Ansible lint validation
- Ansible sanity tests
- Full molecule test suite

## Writing Tests

Tests are written using [Testinfra](https://testinfra.readthedocs.io/) with
pytest fixtures. Example:

```python
class TestSambaConfiguration:
    """Test suite for Samba daemon configuration"""

    def test_smb_conf_file_exists(self, host):
        """Test that smb.conf file exists and has correct permissions."""
        smb_conf = host.file("/etc/samba/smb.conf")
        assert smb_conf.exists, "Samba configuration file does not exist"
        assert smb_conf.mode == 0o644, f"Config file permissions are {oct(smb_conf.mode)}, expected 0o644"

    def test_samba_configuration_valid(self, host):
        """Test that samba configuration is valid using testparm."""
        cmd = host.run("testparm -s")
        assert cmd.rc == 0, f"Samba configuration is invalid: {cmd.stderr}"
```

## Debugging Failed Tests

```bash
# Keep environment after failure for debugging
molecule test --destroy=never -s <scenario>

# Connect to test environment for manual inspection
sudo -i

# View test logs with verbose output
molecule test -s <scenario> -- -v

# Run specific test classes
molecule verify -s <scenario> -- tests/test_default.py::TestSambaConfiguration
```

## Local Development

For faster development iterations:

```bash
# Create environment once
molecule create -s <scenario>

# Iteratively test changes
molecule converge -s <scenario>
molecule verify -s <scenario>

# Cleanup when done
molecule destroy -s <scenario>
```

## Integration Testing

The mount scenario includes integration testing:

1. **Prepare Stage**: Sets up a full Samba server using the config role
2. **Converge Stage**: Applies the mount role to connect to the server
3. **Verify Stage**: Tests both server and client functionality
4. **Cleanup Stage**: Removes both server and client configurations

This provides comprehensive end-to-end testing of the complete Samba workflow.

## Test Variables

Test scenarios use specific variables defined in `group_vars/all/main.yml`:

### Config Scenario Variables

```yaml
config_smbshares:
  - name: "TestShare"
    path: "/srv/samba/test"
    readonly: "no"
    owner: "root"

config_smbusers:
  - name: "testuser"
    password: "testpass123"
```

### Mount Scenario Variables

```yaml
mount_credentials:
  test:
    username: "testuser"
    password: "testpass123"

mount_dirs:
  - src: "//127.0.0.1/TestShare"
    path: "/mnt/test-mount"
    credentials: "test"
    opts: "vers=3.1.1,uid=1000,gid=1000"
```

## Security Testing

Tests include security validation:

- File permission verification (0600 for credentials, 0644 for configs)
- User creation with proper restrictions (no shell, no home directory)
- Directory permissions with setgid bits
- Password handling with no_log verification
- Service configuration security compliance
