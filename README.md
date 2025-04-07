# EasyBox - Advanced Application Containerization System

## Overview

EasyBox is a sophisticated application containerization and management system designed to simplify the deployment, versioning, and execution of software packages. The system provides a structured approach to application lifecycle management with features including dependency resolution, version tracking, metadata management, and rollback capabilities.

## Key Features

- **Secure User Authentication**: Utilizes bcrypt hashing for credential storage with SQLite backend
- **Application Containerization**: Isolated installation and execution environments with resource limits
- **Version Control**: SHA-256 hashing for version identification and change detection
- **Dependency Management**: Automated dependency resolution and installation
- **Metadata Tracking**: Comprehensive JSON-based logging of installation and execution history
- **Rollback Support**: Complete removal of applications including metadata
- **Dry Run Mode**: Preview installation operations without system changes
- **Configuration Management**: JSON-based system configuration persistence
- **Compose Support**: YAML-based multi-application deployment
- **Resource Isolation**: CPU and memory limits for containerized applications
- **Logging System**: Detailed installation and operation logging

## System Architecture

### Core Components

1. **User Authentication Subsystem**
   - SQLite-backed credential storage
   - BCrypt password hashing with salt generation
   - Sessionless authentication model

2. **Application Management Engine**
   - XML-based application definition (easybox)
   - YAML compose file support
   - Dependency resolution pipeline
   - Content-addressable storage for application packages
   - Temporary file handling for downloads

3. **Metadata Tracking System**
   - Installation timestamps
   - Version hashes
   - Execution history logging
   - JSON-based metadata storage
   - Per-application metadata files

4. **Containerization Layer**
   - Application isolation with chroot
   - Version-aware execution
   - Clean uninstallation paths
   - Resource limits (CPU, memory)

5. **Utility Functions**
   - File hashing (SHA-256)
   - Archive handling (tar.gz)
   - Network operations
   - Subprocess management

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/linuxfanboy4/EasyBox/refs/heads/main/install.sh | bash
```

The installation script will:
1. Create necessary system directories (installed_apps, app_metadata)
2. Initialize the SQLite user database (users.db)
3. Set up the default easybox configuration (easybox_config.json)
4. Establish the application metadata framework
5. Create empty easybox XML definition file
6. Set up installation log file (install.log)

## Configuration

System-wide configuration is managed through `easybox_config.json` with the following default structure:

```json
{
    "install_path": "./",
    "logging_level": "info"
}
```

## Command Reference

### User Management

**Register New User:**
```bash
easybox auth <username> <password>
```

**Authenticate User:**
```bash
easybox log <username> <password>
```

### Application Management

**Install Application:**
```bash
easybox install <app_name> [--dry-run] [additional_args]
easybox eb install <app_name> [--dry-run] [additional_args]
```

**Rollback Installation:**
```bash
easybox rollback <app_name>
easybox eb rollback <app_name>
```

**List Installed Applications:**
```bash
easybox list
easybox eb list
```

**View Application Information:**
```bash
easybox info <app_name>
easybox eb info <app_name>
```

**Update Application:**
```bash
easybox update <app_name>
easybox eb update <app_name>
```

**Deploy from Compose File:**
```bash
easybox compose <compose_file.yml>
easybox eb compose <compose_file.yml>
```

## File Formats

### Application Definition (XML)

```xml
<easybox>
    <application>
        <Name>ApplicationName</Name>
        <Dependencies>dependency1, dependency2</Dependencies>
        <RawLink>https://raw.url/to/package.tar.gz</RawLink>
        <StartCMD>optional_start_command</StartCMD>
    </application>
</easybox>
```

### Compose File (YAML)

```yaml
applications:
  - name: app1
    dependencies: "dep1, dep2"
    raw_link: "https://example.com/app1.tar.gz"
    start_cmd: "./start.sh"
    args: ["--port=8080"]
  - name: app2
    raw_link: "https://example.com/app2.tar.gz"
```

### Metadata Structure (JSON)

```json
{
    "name": "ApplicationName",
    "installed_at": "timestamp",
    "version": "sha256_hash",
    "runs": ["timestamp1", "timestamp2"]
}
```

## Security Model

- All passwords are hashed using BCrypt with automatic salt generation
- Application packages are verified using SHA-256 hashes
- Metadata files maintain strict isolation between applications
- No elevation privileges are required for standard operations
- Containerized applications run with resource limits (CPU, memory)
- Temporary files are securely handled during downloads

## Performance Considerations

1. **Hashing Operations**: SHA-256 calculations are performed on all application packages for version control
2. **Dependency Installation**: Sequential installation of dependencies
3. **Metadata Storage**: JSON files are kept minimal to reduce I/O overhead
4. **Network Operations**: Downloads are streamed to memory for hash calculation
5. **Resource Limits**: Default limits of 10 CPU seconds and 100MB memory per container

## Troubleshooting

1. **Installation Failures**:
   - Verify network connectivity for raw link access
   - Check dependency compatibility
   - Review install.log for detailed error messages
   - Check available disk space

2. **Authentication Issues**:
   - Confirm database file permissions
   - Verify credential input formatting
   - Check users.db exists and is accessible

3. **Version Mismatches**:
   - Compare local and remote package hashes
   - Check for corrupted downloads
   - Verify metadata files are intact

4. **Container Issues**:
   - Check resource limits are sufficient
   - Verify StartCMD is correct
   - Review execution logs in metadata

## Best Practices

1. **Application Definitions**:
   - Use absolute URLs for RawLink elements
   - Specify exact dependency versions where possible
   - Include StartCMD only when necessary
   - Test compose files before production use

2. **System Management**:
   - Regularly back up the metadata directory
   - Monitor the install.log for unusual activity
   - Periodically review installed applications
   - Maintain separate environments for testing and production

3. **Security**:
   - Use strong passwords for authentication
   - Only download from trusted sources
   - Regularly review installed applications
   - Monitor resource usage of containers

## Extension Points

1. **Custom Hashing Algorithms**: Modify the calculate_file_hash functions to support alternative hashing methods
2. **Additional Metadata**: Extend the metadata JSON schema to include custom fields
3. **Alternative Storage Backends**: Replace SQLite with other database systems by modifying the user table functions
4. **Additional Archive Formats**: Extend shutil.unpack_archive support
5. **Network Configuration**: Add proxy support for downloads

## Limitations

1. Network-dependent operations require stable internet connectivity
2. Dependency resolution is currently limited to shell command execution
3. Windows support requires additional compatibility layers
4. Limited to tar.gz archive format for applications
5. Resource limits are fixed at container level

## Versioning Policy

EasyBox follows semantic versioning for its own releases. Application versions are managed through content hashing rather than traditional version numbers.

## License

This project is licensed under the terms of the MIT license. See the LICENSE file for details.

## Support

For support issues, please review the project documentation or open an issue in the project repository. Include relevant logs from install.log and metadata files when reporting issues.
