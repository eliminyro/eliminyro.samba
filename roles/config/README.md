# Ansible Role: config

This role is part of the `eliminyro.samba` collection and automates the
configuration of Samba file sharing services. It handles package installation,
daemon configuration, user management, and share creation with flexible
permission settings and Apple compatibility features.

## Requirements

- Ansible 2.15+ and Python 3.x on the control node.
- Target system with systemd support.
- Root/sudo privileges on target hosts.

## Overview

The role performs the following configuration steps:

1. **Install packages** – Installs Samba server and client packages.
2. **Configure daemon** – Generates and deploys the main Samba configuration
   file.
3. **Create groups and users** – Sets up the samba group and creates system
   users.
4. **Deploy user script** – Installs a custom user creation script for Samba
   integration.
5. **Manage Samba users** – Creates Samba database entries and sets passwords.
6. **Create shares** – Sets up share directories with proper permissions and
   ownership.

## Role Variables

### Required Variables

| Variable           | Default | Description                                                              |
| ------------------ | ------- | ------------------------------------------------------------------------ |
| `config_smbshares` | `[]`    | List of file shares to create. Each share requires `name` and `path`.    |
| `config_smbusers`  | `[]`    | List of Samba users to create. Each user requires `name` and `password`. |

### Share Configuration

Each share in `config_smbshares` supports the following parameters:

| Parameter        | Default          | Description                            |
| ---------------- | ---------------- | -------------------------------------- |
| `name`           | _required_       | Name of the share                      |
| `path`           | _required_       | Filesystem path to the share directory |
| `readonly`       | `"yes"`          | Read-only access (`"yes"` or `"no"`)   |
| `owner`          | `"root"`         | Directory owner                        |
| `group`          | `"samba"`        | Directory group                        |
| `browseable`     | `"yes"`          | Share visibility in network browsing   |
| `printable`      | `"no"`           | Allow printing                         |
| `public`         | `"no"`           | Public access without authentication   |
| `comment`        | `"Share {name}"` | Share description                      |
| `create_mask`    | `"0664"`         | File creation permissions              |
| `directory_mask` | `"2775"`         | Directory creation permissions         |

### User Configuration

Each user in `config_smbusers` requires:

| Parameter  | Default    | Description   |
| ---------- | ---------- | ------------- |
| `name`     | _required_ | Username      |
| `password` | _required_ | User password |

## Dependencies

None.

## Example Playbook

```yaml
---
- hosts: servers
  become: True
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
        password: "securepassword123"
      - name: "guest"
        password: "guestpass456"

  roles:
    - eliminyro.samba.config
```

## Security Considerations

- Passwords are handled securely using `no_log: True`
- Share directories use setgid permissions (2775) for proper group access
- Users are created with no shell access and no home directory
- All configuration files have restrictive permissions
