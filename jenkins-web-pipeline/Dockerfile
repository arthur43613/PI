FROM jenkins/jenkins:lts

USER root

# Install git, docker, docker-compose
RUN apt-get update && apt-get install -y git docker.io docker-compose

ARG DOCKER_GID=1001

RUN groupdel docker || true \
    && groupadd -g ${DOCKER_GID} docker \
    && usermod -aG docker jenkins \
    && id jenkins \
    && getent group docker

USER jenkins

RUN whoami && id && groups
