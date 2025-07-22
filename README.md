# Ansible Collection - eliminyro.samba

[![Molecule CI](https://github.com/eliminyro/eliminyro.samba/actions/workflows/main.yml/badge.svg)](https://github.com/eliminyro/eliminyro.samba/actions/workflows/main.yml)
[![Release](https://github.com/eliminyro/eliminyro.samba/actions/workflows/release.yml/badge.svg)](https://github.com/eliminyro/eliminyro.samba/actions/workflows/release.yml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-eliminyro.samba-blue.svg)](https://galaxy.ansible.com/eliminyro/samba)

A comprehensive Ansible collection for Samba/CIFS management, providing
automated server configuration, user management, and client mounting
capabilities.

## Overview

This collection includes two main roles:

- **`config`** - Configure Samba server with shares, users, and security
  settings
- **`mount`** - Mount CIFS/SMB shares on client systems with credential
  management

## Requirements

- Ansible 2.15.0 or higher
- Python 3.x on the control node
- `ansible.posix` collection (for mount operations)
- Target systems with systemd support

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install eliminyro.samba
```

### From Git Repository

```bash
ansible-galaxy collection install git+https://github.com/eliminyro/eliminyro.samba.git
```

### From Local Source

```bash
git clone https://github.com/eliminyro/eliminyro.samba.git
cd eliminyro.samba
ansible-galaxy collection build
ansible-galaxy collection install eliminyro-samba-*.tar.gz
```

## Roles

### config

Configures Samba server with comprehensive user management, share creation, and
security settings.

**Key Features:**

- Automated Samba server installation and configuration
- User creation with secure password management
- File share creation with configurable permissions
- Custom user creation script integration
- Apple compatibility features
- Security-focused configuration with proper permissions

**Example:**

```yaml
- hosts: samba_servers
  become: true
  roles:
    - role: eliminyro.samba.config
      vars:
        config_smbshares:
          - name: "SharedFiles"
            path: "/srv/samba/shared"
            readonly: "no"
            owner: "fileuser"
            comment: "Shared file storage"
          - name: "ReadOnly"
            path: "/srv/samba/readonly"
            readonly: "yes"
            public: "yes"
        config_smbusers:
          - name: "fileuser"
            password: "{{ vault_samba_fileuser_password }}"
          - name: "guest"
            password: "{{ vault_samba_guest_password }}"
```

### mount

Mounts CIFS/SMB shares on client systems with secure credential management and
persistent configuration.

**Key Features:**

- Automated CIFS utilities installation
- Secure credential file management
- Mount point directory creation
- Persistent mount configuration via fstab
- Configurable mount options for performance and security

**Example:**

```yaml
- hosts: samba_clients
  become: true
  roles:
    - role: eliminyro.samba.mount
      vars:
        mount_credentials:
          production:
            username: "{{ vault_samba_username }}"
            password: "{{ vault_samba_password }}"
        mount_dirs:
          - src: "//server.example.com/SharedFiles"
            path: "/mnt/shared"
            credentials: "production"
            opts: "vers=3.1.1,uid=1000,gid=1000,iocharset=utf8"
          - src: "//server.example.com/ReadOnly"
            path: "/mnt/readonly"
            credentials: "production"
            opts: "vers=3.1.1,ro,uid=1000,gid=1000"
```

## Complete Workflow Example

```yaml
- name: Setup Samba server and mount shares on clients
  hosts: all
  become: true
  tasks:
    # Configure Samba server
    - name: Setup Samba server
      include_role:
        name: eliminyro.samba.config
      vars:
        config_smbshares:
          - name: "CompanyFiles"
            path: "/srv/samba/company"
            readonly: "no"
            owner: "smbuser"
            comment: "Company shared files"
            create_mask: "0664"
            directory_mask: "2775"
          - name: "Public"
            path: "/srv/samba/public"
            readonly: "yes"
            public: "yes"
            comment: "Public read-only files"
        config_smbusers:
          - name: "smbuser"
            password: "{{ vault_samba_user_password }}"
      when: inventory_hostname in groups['samba_servers']

    # Mount shares on clients
    - name: Mount Samba shares
      include_role:
        name: eliminyro.samba.mount
      vars:
        mount_credentials:
          company:
            username: "smbuser"
            password: "{{ vault_samba_user_password }}"
        mount_dirs:
          - src:
              "//{{
              hostvars[groups['samba_servers'][0]]['ansible_default_ipv4']['address']
              }}/CompanyFiles"
            path: "/mnt/company"
            credentials: "company"
            opts: "vers=3.1.1,uid=1000,gid=1000,file_mode=0664,dir_mode=0775"
          - src:
              "//{{
              hostvars[groups['samba_servers'][0]]['ansible_default_ipv4']['address']
              }}/Public"
            path: "/mnt/public"
            credentials: "company"
            opts: "vers=3.1.1,ro,uid=1000,gid=1000"
      when: inventory_hostname in groups['samba_clients']
```

## Security Considerations

This collection implements several security best practices:

- **Password Security**: All password operations use `no_log: true`
- **File Permissions**: Credential files have restrictive 0600 permissions
- **User Security**: Samba users are created with no shell access
- **Directory Permissions**: Share directories use setgid permissions (2775)
- **Service Configuration**: Samba configuration follows security best practices

## Testing

This collection includes comprehensive testing using Molecule with multiple
scenarios:

```bash
# Test config role
molecule test -s config

# Test mount role
molecule test -s mount
```

See [TESTING.md](TESTING.md) for detailed testing information.

## Documentation

Detailed documentation for each role is available in their respective README
files:

- [Config Role Documentation](roles/config/README.md)
- [Mount Role Documentation](roles/mount/README.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

GPL-3.0-or-later

## Author

[Pavel Eliminyro](https://bc.eliminyro.me)

## Support

- **Issues**:
  [GitHub Issues](https://github.com/eliminyro/eliminyro.samba/issues)
- **Repository**:
  [GitHub Repository](https://github.com/eliminyro/eliminyro.samba)
