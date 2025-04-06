# EasyBox - Advanced Application Containerization System

## Overview

EasyBox is a sophisticated application containerization and management system designed to simplify the deployment, versioning, and execution of software packages. The system provides a structured approach to application lifecycle management with features including dependency resolution, version tracking, metadata management, and rollback capabilities.

## Key Features

- **Secure User Authentication**: Utilizes bcrypt hashing for credential storage
- **Application Containerization**: Isolated installation and execution environments
- **Version Control**: SHA-256 hashing for version identification and change detection
- **Dependency Management**: Automated dependency resolution and installation
- **Metadata Tracking**: Comprehensive logging of installation and execution history
- **Rollback Support**: Safe uninstallation and version reversion capabilities
- **Dry Run Mode**: Preview installation operations without system changes
- **Configuration Management**: JSON-based system configuration persistence

## System Architecture

### Core Components

1. **User Authentication Subsystem**
   - SQLite-backed credential storage
   - BCrypt password hashing
   - Sessionless authentication model

2. **Application Management Engine**
   - XML-based application definition (easybox)
   - Dependency resolution pipeline
   - Content-addressable storage for application packages

3. **Metadata Tracking System**
   - Installation timestamps
   - Version hashes
   - Execution history logging
   - JSON-based metadata storage

4. **Containerization Layer**
   - Application isolation
   - Version-aware execution
   - Clean uninstallation paths

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/linuxfanboy4/EasyBox/refs/heads/main/install.sh | bash
```

The installation script will:
1. Create necessary system directories
2. Initialize the SQLite user database
3. Set up the default easybox configuration
4. Establish the application metadata framework

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
```

**Rollback Installation:**
```bash
easybox rollback <app_name>
```

**List Installed Applications:**
```bash
easybox list
```

**View Application Information:**
```bash
easybox info <app_name>
```

**Update Application:**
```bash
easybox update <app_name>
```

## Application Definition Format

Applications are defined in the `easybox` XML file with the following structure:

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

## Metadata Structure

Each installed application maintains metadata in JSON format:

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

## Performance Considerations

1. **Hashing Operations**: SHA-256 calculations are performed on all application packages for version control
2. **Dependency Installation**: Parallel installation of dependencies is recommended for large dependency sets
3. **Metadata Storage**: JSON files are kept minimal to reduce I/O overhead

## Troubleshooting

1. **Installation Failures**:
   - Verify network connectivity for raw link access
   - Check dependency compatibility
   - Review install.log for detailed error messages

2. **Authentication Issues**:
   - Confirm database file permissions
   - Verify credential input formatting

3. **Version Mismatches**:
   - Compare local and remote package hashes
   - Check for corrupted downloads

## Best Practices

1. **Application Definitions**:
   - Use absolute URLs for RawLink elements
   - Specify exact dependency versions where possible
   - Include StartCMD only when necessary

2. **System Management**:
   - Regularly back up the metadata directory
   - Monitor the install.log for unusual activity
   - Periodically review installed applications

## Extension Points

1. **Custom Hashing Algorithms**: Modify the calculate_file_hash functions to support alternative hashing methods
2. **Additional Metadata**: Extend the metadata JSON schema to include custom fields
3. **Alternative Storage Backends**: Replace SQLite with other database systems by modifying the user table functions

## Limitations

1. Network-dependent operations require stable internet connectivity
2. Dependency resolution is currently limited to shell command execution
3. Windows support requires additional compatibility layers

## Versioning Policy

EasyBox follows semantic versioning for its own releases. Application versions are managed through content hashing rather than traditional version numbers.

## License

This project is licensed under the terms of the MIT license. See the LICENSE file for details.

## Support

For support issues, please review the project documentation or open an issue in the project repository.
