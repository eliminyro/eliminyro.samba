# Ansible Role: mount

This role is part of the `eliminyro.samba` collection and automates the mounting
of CIFS/SMB shares on client systems. It handles package installation,
credential management, mount point creation, and persistent mount configuration.

## Requirements

- Ansible 2.15+ and Python 3.x on the control node.
- Target system with systemd support.
- Root/sudo privileges on target hosts.
- `ansible.posix` collection (for mount operations).

## Overview

The role performs the following configuration steps:

1. **Install packages** – Installs cifs-utils package for CIFS/SMB support.
2. **Create directories** – Creates mount point directories with proper
   permissions.
3. **Manage credentials** – Generates secure credential files for
   authentication.
4. **Mount shares** – Mounts CIFS/SMB shares persistently via fstab.

## Role Variables

### Required Variables

| Variable            | Default | Description                                                                    |
| ------------------- | ------- | ------------------------------------------------------------------------------ |
| `mount_credentials` | `{}`    | Dictionary of credential sets. Each set requires `username` and `password`.    |
| `mount_dirs`        | `[]`    | List of shares to mount. Each share requires `src`, `path`, and `credentials`. |

### Credential Configuration

Each credential set in `mount_credentials` supports:

| Parameter  | Default    | Description                 |
| ---------- | ---------- | --------------------------- |
| `username` | _required_ | Username for authentication |
| `password` | _required_ | Password for authentication |

### Mount Configuration

Each mount in `mount_dirs` supports:

| Parameter     | Default    | Description                                |
| ------------- | ---------- | ------------------------------------------ |
| `src`         | _required_ | Source share path (//server/share)         |
| `path`        | _required_ | Local mount point directory                |
| `credentials` | _required_ | Name of credential set to use              |
| `opts`        | `""`       | Additional mount options (comma-separated) |

### Optional Variables

| Variable           | Default                                                              | Description                              |
| ------------------ | -------------------------------------------------------------------- | ---------------------------------------- |
| `mount_used_creds` | `{{ mount_dirs \| map(attribute='credentials') \| unique \| list }}` | Automatically calculated credential list |

## Dependencies

- `ansible.posix` collection

## Example Playbook

```yaml
---
- hosts: clients
  become: True
  vars:
    mount_credentials:
      production:
        username: "smbuser"
        password: "{{ vault_samba_password }}"
      readonly:
        username: "guest"
        password: "{{ vault_guest_password }}"

    mount_dirs:
      - src: "//fileserver.company.com/SharedFiles"
        path: "/mnt/shared"
        credentials: "production"
        opts: "vers=3.1.1,uid=1000,gid=1000,iocharset=utf8,file_mode=0664,dir_mode=0775"
      - src: "//fileserver.company.com/Public"
        path: "/mnt/public"
        credentials: "readonly"
        opts: "vers=3.1.1,ro,uid=1000,gid=1000,iocharset=utf8"
      - src: "//backup.company.com/Archives"
        path: "/mnt/archives"
        credentials: "production"
        opts: "vers=2.1,uid=1000,gid=1000,noperm"

  roles:
    - eliminyro.samba.mount
```

## Advanced Configuration

### Multiple Credential Sets

You can define multiple credential sets for different servers or access levels:

```yaml
mount_credentials:
  fileserver:
    username: "fileuser"
    password: "{{ vault_fileserver_pass }}"
  backupserver:
    username: "backupuser"
    password: "{{ vault_backup_pass }}"
  guest:
    username: "guest"
    password: "guestpass"

mount_dirs:
  - src: "//fileserver/data"
    path: "/mnt/data"
    credentials: "fileserver"
    opts: "vers=3.1.1,uid=1000,gid=1000"
  - src: "//backupserver/backups"
    path: "/mnt/backups"
    credentials: "backupserver"
    opts: "vers=3.0,ro,uid=1000,gid=1000"
  - src: "//fileserver/public"
    path: "/mnt/public"
    credentials: "guest"
    opts: "vers=3.1.1,ro"
```

### Common Mount Options

| Option           | Description                            | Example                  |
| ---------------- | -------------------------------------- | ------------------------ |
| `vers=X.X`       | SMB protocol version                   | `vers=3.1.1`, `vers=2.1` |
| `uid=X,gid=X`    | Set file ownership                     | `uid=1000,gid=1000`      |
| `file_mode=XXXX` | File permissions                       | `file_mode=0664`         |
| `dir_mode=XXXX`  | Directory permissions                  | `dir_mode=0775`          |
| `ro`             | Read-only mount                        | `ro`                     |
| `rw`             | Read-write mount (default)             | `rw`                     |
| `iocharset=utf8` | Character set for filename encoding    | `iocharset=utf8`         |
| `noperm`         | Don't check file permissions on server | `noperm`                 |
| `cache=none`     | Disable client-side caching            | `cache=none`             |

## Security Considerations

This role implements several security best practices:

- **Credential Security**: Credential files are created with restrictive 0600
  permissions
- **File Placement**: Credentials are stored in `/etc/.smbcreds-{name}` with
  root ownership
- **Password Handling**: All password operations use `no_log: true` in templates
- **Mount Security**: Supports secure SMB protocol versions (3.0+)

## Troubleshooting

### Common Issues

1. **Mount fails with "Permission denied"**

   - Check username/password in credentials
   - Verify the user has access to the share on the server
   - Ensure the share exists and is accessible

2. **Mount works but files show wrong ownership**

   - Add `uid=X,gid=X` options to set proper ownership
   - Use `file_mode` and `dir_mode` for permission control

3. **Mount fails with "Protocol negotiation failed"**

   - Try different SMB versions: `vers=3.1.1`, `vers=3.0`, `vers=2.1`
   - Some older servers require `vers=1.0` (not recommended for security)

4. **Performance issues**
   - Consider adding `cache=strict` for better performance
   - Use `rsize=1048576,wsize=1048576` for larger I/O operations

## File Structure

The role creates the following files:

- `/etc/.smbcreds-{name}` - Credential files (mode 0600)
- Entries in `/etc/fstab` - Persistent mount configuration
- Mount point directories as specified in `mount_dirs`
