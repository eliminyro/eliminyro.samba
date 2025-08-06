# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-08-06

### Changes

- [FIX] A bug with default variables in mount role (6523e2f)

## [1.0.0] - 2025-08-03

### Changes

- [MAJOR] Added roles and molecule test suite. Added collection description
  files. (ba29271)

### Added

- Fully functional `config` role for comprehensive Samba server configuration
  and management
- Fully functional `mount` role for CIFS/SMB share mounting on client systems
- Comprehensive molecule testing suite with testinfra verification for both
  roles
- Custom user management script (`smbuseradd`) for Samba integration
- Apple compatibility features for macOS Samba clients
- Role-specific README documentation with variable tables and examples
- Security considerations and best practices documentation

### Features

#### config role

- **Package Management**: Automated installation of Samba server and client
  packages
- **Configuration Management**: Template-based Samba daemon configuration with
  customizable settings
- **User Management**: Samba user creation with password management and database
  integration
- **Share Management**: Automated creation of file shares with configurable
  permissions and ownership
- **Security**: Proper permission handling with setgid directories and
  restricted file access
- **Apple Support**: Built-in compatibility features for macOS Samba clients
- **Service Management**: Automatic service startup and configuration validation

#### mount role

- **Package Management**: Automated installation of CIFS utilities
- **Credential Management**: Secure credential file creation with proper
  permissions
- **Mount Management**: Automated mounting of CIFS/SMB shares with configurable
  options
- **Directory Management**: Automatic creation of mount point directories
- **Persistence**: Proper fstab entries for persistent mounts across reboots

### Testing

- **Molecule Scenarios**: Complete test scenarios for both config and mount
  roles
- **Testinfra Integration**: Functional testing using testinfra with proper
  fixture usage
- **Class-based Test Organization**: Well-structured test suites organized by
  functionality
- **Comprehensive Coverage**: Tests for package installation, configuration
  validation, user management, share setup, and service functionality
- **Integration Testing**: Mount role tests include full Samba server setup via
  config role
- **Cleanup Procedures**: Thorough cleanup of all test artifacts and
  configurations

### Documentation

- **Role READMEs**: Comprehensive documentation following collection standards
- **Variable Documentation**: Detailed tables describing all configurable
  parameters
- **Example Playbooks**: Practical usage examples for both roles
- **Security Guidelines**: Documentation of security considerations and best
  practices
- **Testing Documentation**: Instructions for running molecule tests

### Security

- **Secure Password Handling**: All password operations use `no_log: true`
- **Proper File Permissions**: Restrictive permissions on configuration and
  credential files
- **User Security**: Samba users created with no shell access and no home
  directories
- **Directory Permissions**: Share directories use setgid permissions (2775) for
  proper group access
- **Credential Protection**: CIFS credential files have 0600 permissions and
  root ownership

## [0.1.0] - 2025-08-03

### Added

- Initial release with minimal functionality
- `config` role for Samba server setup
- `mount` role for CIFS share mounting
- Basic task implementation without comprehensive testing or documentation
