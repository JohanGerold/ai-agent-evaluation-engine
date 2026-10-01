FROM python:3.13.15-slim-bookworm@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26
ARG SOURCE_REVISION=uncommitted
LABEL org.opencontainers.image.revision=$SOURCE_REVISION
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /opt/aap
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt
COPY dist/*.whl ./dist/
RUN python -m pip install --no-cache-dir --no-deps dist/*.whl && rm -rf dist
COPY manage.py ./
USER 10001:10001
EXPOSE 8000
# Foundation only; override with python -m app.worker for the refusing worker entrypoint.
CMD ["waitress-serve", "--host=127.0.0.1", "--port=8000", "--threads=2", "app.config.wsgi:application"]
