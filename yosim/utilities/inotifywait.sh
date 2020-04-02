#!/bin/bash

# while inotifywait -e close_write yosim/syschecks/tests/test_get_syschecks.py; do
while inotifywait -e close_write yosim/settings/tests/test_config_file.py; do
# while inotifywait -e close_write scripts/collect_syschecks.py; do
    # sudo ~/.virtualenvs/yosim/bin/python manage.py runscript collect_syschecks -v3;
    # sudo ~/.virtualenvs/yosim/bin/python manage.py test --keepdb yosim.syschecks.tests.test_get_syschecks
    sudo ~/.virtualenvs/yosim/bin/python manage.py test --keepdb yosim.settings.tests.test_config_file
done
