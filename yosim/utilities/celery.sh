#!/bin/bash

# restart celery supervisor
sudo pkill -9 -f "yosim.taskapp"
sudo supervisorctl stop all
sudo supervisorctl start yosim_celery
