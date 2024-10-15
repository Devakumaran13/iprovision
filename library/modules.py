#!/usr/bin/env python3
import json
import os
import sys
from pprint import pprint

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_version(relative_path, remove_v=False):
    path = os.path.join(BASE_PATH, relative_path)
    with open(path) as file:
        if remove_v:
            return file.read().replace("v", "")
        else:
            return file.read()
        
def load_local_json(relative_path):
    path = os.path.join(BASE_PATH, relative_path)
    with open(path) as file:
        return json.load(file)
    
def update_template_variables(var):
    for key, value in var.items():
        
        #Guess type from default value
        if value.get("default", None) is not None:
            if str(value.get("default")).lower() in ["true", "false"]:
                value_type = value.get("type", "bool")
            elif type(value.get("default")) is map:
                value_type = value.get("type", "map")
            elif type(value.get("default")) is str:
                value_type = value.get("type", "string")
            elif type(value.get("default")) is int:
                value_type = value.get("type", "integer")
            else:
                value_type = value.get("type", "list")
        else:
            value_type = value.get("type", "string")
            
        variable_value_format_function = ""
        
        if value_type == "string":
            variable_default = ''
            variable_value_format = '"%s"'
        elif value_type == "number":
            variable_default = ''
            variable_value_format = '%s'
        elif value_type == "bool":
            variable_default = ''
            variable_value_format = '%s'
            variable_value_format_function = "lower"
        elif value_type.startswith("list") or value_type.startswith("set"):
            variable_default = []
            variable_value_format = '%s'
        elif value_type.startswith("map"):
            variable_default = {}
            variable_value_format = '"%s"'
        else:
            variable_default = '""'
            variable_value_format = "%s"
            
        value.update({
            "value_type": value_type,
            "variable_default": variable_default,
            "variable_value_format": variable_value_format,
            "variable_value_format_function": variable_value_format_function,
        })
    return var

MODULES = {
    "alb": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-alb",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/" + get_version("../modules-metadata/alb_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/alb.json")),
    },
    "nlb": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-nlb",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/" + get_version("../modules-metadata/alb_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/alb.json")),
    },
    "elb": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-elb",
        "registry_url": "../../../../../../../../../../terraform-aws-modules/terraform-aws-elb",
        "variables": update_template_variables(load_local_json("../modules-metadata/elb.json")),
    },
    "eks": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-eks",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/" + get_version("../modules-metadata/eks_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/eks.json")),
    },
    "ecs": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-ecs",
        "registry_url": "../../../../../../../../../../terraform-aws-modules/terraform-aws-ecs",
        "variables": update_template_variables(load_local_json("../modules-metadata/ecs.json")),
    },
    "rds": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-rds",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/" + get_version("../modules-metadata/rds_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/rds.json")),
    },
    
    "autoscaling": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-autoscaling",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/" + get_version("../modules-metadata/autoscaling_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/autoscaling.json")),
    },
    "ec2-instance": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-ec2-instance",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/" + get_version("../modules-metadata/ec2-instance_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/ec2-instance.json")),
    },
    "sns": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-sns",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/" + get_version("../modules-metadata/sns_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/sns.json")),
    },
    "ecr": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-ecr",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/ecr/aws/" + get_version("../modules-metadata/ecr_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/ecr.json")),
    },
    "vpc": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-vpc",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/" + get_version("../modules-metadata/vpc_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/vpc.json")),
    },
    "s3-bucket": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-s3-bucket",
        "registry_url": "../../../../../../../../../../terraform-aws-modules/terraform-aws-s3-bucket",
        "variables": update_template_variables(load_local_json("../modules-metadata/s3-bucket_variable.json")),
    },
    "lambda": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-lambda",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/" + get_version("../modules-metadata/lambda_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/lambda.json")),
    },
    "dynamodb": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-dynamodb",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/dynamodb/aws/" + get_version("../modules-metadata/dynamodb_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/dynamodb.json")),
    },
    "efs": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-efs",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/efs/aws/" + get_version("../modules-metadata/efs_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/efs.json")),
    },
    "sns": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-aws-sns",
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/" + get_version("../modules-metadata/sns_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/sns.json")),
    },
    "resource-group": {
        "source": "../../../../../../../../../../terraform-azurerm-modules/terraform-azurerm-rg",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/terraform-azurerm-rg",
        "variables": update_template_variables(load_local_json("../modules-metadata/resource-group.json")),
    },
    "storage-account": {
        "source": "../../../../../../../../../../terraform-azurerm-modules/terraform-azurerm-sa",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/terraform-azurerm-sa",
        "variables": update_template_variables(load_local_json("../modules-metadata/storage-account.json")),
    },
    "compute": {
        "source": "../../../../../../../../../../terraform-azurerm-modules/terraform-azurerm-compute",
        "registry_url": "https://registry.terraform.io/modules/Azure/compute/azurerm/" + get_version("../modules-metadata/compute_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/compute.json")),
    },
    "vnet": {
        "source": "../../../../../../../../../../terraform-azurerm-modules/terraform-azurerm-vnet",
        "registry_url": "https://registry.terraform.io/modules/Azure/compute/azurerm/" + get_version("../modules-metadata/vnet_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/vnet.json")),
    },
    "vnet-peering": {
        "source": "../../../../../../../../../../terraform-azurerm-modules/virtual_network/peering",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/virtual_network/peering",
        "variables": update_template_variables(load_local_json("../modules-metadata/vnet-peering.json")),
    },
    "private-dns-zone": {
        "source": "../../../../../../../../../../terraform-aws-modules/private_dns_zone",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/virtual_network/peering",
        "variables": update_template_variables(load_local_json("../modules-metadata/private-dns-zone.json")),
    },
    "az-subnet": {
        "source": "../../../../../../../../../../terraform-aws-modules/subnet",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/subnet",
        "variables": update_template_variables(load_local_json("../modules-metadata/az-subnet.json")),
    },
    "network-security-group": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-azurerm-network-security-group",
        "registry_url": "https://registry.terraform.io/modules/Azure/netowk-security-group/azurerm/" + get_version("../modules-metadata/network-security-group_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/network-security-group.json")),
    },
    "aks": {
        "source": "../../../../../../../../../../terraform-aws-modules/terraform-azurerm-aks",
        "registry_url": "https://registry.terraform.io/modules/Azure/aks/azurerm/" + get_version("../modules-metadata/aks_version.txt", True),
        "variables": update_template_variables(load_local_json("../modules-metadata/aks.json")),
    },
    "vmss": {
        "source": "../../../../../../../../../../terraform-aws-modules/vmss",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/vmss",
        "variables": update_template_variables(load_local_json("../modules-metadata/vmss.json")),
    },
    "availability-set": {
        "source": "../../../../../../../../../../terraform-aws-modules/availability-set",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/availability-set",
        "variables": update_template_variables(load_local_json("../modules-metadata/availability-set.json")),
    },
    "route-table": {
        "source": "../../../../../../../../../../terraform-aws-modules/route_table",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/route_table",
        "variables": update_template_variables(load_local_json("../modules-metadata/route_table.json")),
    },
    "route": {
        "source": "../../../../../../../../../../terraform-aws-modules/route_table/route",
        "registry_url": "../../../../../../../../../../terraform-azurerm-modules/route_table/route",
        "variables": update_template_variables(load_local_json("../modules-metadata/route.json")),
    }
}