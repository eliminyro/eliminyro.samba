from conftest import testinfra_hosts
import testinfra

# Get the host
host = testinfra.get_host(f'local://{testinfra_hosts[0]}', sudo=True)


def test_cifs_utils_package_installed():
    """Test that cifs-utils package is installed."""
    cifs_utils = host.package("cifs-utils")
    assert cifs_utils.is_installed


def test_mount_directories_exist(ansible_vars):
    """Test that mount directories exist with correct permissions."""
    mount_dirs = ansible_vars['mount_dirs']

    for mount_dir in mount_dirs:
        path = mount_dir['path']
        directory = host.file(path)
        assert directory.exists
        assert directory.is_directory
        assert directory.mode == 0o755


def test_credentials_files_exist(ansible_vars):
    """Test that credentials files exist with correct permissions."""
    used_creds = ansible_vars['mount_used_creds']

    for cred_name in used_creds:
        cred_file = host.file(f"/etc/.smbcreds-{cred_name}")
        assert cred_file.exists
        assert cred_file.is_file
        assert cred_file.user == "root"
        assert cred_file.group == "root"
        assert cred_file.mode == 0o600


def test_credentials_file_content(ansible_vars):
    """Test that credentials files contain expected content."""
    credentials = ansible_vars['mount_credentials']
    used_creds = ansible_vars['mount_used_creds']

    for cred_name in used_creds:
        cred_file = host.file(f"/etc/.smbcreds-{cred_name}")
        content = cred_file.content_string

        username = credentials[cred_name]['username']
        password = credentials[cred_name]['password']

        assert f"Username={username}" in content
        assert f"Password={password}" in content


def test_mount_points_configured(ansible_vars):
    """Test that mount points are configured in /etc/fstab or currently mounted."""
    mount_dirs = ansible_vars['mount_dirs']

    for mount_dir in mount_dirs:
        path = mount_dir['path']
        src = mount_dir['src']

        # Check if mount point is in /etc/fstab (persistent mount)
        fstab = host.file("/etc/fstab")
        fstab_content = fstab.content_string

        # Look for the mount entry in fstab
        fstab_lines = [line for line in fstab_content.split('\n')
                       if src in line and path in line and 'cifs' in line]

        # Check if currently mounted in /proc/mounts
        mounts_file = host.file("/proc/mounts")
        mounts_content = mounts_file.content_string
        mount_lines = [line for line in mounts_content.split('\n')
                       if path in line and 'cifs' in line]

        # Mount should be either in fstab (for persistence) or currently mounted
        # Since ansible.posix.mount with state=mounted adds to fstab and mounts
        assert len(fstab_lines) > 0 or len(mount_lines) > 0, \
            f"Mount {src} -> {path} not found in fstab or proc/mounts"


def test_mount_options_in_fstab(ansible_vars):
    """Test that mount entries have correct options in /etc/fstab."""
    mount_dirs = ansible_vars['mount_dirs']

    fstab = host.file("/etc/fstab")
    fstab_content = fstab.content_string

    for mount_dir in mount_dirs:
        path = mount_dir['path']
        src = mount_dir['src']
        credentials = mount_dir['credentials']
        opts = mount_dir['opts']

        # Find the fstab line for this mount
        fstab_lines = [line for line in fstab_content.split('\n')
                       if src in line and path in line and 'cifs' in line]

        if fstab_lines:  # If mount is in fstab
            fstab_line = fstab_lines[0]

            # Check that credentials file is referenced
            assert f"/etc/.smbcreds-{credentials}" in fstab_line, \
                f"Credentials file not found in fstab entry: {fstab_line}"

            # Check that custom options are present
            assert "vers=3.1.1" in fstab_line, \
                f"Expected mount options not found in fstab entry: {fstab_line}"
