# -*- coding: utf-8 -*-
from sys import maxsize
from unittest.mock import MagicMock, patch

import pytest

from chaosaws.asg.probes import (desired_equals_healthy,
                                 desired_equals_healthy_tags,
                                 is_scaling_in_progress,
                                 wait_desired_equals_healthy,
                                 wait_desired_equals_healthy_tags,
                                 wait_desired_not_equals_healthy_tags,
                                 process_is_suspended)
from chaoslib.exceptions import FailedActivity


def test_desired_equals_healthy_needs_asg_names():
    with pytest.raises(FailedActivity) as x:
        desired_equals_healthy([])
    assert "Non-empty list of auto scaling groups is required" in str(x)


def test_wait_desired_equals_healthy_asg_names():
    with pytest.raises(FailedActivity) as x:
        wait_desired_equals_healthy([])
    assert "Non-empty list of auto scaling groups is required" in str(x)


def test_desired_equals_healthy_tags_needs_tags():
    with pytest.raises(FailedActivity) as x:
        desired_equals_healthy_tags([])
    assert "Non-empty tags is required" in str(x)


def test_wait_desired_equals_healthy_tags_needs_tags():
    with pytest.raises(FailedActivity) as x:
        wait_desired_equals_healthy_tags([])
    assert "Non-empty tags is required" in str(x)


def test_wait_desired_not_equals_healthy_tags_needs_tags():
    with pytest.raises(FailedActivity) as x:
        wait_desired_not_equals_healthy_tags([])
    assert "Non-empty tags is required" in str(x)


def test_is_scaling_in_progress():
    with pytest.raises(FailedActivity) as x:
        is_scaling_in_progress([])
    assert "Non-empty tags is required" in str(x)


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_desired_equals_healthy_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup1', 'AutoScalingGroup2']
    client.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [{
            "DesiredCapacity": 1,
            "Instances": [{
                "HealthStatus": "Healthy",
                "LifecycleState": "InService"
            }]
        }]
    }
    assert desired_equals_healthy(asg_names=asg_names) is True


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_desired_equals_healthy_false(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup1', 'AutoScalingGroup2']
    client.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [{
            "DesiredCapacity": 1,
            "Instances": [{
                "HealthStatus": "Unhealthy",
                "LifecycleState": "InService"
            }]
        }]
    }
    assert desired_equals_healthy(asg_names=asg_names) is False


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_desired_equals_healthy_empty(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup1', 'AutoScalingGroup2']
    client.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [
        ]
    }
    assert desired_equals_healthy(asg_names=asg_names) is False


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_wait_desired_equals_healthy_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup1']
    client.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [{
            "DesiredCapacity": 1,
            "Instances": [{
                "HealthStatus": "Healthy",
                "LifecycleState": "InService"
            }]
        }]
    }
    assert wait_desired_equals_healthy(
        asg_names=asg_names, timeout=0.1) in [0, 2]


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_wait_desired_equals_healthy_timeout(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup1']
    client.describe_auto_scaling_groups.response = [
        {
            "AutoScalingGroups": [{
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "Initializing"
                }]
            }]
        }
    ]
    assert wait_desired_equals_healthy(
        asg_names=asg_names, timeout=0) is maxsize


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_desired_equals_healthy_tags_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Healthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Healthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            },
            {
                'AutoScalingGroupName': 'AutoScalingGroup2',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'NOTmychaosapp'
                }]
            }
        ]},
        {
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup3',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'NOTApplication',
                    'Value': 'mychaosapp'
                }]
            }]
    }]
    assert desired_equals_healthy_tags(tags=tags) is True


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_desired_equals_healthy_tags_false(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Unhealthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            },
            {
                'AutoScalingGroupName': 'AutoScalingGroup2',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'NOTmychaosapp'
                }]
            }
        ]},
        {
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup3',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'NOTApplication',
                    'Value': 'mychaosapp'
                }]
            }]
    }]
    assert desired_equals_healthy_tags(tags=tags) is False


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_wait_desired_equals_healthy_tags_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Healthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Healthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            },
            {
                'AutoScalingGroupName': 'AutoScalingGroup2',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'NOTmychaosapp'
                }]
            }
        ]},
        {
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup3',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'NOTApplication',
                    'Value': 'mychaosapp'
                }]
            }]
    }]
    assert wait_desired_equals_healthy_tags(tags=tags, timeout=0.1) in [0, 2]


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_wait_desired_equals_healthy_tags_false(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Unhealthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            },
            {
                'AutoScalingGroupName': 'AutoScalingGroup2',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'NOTmychaosapp'
                }]
            }
        ]},
        {
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup3',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'NOTApplication',
                    'Value': 'mychaosapp'
                }]
            }]
    }]
    assert wait_desired_equals_healthy_tags(tags=tags, timeout=0) is maxsize


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_wait_desired_not_equals_healthy_tags_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Unhealthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            },
            {
                'AutoScalingGroupName': 'AutoScalingGroup2',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'NOTmychaosapp'
                }]
            }
        ]},
        {
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup3',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            }]
    }]
    assert wait_desired_not_equals_healthy_tags(
        tags=tags, timeout=0.2) in [0, 2]


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_wait_desired_not_equals_healthy_tags_false(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Healthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            },
            {
                'AutoScalingGroupName': 'AutoScalingGroup2',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Unhealthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'NOTmychaosapp'
                }]
            }
        ]
    }]
    assert wait_desired_not_equals_healthy_tags(
        tags=tags, timeout=0) is maxsize


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_is_scaling_in_progress_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Healthy",
                        "LifecycleState": "OutOfService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Healthy",
                    "LifecycleState": "OutOfService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            }
        ]
    }]
    assert is_scaling_in_progress(tags=tags) is True


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_is_scaling_in_progress_false(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'Application', 'Value': 'mychaosapp'}]
    client.describe_auto_scaling_groups.return_value = \
        {
            "AutoScalingGroups": [
                {
                    'AutoScalingGroupName': 'AutoScalingGroup1',
                    "DesiredCapacity": 1,
                    "Instances": [{
                        "HealthStatus": "Healthy",
                        "LifecycleState": "InService"
                    }],
                    'Tags': [{
                        'ResourceId': 'AutoScalingGroup1',
                        'Key': 'Application',
                        'Value': 'mychaosapp'
                    }]
                }
            ]
        }
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [
            {
                'AutoScalingGroupName': 'AutoScalingGroup1',
                "DesiredCapacity": 1,
                "Instances": [{
                    "HealthStatus": "Healthy",
                    "LifecycleState": "InService"
                }],
                'Tags': [{
                    'ResourceId': 'AutoScalingGroup1',
                    'Key': 'Application',
                    'Value': 'mychaosapp'
                }]
            }
        ]
    }]
    assert is_scaling_in_progress(tags=tags) is False


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_is_process_suspended_names_true(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup-A']
    process_names = ['Launch']
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [{
            "AutoScalingGroupName": "AutoScalingGroup-A",
            "SuspendedProcesses": [{
                "ProcessName": "Launch"
            }]}]}]
    assert process_is_suspended(
        asg_names=asg_names, process_names=process_names) is True
    assert client.suspend


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_is_process_suspended_names_false(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    asg_names = ['AutoScalingGroup-A']
    process_names = ['Launch']
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [{
            "AutoScalingGroupName": "AutoScalingGroup-A",
            "SuspendedProcesses": [{"ProcessName": "AZRebalance"}]}]}]
    assert process_is_suspended(
        asg_names=asg_names, process_names=process_names) is False
    assert client.suspend


@patch('chaosaws.asg.probes.aws_client', autospec=True)
def test_is_process_suspended_tags(aws_client):
    client = MagicMock()
    aws_client.return_value = client
    tags = [{'Key': 'TestKey', 'Value': 'TestValue'}]
    process_names = ['Launch']
    client.get_paginator.return_value.paginate.return_value = [{
        "AutoScalingGroups": [{
            "AutoScalingGroupName": "AutoScalingGroup-A",
            "SuspendedProcesses": ["Launch"],
            "Tags": [{
                "ResourceId": "AutoScalingGroup-A",
                "Key": "TestKey",
                "Value": "TestValue"}]}]}]
    client.describe_auto_scaling_groups.return_value = {
        "AutoScalingGroups": [{
            "AutoScalingGroupName": "AutoScalingGroup-A",
            "SuspendedProcesses": [{
                "ProcessName": "Launch"
            }]}]}
    assert process_is_suspended(
        tags=tags, process_names=process_names) is True
