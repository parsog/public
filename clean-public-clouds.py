# Resets the public cloud accounts for all key sets in the hol_dynamodb.json file
# Use this to delete all elastic load balancers and instances in AWS

import boto3
import json

cred_file = "point_to_file_with_account_credentials.json"
list_only = False    #Set to True if you just want counts of the resources but don't want to delete them

def clean_aws(tx_aws_access,tx_aws_secret,tx_region):
    ec2 = boto3.client('ec2',aws_access_key_id=tx_aws_access, aws_secret_access_key=tx_aws_secret, region_name=tx_region)
    ec2_response = ec2.describe_instances()

    instance_count = 0    # number of ec2 instances
    for reservation in ec2_response["Reservations"]:
        for instance in reservation["Instances"]:
            # This will get the value of the Dictionary key 'InstanceId'
            inst_id = instance["InstanceId"]
            inst_state = instance["State"]["Name"]
            if inst_state == 'running':     #instances stay in "terminated" state for a while - only want to terminate running instances
                if not list_only:
                    hi = ec2.terminate_instances(InstanceIds=[inst_id])
                instance_count += 1   # increment counter

    lb_count = 0  # number of elastic load balancers
    elb = boto3.client('elbv2',aws_access_key_id=tx_aws_access, aws_secret_access_key=tx_aws_secret, region_name=tx_region)
    elb_response = elb.describe_load_balancers()
    for elbs in elb_response['LoadBalancers']:
        elb_arn = elbs['LoadBalancerArn']
        elb_name = elbs['LoadBalancerName']
        elb_state = elbs['State']['Code']
        if elb_state == 'active':
            if not list_only:
                del_lbs = elb.delete_load_balancer(LoadBalancerArn=elb_arn)
            lb_count += 1     # increment counter
    
    asg_count = 0  # number of auto scaling groups
    asg = boto3.client('autoscaling',aws_access_key_id=tx_aws_access, aws_secret_access_key=tx_aws_secret, region_name=tx_region)
    asg_response = asg.describe_auto_scaling_groups()
    for auto_groups in asg_response['AutoScalingGroups']:
        asg_name = auto_groups['AutoScalingGroupName']
        if not list_only:
            del_asg = asg.delete_auto_scaling_group(
                AutoScalingGroupName=asg_name,
                ForceDelete=True
            )
        asg_count += 1

    aslc_count = 0  # number of auto scaling launch configurations
    aslc_response = asg.describe_launch_configurations()
    for launch_configs in aslc_response['LaunchConfigurations']:
        aslc_name = launch_configs['LaunchConfigurationName']
        if not list_only:
            del_aslc = asg.delete_launch_configuration(LaunchConfigurationName=aslc_name)
        aslc_count += 1

    return(instance_count,lb_count,asg_count, aslc_count)
    


##### MAIN
if list_only:
    action = "Counted"
else:
    action = "Deleted"
with open(cred_file) as json_file:
    keysets = json.load(json_file)
    for keyset in keysets:
        pod = keyset['pod']
        aws_access_key = keyset['aws_access_key']
        aws_secret_key = keyset['aws_secret_key']
        azure_subscription_id = keyset['azure_subscription_id']
        azure_tenant_id = keyset['azure_tenant_id']
        azure_application_id = keyset['azure_application_id']
        azure_application_key = keyset['azure_application_key']
        in_use = keyset['in_use']
        reserved = keyset['reserved']
       
        aws_region = 'us-west-1'
        num_ec2,num_lb,num_asg, num_aslc = clean_aws(aws_access_key,aws_secret_key,aws_region)
        if (num_ec2 > 0) or (num_lb > 0) or (num_asg > 0) or (num_aslc > 0):
            print(action, num_ec2, "EC2 instances,", num_lb, "load balancers", num_asg, "autoscale groups", num_aslc, "autoscale launch configurations in", aws_region, "for", pod)
        
        aws_region = 'us-west-2'
        num_ec2,num_lb,num_asg, num_aslc = clean_aws(aws_access_key,aws_secret_key,aws_region)
        if (num_ec2 > 0) or (num_lb > 0) or (num_asg > 0) or (num_aslc > 0):
            print(action, num_ec2, "EC2 instances,", num_lb, "load balancers", num_asg, "autoscale groups", num_aslc, "autoscale launch configurations in", aws_region, "for", pod)



        





