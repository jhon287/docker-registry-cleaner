"""Docker Registry Cleaner Main"""

from docker_registry_client import DockerRegistryClient
from logger import logger
from utils import str2bool, is_valid_url, check_pattern, get_percentage
import config


def log_summary(deleted: list[str], failed: list[str]) -> None:
    """Function that logs summary information"""

    total: int = len(deleted) + len(failed)
    for kind, images, emoji in [
        ("deleted", deleted, "🟢"),
        ("failed", failed, "🔴"),
    ]:
        if not images:
            continue

        logger.info(
            msg=(
                f"{emoji} Total {kind} Docker images: {len(images):>3} "
                f"({get_percentage(nbr_a=len(images), nbr_b=total):.2%})"
                f" -> {sorted(images)}"
            )
        )


def main() -> None:
    """Main Function"""

    if not is_valid_url(url=config.DOCKER_REGISTRY_URL):
        raise ValueError(
            "Unvalid Docker registry URL ($DOCKER_REGISTRY_URL), "
            "it needs to start with 'https://'."
        )

    for kind, pattern in {
        "images": config.DOCKER_IMAGES_FILTER,
        "tags": config.DOCKER_TAGS_FILTER,
    }.items():
        logger.info(msg=f"🧐 Checking filter ({kind=} ({pattern=})")
        check_pattern(pattern=pattern, force=str2bool(config.FORCE))

    client = DockerRegistryClient(
        registry_url=config.DOCKER_REGISTRY_URL,
        timeout=config.HTTPS_CONNECTION_TIMEOUT,
        ca_file=config.DOCKER_REGISTRY_CA_FILE,
    )

    image_tags_deleted: list[str] = []
    image_tags_failed: list[str] = []

    # Get Docker images
    images: list[str] = client.get_images(
        number_max=config.IMAGE_LIST_NBR_MAX, pattern=config.DOCKER_IMAGES_FILTER
    )

    logger.info(msg=f"💡 Number of Docker images: {len(images)}")

    for image in images:
        # Get all tags of Docker image
        image_tags: list[str] = client.get_image_tags(
            image=image, pattern=config.DOCKER_TAGS_FILTER
        )

        logger.info(
            msg=(
                "💡 Number of Docker tags marked as deletion"
                f" for '{image}': {len(image_tags)}"
            )
        )

        # No Docker image tags found
        if not image_tags:
            tags_filer: str = config.DOCKER_TAGS_FILTER
            logger.warning(msg=f"🤡 No Docker tags found ({image=} {tags_filer=})")
            continue

        for image_tag in sorted(image_tags):
            # Get Docker image digest
            if (digest := client.get_image_tag_digest(image_tag=image_tag)) is None:
                logger.warning(
                    msg=f"❌ Error: cannot get digest for Docker image '{image_tag}"
                )
                continue

            (name, tag) = image_tag.split(":")

            message: str = (
                f"🔫 Deleting Docker image '{name}:{tag}' using digest '{digest}'"
            )

            if str2bool(string=config.DRY_RUN):
                logger.info(msg=f"{message} (DRY-RUN)")
                continue

            logger.info(msg=message)

            # Delete Docker image using digest
            if client.delete_image(image=image, digest=digest):
                logger.info(
                    msg=f"✅ Docker image '{image_tag}' ({digest}) deleted successfully"
                )
                image_tags_deleted.append(f"{image_tag} ({digest})")
            else:
                logger.warning(
                    msg=(
                        "❌ Error while trying to delete Docker image "
                        f"'{image_tag}' ({digest})"
                    )
                )
                image_tags_failed.append(f"{image_tag} ({digest})")

    # Log summary
    log_summary(deleted=image_tags_deleted, failed=image_tags_failed)


if __name__ == "__main__":
    main()
