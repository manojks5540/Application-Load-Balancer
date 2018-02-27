#!/usr/bin/python2.7

import boto3
import boto
import boto.utils
import os
import socket
import requests
import json
import time

## VARIABLES

### AWS
access_key = '####################'
secret_key = '############################'
region = 'AWS region'
targets = [['Target group name', 'Port']]

client = boto3.client('elbv2', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

def instance_health(instance, arn, portnumber):

        response = client.describe_target_health(
            TargetGroupArn=arn,
            Targets=[
                {
                    'Id': instance,
                    'Port': portnumber
                },
            ]
        )

        array = json.dumps(response)

        data=json.loads(array)

        return data["TargetHealthDescriptions"][0]["TargetHealth"]["State"]

def target_arn(target_group):

        response = client.describe_target_groups(
            Names=[
                target_group,
            ],
            Marker='string',
            PageSize=123
        )

        array = json.dumps(response)

        data=json.loads(array)

        return data["TargetGroups"][0]["TargetGroupArn"]

def remove_from_target(target_name, instance_port):

        arn_name = target_arn(target_name)

        instance_id = boto.utils.get_instance_metadata()['instance-id']

        response2 = client.deregister_targets(
            TargetGroupArn=arn_name,
            Targets=[
                {
                    'Id': instance_id,
                    'Port': instance_port
                },
            ],
        )

        start = time.time()
        msg = 'removing host from target ' 

        try:
            slack('warning', msg)
        except:
            pass

        timeout = time.time() + 60*5

        while True:
                health = instance_health(instance_id, arn_name, instance_port)
                assert time.time() < timeout
                if health == 'unused':
                    break
                time.sleep(5)

        msg = 'host successfully removed from target' 
        
        try:
            slack('good',msg)
        except:
            pass


if __name__ == "__main__":
      for target in targets:
        TargetName = target[0]
        TargetPort = int(target[1])
        remove_from_target(TargetName, TargetPort)

