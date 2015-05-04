# Docker Build Hook

Deploys a webhook environment for your docker infrastructure.

This allows you to create a 'project' with the dockerfile charm and trigger
continuous builds/cycling containers from a github project. The `dockerfile`
charm receives 3 variables: abspath to deploy, git repository, and the build script.

from here, browse to the endpoint of your docker host(s) on port `8080` and verify
you have a JSON api responding.


    {
      hooks: [
        {
            cwd: null,
            command: "/home/ubuntu/dockerfile/docker-selfoss/build.sh",
            name: "docker-selfoss",
            repository: "docker-selfoss",
            branch: "master"
        },
        {
            cwd: null,
            command: "/home/ubuntu/dockerfile/docker-mumble/build.sh",
            name: "docker-mumble",
            repository: "docker-mumble",
            branch: "master"
        }
      ],
      success: true
    }

Plug the Host/IP into your github projects webhooks and Viola! On every push
your dockerfile repository will be pulled, and whatever logic in 'build.sh' will
be executed.

This charm also ships with `build-hook.py` located in `/home/ubuntu/hooked`

This build hook exposes several convenience methods, such as starting containers
and executing build routines w/ image cleanup

    usage: build-hook [-h] -r REPO -t TAG [--no-kill] [-s SCRIPT] [-v] [--debug]

    A build hook intended to run Docker container builds on a live system

    optional arguments:
      -h, --help            show this help message and exit
      -r REPO, --repo REPO  Repository warehousing a Dockerfile
      -t TAG, --tag TAG     Docker tag to apply to the build
      --no-kill             Do not kill existing container
      -s SCRIPT, --script SCRIPT
                            path to start script
      -v, --verbose
      --debug

For example - your `build.sh` might look like the following:

    #!/bin/bash

    /home/ubuntu/hooked/build-hook.py -r $HOME/dockerfile/docker-mumble -t mumble -s $HOME/dockerfile/docker-mumble/start.sh -v &


Deploy
------

    juju deploy trusty/docker
    juju set docker latest=true version=1.6.0
    juju deploy cs:~lazypower/docker-build-hook
    juju add-relation docker-build-hook docker

![](http://i.imgur.com/QmXwe7H.png)


Caveats
---------

This charm is experimental at best, and should be considered not ready for use
by anyone but the bravest of souls wishing to deploy a 'build on site' docker
host.

I find this to be great in a staging / testing environment, but for production
usage you may want to go with the Docker Registry / Private registry approach
and only pull down images you've already tagged/vett'd appropriately. This will
consume CPU on the host, and may tank builds, and take out other containers
with it if you're doing something really hairy in your build scripts.

YMMV




