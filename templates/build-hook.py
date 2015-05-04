#!/usr/bin/env python

import argparse
from docker import Client
import logging
import shlex
from subprocess import check_call

logger = logging.getLogger('build-hook')
logger.setLevel(logging.INFO)

def setup_logging(verbose=None, debug=None):
    logger = logging.getLogger('build-hook')
    logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    if verbose:
        f = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    else:
        f = '%(levelname)s %(name)s: %(message)s'

    formatter = logging.Formatter(f)
    ch.setFormatter(formatter)

    if verbose is None:
        ch = logging.NullHandler()

    logger.addHandler(ch)
    return logger

def setup_parser():
    p = argparse.ArgumentParser(prog='build-hook',
                                description='A build hook intended to run'
                                            ' Docker container builds on'
                                            ' a live system')
    p.add_argument('-r', '--repo', required=True,
                   help='Repository warehousing a Dockerfile')
    p.add_argument('-t','--tag', required=True,
                   help='Docker tag to apply to the build')
    p.add_argument('--no-kill', action='store_true',
                   help='Do not kill existing container')
    p.add_argument('-s', '--script', help="path to start script")
    p.add_argument('-v', '--verbose', action='store_true')
    p.add_argument('--debug', action='store_true')
    return p

def setup_docker_client():
    cli = Client(base_url='unix://var/run/docker.sock')
    return cli

def find_running_container(cli, tag, log):
    containers = cli.containers()

    for c in containers:
        if c['Image'] == "{}:latest".format(tag):
            log.warn("Container {} scheduled for nuking "
                     "after build".format(c['Id']))
            return c['Id']
    log.info("No container found... continuing build")

def build(cli, repo, tag, log):
    log.info("Starting build... please wait, this can take some time")
    try:
        response = [line for line in cli.build(path=repo, nocache=True, rm=True, tag=tag)]
    except:
        log.critical("Build failed, dumping response")
        for line in response:
            log.critical(line)
        return False

    log.info("Build Succeeded!")
    return True

def main(args=None):
    parser = setup_parser()
    known, unknown = parser.parse_known_args(args)
    log = setup_logging(verbose=known.verbose, debug=known.debug)

    cli = setup_docker_client()

    if not known.no_kill:
        running_container = find_running_container(cli, known.tag, log)


    build_status = build(cli, known.repo, known.tag, log)
    if not build_status:
        log.warn('Known build failure. Exiting prematurely')
        return

    if not known.no_kill and running_container:
        log.warn("Killing existing container {}".format(running_container))
        cli.kill(running_container)

    if known.script:
        log.info("Calling startup script: {}".format(known.script))
        check_call(known.script)
    else:
        cmd = "docker run -d {}".format(known.tag)
        log.info("Calling startup with generated default: {}".format(cmd))
        check_call(shlex.split(cmd))

if __name__ == "__main__":
    main()
