"""Docker Client Tests"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
from typing import Any, Optional
from json import dumps
from http.client import HTTPException
from hashlib import sha256
from docker_registry_client import DockerRegistryClient

docker_image_tag_fake_digest: str = sha256(b"Pouet").hexdigest()


class FakeHTTPSConnection:
    """FakeHTTPSConnection Class"""

    def __init__(self, status: int = 200, headers: dict[str, str] | None = None):
        self.status = status
        self.headers = headers if headers else {}

    def request(self, url: str, **_):
        """FakeHTTPSConnection Request Method"""

        self.url = url  # pylint: disable=attribute-defined-outside-init

    def getresponse(self):
        """FakeHTTPSConnection getresponse Method"""

        return FakeHTTPResponse(url=self.url, status=self.status, headers=self.headers)


class FakeHTTPResponse:  # pylint: disable=too-few-public-methods
    """FakeHTTPResponse Class"""

    def __init__(self, url: str, status: int, headers: dict[str, str]):
        self.status = status
        self.url = url
        self.headers = headers

        if status == 200:
            self.reason = "OK"
        if status == 202:
            self.reason = "Accepted"
        if status == 301:
            if url == "/v2/_catalog":
                self.status = 200
                self.reason = "OK"
            self.reason = "Moved Permanently"
        if status == 404:
            self.reason = "Not Found"

    def __to_json(self, obj: Any) -> str:
        return dumps(obj=obj)

    def read(self) -> str:
        """FakeHTTPResponse Read Method"""

        # Get Docker images
        if "/v2/_catalog" in self.url:
            return self.__to_json(
                obj={"repositories": ["fake-alpine", "fake-ubuntu", "fake-python"]}
            )

        # Get Docker image tags
        if "/tags/list" in self.url:
            tags: list[str] = ["a", "b", "c"]
            _, image_name, *_ = self.url.lstrip("/").split("/")
            print(image_name)
            if image_name == "fake-no-tags":
                tags *= 0
            return self.__to_json(obj={"name": image_name, "tags": tags})

        return self.__to_json(obj={})

    def getheader(self, name: str) -> Optional[str]:
        """FakeHTTPResponse Get Header Method"""

        return self.headers.get(name)


class DockerRegistryClientTests(TestCase):
    """Docker Client Tests Class"""

    my_registry_host: str = "docker.registry.example.com"
    my_registry_port: int = 12345
    my_registry_path: str = "/my/awesome/path"
    my_registry_url: str = (
        f"https://{my_registry_host}:{my_registry_port}{my_registry_path}"
    )
    my_ca_file: str = "./tests/certs/example.com.crt"
    my_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
        registry_url=my_registry_url, ca_file=my_ca_file
    )

    def test_init(self):
        """Docker Client Initialization Test"""

        self.assertEqual(
            first=self.my_docker_registry_client.registry_host,
            second=self.my_registry_host,
        )
        self.assertEqual(
            first=self.my_docker_registry_client.registry_port,
            second=self.my_registry_port,
        )
        self.assertEqual(
            first=self.my_docker_registry_client.registry_path,
            second=self.my_registry_path,
        )
        with self.assertRaises(expected_exception=ValueError):
            DockerRegistryClient(
                registry_url="http://insecure.registry.example.com:8080"
            )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection()),
    )
    def test_get_images(self):
        """Docker Client Get Images Test"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345"
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_images(),
            second=["fake-alpine", "fake-ubuntu", "fake-python"],
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection()),
    )
    def test_get_image_tags(self):
        """Docker Client Get Image Tags Test"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345"
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_image_tags(image="fake-no-tags"),
            second=[],
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_image_tags(image="fake-alpine"),
            second=["fake-alpine:a", "fake-alpine:b", "fake-alpine:c"],
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection(status=404)),
    )
    def test_request_404(self):
        """Docker Client Get Image Tags Image Not Found (404)"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345"
        )
        with self.assertRaises(expected_exception=HTTPException):
            my_fake_docker_registry_client.get_image_tags(image="pouet")

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(
            return_value=FakeHTTPSConnection(
                status=301, headers={"location": "/v2/_catalog"}
            )
        ),
    )
    def test_request_301(self):
        """Docker Client Get Images (301)"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345/"
        )

        self.assertEqual(
            first=my_fake_docker_registry_client.get_images(),
            second=["fake-alpine", "fake-ubuntu", "fake-python"],
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(
            return_value=FakeHTTPSConnection(
                status=200,
                headers={"Docker-Content-Digest": docker_image_tag_fake_digest},
            )
        ),
    )
    def test_get_image_tag_digest(self):
        """Docker Client Get Image Tag Digest"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345/"
        )

        self.assertEqual(
            first=my_fake_docker_registry_client.get_image_tag_digest(
                image_tag="fake-ubuntu"
            ),
            second=docker_image_tag_fake_digest,
        )
        self.assertEqual(
            first=my_fake_docker_registry_client.get_image_tag_digest(
                image_tag="fake-ubuntu:22.04"
            ),
            second=docker_image_tag_fake_digest,
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection(status=404)),
    )
    def test_get_image_tag_digest_not_found(self):
        """Docker Client Get Image Tag Digest (404 Not Found)"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345/"
        )

        self.assertIsNone(
            obj=my_fake_docker_registry_client.get_image_tag_digest(
                image_tag="fake-ubuntu"
            )
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection(status=202)),
    )
    def test_delete_image_202(self):
        """Docker Client Delete Docker Image Using Digest"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345/"
        )

        self.assertEqual(
            first=my_fake_docker_registry_client.delete_image(
                image="fake-ubuntu", digest="docker_image_tag_fake_digest"
            ),
            second=True,
        )

    @patch(
        target="docker_registry_client.HTTPSConnection",
        new=MagicMock(return_value=FakeHTTPSConnection(status=404)),
    )
    def test_delete_image_404(self):
        """Docker Client Delete Docker Image Using Digest"""

        my_fake_docker_registry_client: DockerRegistryClient = DockerRegistryClient(
            registry_url="https://fake.registry.example.com:12345/"
        )

        self.assertEqual(
            first=my_fake_docker_registry_client.delete_image(
                image="fake-ubuntu", digest="docker_image_tag_fake_digest"
            ),
            second=False,
        )
