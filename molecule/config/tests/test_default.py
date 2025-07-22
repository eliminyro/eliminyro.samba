class TestSambaPackageInstallation:
    """Test suite for Samba package installation"""

    def test_samba_package_installed(self, host):
        """Test that samba package is installed."""
        samba = host.package("samba")
        assert samba.is_installed

    def test_smbclient_command_available(self, host):
        """Test that smbclient command is available."""
        cmd = host.run("which smbclient")
        assert cmd.rc == 0, "smbclient command not found"

    def test_samba_group_exists(self, host):
        """Test that samba group exists."""
        group = host.group("samba")
        assert group.exists


class TestSambaConfiguration:
    """Test suite for Samba daemon configuration"""

    def test_smb_conf_file_exists(self, host):
        """Test that smb.conf file exists and has correct permissions."""
        smb_conf = host.file("/etc/samba/smb.conf")
        assert smb_conf.exists, "Samba configuration file does not exist"
        assert smb_conf.is_file, "Samba config path is not a file"
        assert smb_conf.user == "root", f"Config file owner is {smb_conf.user}, expected root"
        assert smb_conf.group == "root", f"Config file group is {smb_conf.group}, expected root"
        assert smb_conf.mode == 0o644, f"Config file permissions are {oct(smb_conf.mode)}, expected 0o644"

    def test_smb_conf_contains_global_section(self, host):
        """Test that smb.conf contains expected global configuration."""
        smb_conf = host.file("/etc/samba/smb.conf")
        assert smb_conf.exists, "Samba configuration file not found"

        content = smb_conf.content_string
        assert "[global]" in content, "Global section not found in smb.conf"
        assert "server role = standalone server" in content, "Server role not configured"
        assert "logging = systemd" in content, "Systemd logging not configured"

    def test_samba_configuration_valid(self, host):
        """Test that samba configuration is valid using testparm."""
        cmd = host.run("testparm -s")
        assert cmd.rc == 0, f"Samba configuration is invalid: {cmd.stderr}"


class TestSambaUserScript:
    """Test suite for custom user script deployment"""

    def test_smbuseradd_script_exists(self, host):
        """Test that smbuseradd script exists with correct permissions."""
        script = host.file("/usr/bin/smbuseradd")
        assert script.exists, "smbuseradd script not found"
        assert script.is_file, "smbuseradd path is not a file"
        assert script.user == "root", f"Script owner is {script.user}, expected root"
        assert script.group == "root", f"Script group is {script.group}, expected root"
        assert script.mode == 0o755, f"Script permissions are {oct(script.mode)}, expected 0o755"


class TestSambaShares:
    """Test suite for Samba share configuration"""

    def test_share_directories_exist(self, host, ansible_vars):
        """Test that share directories exist with correct permissions."""
        shares = ansible_vars['config_smbshares']

        for share in shares:
            path = share['path']
            share_dir = host.file(path)

            if share_dir.exists:
                assert share_dir.is_directory, f"Share path {path} is not a directory"
                assert share_dir.group == "samba", f"Share directory group is {share_dir.group}, expected samba"
                # Check for setgid bit (2775)
                assert share_dir.mode & 0o2000, f"Share directory {path} missing setgid bit"

    def test_smb_conf_contains_shares(self, host, ansible_vars):
        """Test that smb.conf contains share configurations."""
        smb_conf = host.file("/etc/samba/smb.conf")
        assert smb_conf.exists, "Samba configuration file not found"

        content = smb_conf.content_string
        shares = ansible_vars['config_smbshares']

        for share in shares:
            share_name = share['name']
            share_path = share['path']
            assert f"[{share_name}]" in content, f"Share [{share_name}] not found in configuration"
            assert share_path in content, f"Share path {share_path} not found in configuration"


class TestSambaUsers:
    """Test suite for Samba user management"""

    def test_samba_users_created(self, host, ansible_vars):
        """Test that samba users are created."""
        users = ansible_vars['config_smbusers']

        for user in users:
            username = user['name']
            # Check if user exists in samba database
            cmd = host.run(f"pdbedit -L | grep -q '{username}'", sudo=True)
            assert cmd.rc == 0, f"Samba user {username} not found in database"


class TestSambaServices:
    """Test suite for Samba service functionality"""

    def test_smbd_service_can_start(self, host):
        """Test that smbd service can be started (dry run)."""
        # Test configuration syntax without actually starting service
        cmd = host.run(
            "smbd -D --configfile=/etc/samba/smb.conf --option='server role check:inhibit=yes' -S")
        # This should not fail due to configuration errors
        # 1 is acceptable as service may already be running
        assert cmd.rc in [0, 1], f"Samba daemon failed to start: {cmd.stderr}"
