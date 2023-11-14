ARG PYTHON_VERSION

FROM python:"${PYTHON_VERSION}-slim"

WORKDIR /app

COPY src/ .

# DL3008 warning: Pin versions in apt get install
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && adduser --disabled-password --comment "Docker Registry Cleaner" cleaner \
    && chown -R cleaner:cleaner . \
    && pip uninstall -y setuptools

USER cleaner

ENV TZ="Europe/Brussels" \
    PYTHONUNBUFFERED="1"

ENTRYPOINT [ "python", "main.py" ]
