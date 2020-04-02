# -*- coding: utf-8 -*-
from django.test import TestCase

from yosim.rules.models import Rule, RuleLevel
from yosim.utilities.collector import XMLCollector
from yosim.utilities.utilities import (
    get_default_ossec_params, get_absolute_path
)

RULES_COUNT = 0
RULE_LEVELS = [
    {
        'number': 0,
        'common_name': 'Ignored',
        'description': 'No action taken. Used to avoid false positives. These \
        rules are scanned before all the others. They include events with no \
        security relevance.',
    },
    {
        'number': 1,
        'common_name': 'None',
        'description': 'None',
    },
    {
        'number': 2,
        'common_name': 'System low priority notification',
        'description': 'System notification or status messages. They have \
        no security relevance.',
    },
    {
        'number': 3,
        'common_name': 'Successful/Authorized events',
        'description': 'They include successful login attempts, firewall \
        allow events, etc.',
    },
    {
        'number': 4,
        'common_name': 'System low priority error',
        'description': 'Errors related to bad configurations or unused \
        devices/applications. They have no security relevance and are \
        usually caused by default installations or software testing.',
    },
    {
        'number': 5,
        'common_name': 'User generated error',
        'description': 'They include missed passwords, denied actions, \
        etc. By itself they have no security relevance.',
    },
    {
        'number': 6,
        'common_name': 'Low relevance attack',
        'description': 'They indicate a worm or a virus that have no \
        affect to the system (like code red for apache servers, etc). \
        They also include frequently IDS events and frequently errors.',
    },
    {
        'number': 7,
        'common_name': '"Bad word" matching',
        'description': 'They include words like “bad”, “error”, etc. \
        These events are most of the time unclassified and may have \
        some security relevance.',
    },
    {
        'number': 8,
        'common_name': 'First time seen',
        'description': 'Include first time seen events. First time an \
        IDS event is fired or the first time an user logged in. If you \
        just started using OSSEC HIDS these messages will probably be \
        frequently. After a while they should go away, It also includes \
        security relevant actions (like the starting of a sniffer or \
        something like that).',
    },
    {
        'number': 9,
        'common_name': 'Error from invalid source',
        'description': 'Include attempts to login as an unknown user \
        or from an invalid source. May have security relevance (specially \
        if repeated). They also include errors regarding the “admin” \
        (root) account.',
    },
    {
        'number': 10,
        'common_name': 'Multiple user generated errors',
        'description': 'They include multiple bad passwords, multiple \
        failed logins, etc. They may indicate an attack or may just be \
        that a user just forgot his credencials.',
    },
    {
        'number': 11,
        'common_name': 'Integrity checking warning',
        'description': 'They include messages regarding the modification \
        of binaries or the presence of rootkits (by rootcheck). If you \
        just modified your system configuration you should be fine \
        regarding the “syscheck” messages. They may indicate a \successful \
        attack. Also included IDS events that will be ignored (high number \
        of repetitions).',
    },
    {
        'number': 12,
        'common_name': 'High importancy event',
        'description': 'They include error or warning messages from \
        the system, kernel, etc. They may indicate an attack against \
        a specific application.',
    },
    {
        'number': 13,
        'common_name': 'Unusual error (high importance)',
        'description': 'Most of the times it matches a common attack pattern.',
    },
    {
        'number': 14,
        'common_name': 'High importance security event',
        'description': 'Most of the times done with correlation and it \
        indicates an attack.',
    },
    {
        'number': 15,
        'common_name': 'Severe attack',
        'description': 'No chances of false positives. Immediate \
        attention is necessary.',
    },
]


class TestRules(TestCase):
    def filter_rules(self, xmlparse):
        global RULES_COUNT
        # get var tag and value
        defined_vars = {}
        for var in xmlparse.iter('var'):
            defined_vars[var.attrib['name']] = var.text

        # loop each group
        for group in xmlparse.iter('group'):
            # if check group has attr
            if group.attrib:
                categories = group.attrib['name'].split(',')
                categories = [category.strip()
                              for category in categories if category]
                # loop each rule
                for rule in group.iter('rule'):
                    arule = {}
                    arule['category'] = ", ".join(categories)

                    # get rule attributes
                    for key, value in rule.attrib.items():
                        arule[key] = value

                    # change id key
                    arule['rule_id'] = arule.pop('id')

                    if 'ignore' in arule:
                        arule['ignore_attr'] = arule.pop('ignore')

                    for child in rule:
                        if child.tag in arule:
                            arule[child.tag] = arule[child.tag]
                            + "| " + child.text
                        else:
                            arule[child.tag] = child.text

                    # format group
                    if 'group' in arule:
                        groups = arule['group'].split(',')
                        groups = [group.strip() for group in groups if group]
                        arule['group'] = ", ".join(groups)

                    # convert None type to "Yes"
                    for key, value in arule.items():
                        if value is None:
                            arule[key] = "Yes"

                    # change list key
                    if 'list' in arule:
                        arule['rule_list'] = arule.pop('list')

                    # change nested id key
                    if 'id' in arule:
                        arule['regex_id'] = arule.pop('id')

                    # get all fields in Rule
                    fields = [f.name for f in Rule._meta.get_fields()]

                    # avoid dictionary changed size during iteration
                    arule['unknown'] = ''
                    # push all unknown tag to unknown field
                    for key, value in arule.items():
                        if key not in fields:
                            unknown_data = arule['unknown']
                            + key + ": " + value + "| "
                            arule['unknown'] = unknown_data.rstrip("| ")

                    if defined_vars:
                        for key, value in arule.items():
                            for name, text in defined_vars.items():
                                var_name = "$" + name
                                if value == var_name:
                                    arule[key] = text

                    RULES_COUNT += 1
                    # get rule level object
                    arule['level'] = RuleLevel.objects.get(
                        number=arule['level'])
                    # create rule object
                    rule, created = Rule.objects.update_or_create(**arule)
                    print("Collect rule id: {}".format(rule.rule_id))
                    self.assertTrue(rule)

    def test_01_get_rules(self):
        print('Collecting rule levels....')
        for RULE_LEVEL in RULE_LEVELS:
            rule_level, created = RuleLevel.objects.update_or_create(
                **RULE_LEVEL)
            print("Collect rule level id: {}".format(rule_level.number))
            self.assertTrue(rule_level)

        print("Collecting rules....")
        params = get_default_ossec_params()
        rule_dir = get_absolute_path(params['DIRECTORY'], 'rules')
        xmlcollector = XMLCollector(rule_dir)
        xmlparses = xmlcollector.get_parsed_xml_files()

        for xmlparse in xmlparses:
            self.filter_rules(xmlparse)

        print("Total collected rules: {}".format(RULES_COUNT))
