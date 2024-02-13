"""Configuration"""

from typing import Final, Optional
from os import getenv
from utils import str2bool

LOGGING_LEVEL: Final[str] = getenv(key="LOGGING_LEVEL", default="INFO")
DOCKER_REGISTRY_URL: Final[str] = getenv(key="DOCKER_REGISTRY_URL", default="")
DOCKER_REGISTRY_CA_FILE: Final[Optional[str]] = getenv(key="DOCKER_REGISTRY_CA_FILE")
DOCKER_IMAGES_FILTER: Final[str] = getenv(key="DOCKER_IMAGES_FILTER", default=r".*")
DOCKER_TAGS_FILTER: Final[str] = getenv(key="DOCKER_TAGS_FILTER", default=r".*")
IMAGE_LIST_NBR_MAX: Final[int] = int(getenv(key="IMAGE_LIST_NBR_MAX", default="1000"))
HTTPS_CONNECTION_TIMEOUT: Final[int] = int(
    getenv(key="HTTP_CONNECTION_TIMEOUT", default="3")
)
FORCE: Final[bool] = str2bool(string=getenv(key="FORCE", default="NO"))
DRY_RUN: Final[bool] = str2bool(string=getenv(key="DRY_RUN", default="YES"))
