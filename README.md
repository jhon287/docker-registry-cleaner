# Docker Registry Cleaner

## Description

TODO

## Configuration

### Environment Variables

- `LOGGING_LEVEL`: (Optional) Logging level needed. Can be `DEBUG`, `INFO`, `WARNING` or `CRITICAL`. (Default: `INFO`)
- `DOCKER_REGISTRY_URL`: **(Required)** Docker registry **HTTPS** URL that needs to be scanned. (e.g. `https://docker-registry.example.com:12345/path/to/repository/`)
- `DOCKER_REGISTRY_CA_FILE`: (Optional) PEM format file of CA.
- `DOCKER_IMAGES_FILTER`: (Optional) REGEX pattern used to filter Docker images. (Default: `.*`)
- `DOCKER_TAGS_FILTER`: (Optional) REGEX pattern used to filter Docker image tags. (Default: `.*`)
- `IMAGE_LIST_NBR_MAX`: (Optional) Maximum number of Docker images that needs to be fetch from Docker registry. (Default: `1000`)
- `HTTPS_CONNECTION_TIMEOUT`: (Optional) Docker registry client HTTPS connection timeout. (Default: `3`)
- `FORCE`: (Optional) This option is useful only if you give "dangerous" regex patterns such as '`.*`'. (Default: `NO`)
- `DRY_RUN`: (Optional) This option make sure you can run the cleaner without really delete Docker images. It is enabled by default to avoid mistakes. (Default: `YES`)
