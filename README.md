# Metasploit Docker Setup

This repository contains a Docker Compose configuration for running Metasploit Framework with PostgreSQL database.

## Quick Start

1. Start the containers:
```bash
docker-compose up -d
```

2. Access Metasploit:
```bash
docker exec -it metasploit /bin/bash
./msfconsole
```

## Container Structure

- **Metasploit Container**: Runs the Metasploit Framework
  - Working directory: `/usr/src/metasploit-framework`
  - msfconsole is located at `./msfconsole` in the working directory
  - Database configuration is automatically set up

- **PostgreSQL Container**: Provides database support
  - Port: 5432
  - Database name: msf
  - Username: msf
  - Password: msf

## Verifying Setup

Once inside msfconsole, you can verify the setup with these commands:

1. Check version:
```bash
version
```

2. Check database connection:
```bash
db_status
```

3. List available modules:
```bash
show exploits
```

## Troubleshooting

If you encounter any issues:

1. Check container logs:
```bash
docker logs metasploit
```

2. Ensure you're in the correct directory:
```bash
pwd  # Should show /usr/src/metasploit-framework
```

3. Verify database connection:
```bash
docker logs metasploit-postgres
```

## Notes

- The Metasploit console must be started from the `/usr/src/metasploit-framework` directory
- Use `./msfconsole` instead of just `msfconsole` as it's not in the system PATH
- Database data is persisted in the `./postgres_data` directory
- Metasploit data is persisted in the `./msf_data` directory 


should be installed pymetasploit3
