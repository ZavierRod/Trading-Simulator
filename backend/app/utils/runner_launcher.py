
import os
os.environ.pop("DOCKER_HOST", None)

import docker
# Force the SDK to use the Unix socket inside the container

def launch_runner(strategy_id: int, feed_file: str):
    """
    Fire-and-forget ‘trading-simulation-game-runner’ container
    that executes the given strategy against the feed_file.
    """
    # Connect directly to the local Unix socket instead of relying on
    # DOCKER_HOST to avoid the “http+docker” URLSchemeUnknown error.
    client = docker.DockerClient(base_url="unix:///var/run/docker.sock")

    # Same image name docker-compose builds
    image = "trading-simulation-game-runner:latest"

    # Share network namespace with backend container so
    # ‘backend:8000’ keeps working inside runner
    network_mode = "service:backend"

    client.containers.run(
        image,
        command=[str(strategy_id), feed_file],   # runner.py already accepts these
        network_mode=network_mode,
        remove=True,        # auto-cleanup when done
        volumes={
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"},  # <- make sure compose mounts this too
        },
        detach=True,        # non-blocking
        environment={
            "PYTHONUNBUFFERED": "1",   # nicer logging order
        },
    )