import time
import docker
import logging


try:
    from Config.base_config import BaseConfig
    from Config.container_names import DockerContainerNames

except ModuleNotFoundError:
    from ..Config.base_config import BaseConfig
    from ..Config.container_names import DockerContainerNames

logging.basicConfig(level=logging.INFO)


class DockerIntegration(object):
    docker_client = docker.from_env()

    @classmethod
    def get_all_docker_containers(cls):
        """
        Returns a list of all running docker containers names (char '/' removed)
        @return: list of strings
        """
        containers = cls.docker_client.containers()
        all_running_containers = [str(x['Names'][0]).strip('/') for x in containers]
        return all_running_containers

    @classmethod
    def get_container_by_name(cls, container_name):
        """
        Returns a container object by name. It is recommended to use DockerContainers Enum when entering
        the container name.
        Example: get_container_by_name(DockerContainers.FEE_SERVICE.value)
        @param container_name: string
        @return: Container object
        """
        containers = cls.docker_client.containers()

        for container in containers:
            if str(container['Names'][0]).strip('/') == container_name:
                return container

    @classmethod
    def restart_container(cls, container_name):
        """
        Finds docker container by provided name and restarts it. It is recommended to use
        DockerContainers Enum when entering the container name.
        @param container_name: string
        @return: True on success, False on failure
        """
        container_to_restart = cls.get_container_by_name(container_name)
        if container_to_restart is None:
            logging.error(f"Didn't find running docker container with name {container_name}")
            return False

        try:
            cls.docker_client.restart(container_to_restart)
            logging.info(f"Restarted container {container_to_restart['Image']}")
            return True

        except Exception as e:
            logging.error(f"Failed to restart docker container {container_name} - {e}")
            return False

    @classmethod
    def stop_container(cls, container_name):
        """
        Finds docker container by provided name and stops it. It is recommended to use
        DockerContainers Enum when entering the container name.

        TO START A CONTAINER THAT WAS STOPPED save the 'container' object before stopping it.
        Call docker_client.start(container_to_start) method, passing the saved container to it.

        @param container_name: string
        @return: Container object on success, False on failure
        """
        container_to_stop = cls.get_container_by_name(container_name)
        if container_to_stop is None:
            logging.error(f"Didn't find running docker container with name {container_name}")
            return False

        try:
            cls.docker_client.stop(container_to_stop)
            return container_to_stop

        except Exception as e:
            logging.error(f"Failed to stop docker container {container_name} - {e}")
            return False

    @classmethod
    def start_container(cls, container):
        """
        This method can be used to start docker container that was earlier stopped.
        Expects a container object (stopped container)
        @param container: stopped container
        @return: True on success, False on failure
        """
        try:
            cls.docker_client.start(container)
            return True

        except Exception as e:
            logging.error(f"Failed to start stopped container - {e}")
            return False


if __name__ == '__main__':
    print(DockerIntegration.get_all_docker_containers())

    a = DockerIntegration.get_container_by_name("creditto_creditto_matcher_1")
    b = DockerIntegration.stop_container(DockerContainerNames.GATEWAY.value)
    time.sleep(6)
    DockerIntegration.start_container(b)