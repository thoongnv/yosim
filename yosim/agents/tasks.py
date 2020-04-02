# -*- coding: utf-8 -*-
import subprocess
from datetime import timedelta
from celery.task import periodic_task
from celery.utils.log import get_task_logger

from ..servers.models import Server
from .models import Agent

logger = get_task_logger(__name__)


@periodic_task(run_every=timedelta(seconds=30), bind=True)
def collect_agents(self):
    process = subprocess.Popen(['/var/ossec/bin/agent_control', '-ls'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.stdout.read()
    lines = output.decode('ascii').splitlines()
    default_server_id = Server.objects.get(pk=1)
    for line in lines:
        if line:
            parts = line.split(',')
            defaults = {
                'server': default_server_id,
                'agent_id': parts[0],
                'name': parts[1],
                'ip_address': parts[2],
                'agent_status': parts[3],
            }
            agent, created = Agent.objects.update_or_create(
                agent_id=defaults['agent_id'], defaults=defaults)
            if created:
                logger.info("New agent: {0} with ip address: {1}".format(
                    agent.name, agent.ip_address))
            else:
                logger.info("Update existing agent: {0}".format(agent.name))
            agent.save()
