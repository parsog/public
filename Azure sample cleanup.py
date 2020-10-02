
import os
import traceback
import json
import re

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.sql import SqlManagementClient

from msrestazure.azure_exceptions import CloudError




def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    results = extract(obj, arr, key)
    return results

# Azure Datacenter
LOCATION = 'westus'

def get_credentials():
    # put your Azure creds here
    subscription_id = ''
    credentials = ServicePrincipalCredentials(
        client_id='',
        secret='',
        tenant=''
    )
    return credentials, subscription_id

def list_vms_subscription():
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    all_vms = compute_client.virtual_machines.list_all()
    #print(all_vms)
    for vm in compute_client.virtual_machines.list_all():
            print("\tVM: {}".format(vm.name))

def list_resource_groups(vm_name):
    credentials, subscription_id = get_credentials()
    client = ResourceManagementClient(credentials, subscription_id)
    for item in client.resource_groups.list():
        res_group = item.name
        vmname = item.tags
        jd = json.dumps(vmname)
        jl = json.loads(jd)
        v_name = extract_values(jl,'__relatedTo')
        if vmname != None:
            v_name = v_name[0]
            if v_name == vm_name:
                return res_group


def delete_vms_subscription():
    credentials, subscription_id = get_credentials()
    compute_client = ComputeManagementClient(credentials, subscription_id)
    for vm in compute_client.virtual_machines.list_all():
        vm_name = vm.name
        res_group = list_resource_groups(vm_name)
        async_vm_delete = compute_client.virtual_machines.delete(res_group,vm_name)
        async_vm_delete.wait()
        print("Deleted VM: {}".format(vm.name))

def list_subscriptions():
    credentials, subscription_id = get_credentials()
    client = ResourceManagementClient(credentials, subscription_id)
    resource_groups = client.resource_groups.list()
    for item in client.resource_groups.list():
        print(item)
        print('\r')

def list_databases():
    credentials, subscription_id = get_credentials()
    sql_client = SqlManagementClient(credentials, subscription_id)
    sql_arry = []
    for item in sql_client.servers.list():
        db_id = item.id
        regex_string = 'resourceGroups\/(.*)\/providers'
        resource_group = re.search(regex_string, db_id).group(1)
        sql_arry.append([resource_group,item.name])
    return(sql_arry)

def delete_databases(sql_list):
    credentials, subscription_id = get_credentials()
    sql_client = SqlManagementClient(credentials, subscription_id)
    for item in sql_list:
        rg = item[0]
        dbName = item[1]
        sql_client.servers.delete(rg, dbName)

#delete_vms_subscription()
#list_subscriptions()
#list_vms_subscription()
#list_databases()
sql_servers = list_databases()
print(sql_servers)
#delete_databases(sql_servers)
