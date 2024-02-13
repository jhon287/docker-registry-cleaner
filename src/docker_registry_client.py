"""Docker Registry Client"""

from http.client import HTTPSConnection, HTTPResponse, HTTPException
from urllib.parse import urlparse, ParseResult
from json import loads
from re import search
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
from typing import Optional
from logger import logger


class DockerRegistryClient:
    """DockerRegistryClient Class"""

    https_connection: HTTPSConnection
    registry_host: str
    registry_port: int
    registry_path: str

    def __init__(
        self,
        registry_url: str,
        ca_file: Optional[str] = None,
        timeout: int = 3,
    ) -> None:
        if not registry_url.startswith("https://"):
            raise ValueError("Docker registry URL must start with 'https://'")

        parse_result: ParseResult = urlparse(url=registry_url)

        self.registry_host: str = parse_result.hostname if parse_result.hostname else ""
        self.registry_port: int = parse_result.port if parse_result.port else 443
        self.registry_path = parse_result.path

        ssl_context: SSLContext = SSLContext(
            protocol=PROTOCOL_TLS_CLIENT, verify_mode=CERT_REQUIRED
        )
        if ca_file:
            ssl_context.load_verify_locations(cafile=ca_file)
        else:
            ssl_context.load_default_certs()
        self.https_connection = HTTPSConnection(  # nosemgrep: bandit.B309
            host=self.registry_host,
            port=self.registry_port,
            timeout=timeout,
            context=ssl_context,
        )

    def __request(self, url: str, method: str = "GET") -> bytes | None:
        self.https_connection.request(method=method, url=url)
        response: HTTPResponse = self.https_connection.getresponse()
        if response.status not in range(200, 300):
            # Detect redirect URL
            location_header: Optional[str] = response.getheader(name="location")
            if location_header is not None:
                logger.info(msg=f"Redirect detected: {url} -> {location_header}")
                # Avoid http.client.ResponseNotReady: Request-sent
                _ = response.read()
                return self.__request(url=location_header, method=method)

            # Raise HTTPException
            raise HTTPException(
                f"Received HTTP code != 200: {response.status} -> {response.reason}"
            )
        body: bytes | None = response.read()
        return loads(body) if body else body

    def __request_get_header_value(
        self, url: str, headers: dict[str, str], header_name: str
    ) -> str | None:
        self.https_connection.request(method="HEAD", url=url, headers=headers)
        response: HTTPResponse = self.https_connection.getresponse()
        if response.status != 200:
            # Avoid http.client.ResponseNotReady: Request-sent
            _ = response.read()
            # Raise HTTPException
            raise HTTPException(
                "Received HTTP code != 200: "
                f"{response.status} -> {response.reason} ({url=})"
            )
        value: str | None = response.getheader(name=header_name)
        # Avoid http.client.ResponseNotReady: Request-sent
        _ = response.read()
        return value if value is not None else ""

    def get_images(self, number_max: int = 500, pattern: str = r".*") -> list[str]:
        """DockerClient Get Images Method"""

        images: list[str] = dict(
            self.__request(url=f"{self.registry_path}/v2/_catalog?n={number_max}")
        ).get("repositories")

        return [image for image in images if search(pattern=pattern, string=image)]

    def get_image_tags(self, image: str, pattern: str = r".*") -> list[str]:
        """DockerClient Get Image Tags Method"""

        tags: list[str] = dict(
            self.__request(url=f"{self.registry_path}/v2/{image}/tags/list")
        ).get("tags")
        if not tags:
            return []
        return [f"{image}:{tag}" for tag in tags if search(pattern=pattern, string=tag)]

    def get_image_tag_digest(self, image_tag: str) -> str | None:
        """Method that returns Docker image digest"""

        try:
            (image, tag) = image_tag.split(":")
        except ValueError:
            image: str = image_tag
            tag: str = "latest"

        url: str = f"/v2/{image}/manifests/{tag}"

        try:
            return self.__request_get_header_value(
                url=url,
                headers={
                    "Accept": "application/vnd.docker.distribution.manifest.v2+json"
                },
                header_name="Docker-Content-Digest",
            )
        except HTTPException:
            try:
                return self.__request_get_header_value(
                    url=url,
                    headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
                    header_name="Docker-Content-Digest",
                )
            except HTTPException:
                return None

    def delete_image(self, image: str, digest: str) -> bool:
        """Method that delete a Docker image using digest"""

        try:
            self.__request(url=f"/v2/{image}/manifests/{digest}", method="DELETE")
        except HTTPException as exception:
            logger.warning(msg=exception)
            return False
        return True
