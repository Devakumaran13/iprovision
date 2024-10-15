#!/usr/bin/env python3
import json
import logging
import random
import string
import uuid
import jmespath
from hashlib import md5
from pprint import pformat, pprint

vpc_in_private_subnets = None
vpc_in_public_subnets = None
def generate_dynamic_params(data, r):
    platform = jmespath.search("nodeDataArray[?uid=='%d'].platform" % r.uid, data)
    if "aws" in platform:
        generate_dynamic_params_aws(data, r)
    elif "azure" in platform:
        generate_dynamic_params_azure(data, r)
    elif "gcp" in platform:
        generate_dynamic_params_gcp(data, r)


def getAllAzsWithinVpc(vpc_key, r, data):
    az_keys = jmespath.search("nodeDataArray[?region=='%s' && resourcetype=='az'].uid" %  r.region, data)
    azs = []
    for az_key in az_keys:
        group = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='az'].group" %  az_key, data)[0]
        group_uid = jmespath.search("nodeDataArray[?key=='%s'].uid" %  group, data)[0]
        if (group_uid == vpc_key):
            azs.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='az'].input_properties.name" %  az_key, data)[0])
    return azs

def getAllPublicSubnetsWithinVpc(r, data):
    public_subnets_keys = jmespath.search("nodeDataArray[?region=='%s' && resourcetype=='subnet' && input_properties.type=='public'].uid" %  r.region, data)
    public_subnets = []
    
    for pub_subnet_key in public_subnets_keys:
        group = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='public'].group" %  pub_subnet_key, data)[0]
        group_uid = jmespath.search("nodeDataArray[?key=='%s'].uid" %  group, data)[0]
        group_name = jmespath.search("nodeDataArray[?key=='%s'].resourcetype" %  group, data)[0] + "-" + str(group_uid)
        if "vpc" in r.type:
            vpc_key = jmespath.search("nodeDataArray[?key=='%s' && resourcetype=='az'].group" %  group, data)[0]
            vpc_group_id = jmespath.search("nodeDataArray[?key=='%s'].uid" %  vpc_key, data)[0]
            if vpc_group_id == r.uid:
                public_subnets.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='public'].input_properties.cidr" %  pub_subnet_key, data)[0])
        if group_name in r.dependencies:
            public_subnets.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='public'].input_properties.cidr" %  pub_subnet_key, data)[0])
    
    for dep in r.dependencies:
        public_subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='public'].input_properties.cidr" %  dep[7:], data)
        if len(public_subnet_cidr) > 0:
            public_subnets.append(public_subnet_cidr[0])
    return public_subnets

def getAllPrivateSubnetsWithinVpc(r, data):
    private_subnets_keys = jmespath.search("nodeDataArray[?region=='%s' && resourcetype=='subnet' && input_properties.type=='private'].uid" %  r.region, data)
    private_subnets = []
    
    for pri_subnet_key in private_subnets_keys:
        group = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='private'].group" %  pri_subnet_key, data)[0]
        group_uid = jmespath.search("nodeDataArray[?key=='%s'].uid" %  group, data)[0]
        group_name = jmespath.search("nodeDataArray[?key=='%s'].resourcetype" %  group, data)[0] + "-" + str(group_uid)
        if "vpc" in r.type:
            vpc_key = jmespath.search("nodeDataArray[?key=='%s' && resourcetype=='az'].group" %  group, data)[0]
            vpc_group_id = jmespath.search("nodeDataArray[?key=='%s'].uid" %  vpc_key, data)[0]
            if vpc_group_id == r.uid:
                private_subnets.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='private'].input_properties.cidr" %  pri_subnet_key, data)[0])
        if group_name in r.dependencies:
            private_subnets.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='private'].input_properties.cidr" %  pri_subnet_key, data)[0])
    
    for dep in r.dependencies:
        private_subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='subnet' && input_properties.type=='private'].input_properties.cidr" %  dep[7:], data)
        if len(private_subnet_cidr) > 0:
            private_subnets.append(private_subnet_cidr[0])
    return private_subnets

def generate_dynamic_params_aws(data, r):
    
    global private_subnets_in_vpc
    global public_subnets_in_vpc
    global vpc_in_public_subnets
    global vpc_in_private_subnets
    
    if vpc_in_private_subnets is None:
        vpc_in_private_subnets = {}
    
    if vpc_in_public_subnets is None:
        vpc_in_public_subnets = {}
    if "vpc" in r.type:
        azs = getAllAzsWithinVpc(r.uid, r, data)
        private_subnets_in_vpc = getAllPrivateSubnetsWithinVpc(r, data)
        public_subnets_in_vpc = getAllPublicSubnetsWithinVpc(r, data)
        vpc_in_public_subnets.update({ "vpc-" + str(r.uid): public_subnets_in_vpc})
        vpc_in_private_subnets.update({ "vpc-" + str(r.uid): private_subnets_in_vpc})
        r.update_dynamic_params("azs", json.dumps(azs))
        r.update_dynamic_params("private_subnets", json.dumps(vpc_in_private_subnets.get("vpc-" + str(r.uid))))
        r.update_dynamic_params("public_subnets", json.dumps(vpc_in_public_subnets.get("vpc-" + str(r.uid))))
    
    if "security-group" in r.type:
        for dep in r.dependencies:
            if "vpc" in dep:
                r.update_dynamic_params("vpc_id", "dependency." + dep + ".outputs.vpc_id")
    if "eks" in r.type:
        subnet_string = ""
        vpc_id = ""
        private_subnet_indices = []
        public_subnet_indices = []
        for i in range(len(r.dependencies)):
            if "vpc" in r.dependencies[i]:
                vpc_id = r.dependencies[i]
        for dep in r.dependencies:
            if "subnet" in dep:
                subnet_type = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.type" %  dep[7:], data)
                subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.cidr" %  dep[7:], data)
                if "private" in subnet_type:
                    private_subnet_index = vpc_in_private_subnets.get(vpc_id).index(subnet_cidr[0])
                    private_subnet_indices.append(private_subnet_index)
                if "public" in subnet_type:
                    public_subnet_index = vpc_in_public_subnets.get(vpc_id).index(subnet_cidr[0])
                    public_subnet_indices.append(public_subnet_index)
                    
            if "vpc" in dep:
                r.update_dynamic_params("vpc_id", "dependency." + dep + ".outputs.vpc_id")
                if "public" in subnet_type:
                    for item in public_subnet_indices:
                        subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.public_subnets" + "[" + str(item) + "]"
                if "private" in subnet_type:
                    for item in private_subnet_indices:
                        subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.private_subnets" + "[" + str(item) + "]"

        r.update_dynamic_params("subnet_ids", "[" + subnet_string.replace(',','',1) + "]")
        
        
    if "autoscaling" in r.type:
        asg_sg_id = 0
        asg_Sg_ids = ""
        subnet_string = ""
        vpc_id = ""
        private_subnet_indices = []
        public_subnet_indices = []
        for i in range(len(r.dependencies)):
            if "vpc" in r.dependencies[i]:
                vpc_id = r.dependencies[i]
        for dep in r.dependencies:
            if "subnet" in dep:
                subnet_type = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.type" %  dep[7:], data)
                subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.cidr" %  dep[7:], data)
                if "private" in subnet_type:
                    private_subnet_index = vpc_in_private_subnets.get(vpc_id).index(subnet_cidr[0])
                    private_subnet_indices.append(private_subnet_index)
                if "public" in subnet_type:
                    public_subnet_index = vpc_in_public_subnets.get(vpc_id).index(subnet_cidr[0])
                    public_subnet_indices.append(public_subnet_index)
                    
            if "vpc" in dep:
                if "public" in subnet_type:
                    for item in public_subnet_indices:
                        subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.public_subnets" + "[" + str(item) + "]"
                if "private" in subnet_type:
                    for item in private_subnet_indices:
                        subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.private_subnets" + "[" + str(item) + "]"
            
            if "security-group" in dep:
                asg_sg_id = asg_sg_id + 1
                asg_sg_ids = asg_sg_ids + "," + "dependency." + dep + ".outputs.security_group_id"
        
        r.update_dynamic_params("vpc_zone_identifier", "[" + subnet_string.replace(',','',1) + "]")
        r.update_dynamic_params("security_groups", "[" + asg_sg_ids.replace(',','',1) + "]")
        
    if "elb" in r.type:
        ec2_sg_id = 0
        ec2_sg_ids = ""
        instance_ids = ""
        instances = 0
        subnet_string = ""
        vpc_id = ""
        private_subnet_indices = []
        public_subnet_indices = []
        for i in range(len(r.dependencies)):
            if "vpc" in r.dependencies[i]:
                vpc_id = r.dependencies[i]
        for dep in r.dependencies:
            if "subnet" in dep:
                subnet_type = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.type" %  dep[7:], data)
                subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.cidr" %  dep[7:], data)
                if "private" in subnet_type:
                        private_subnet_index = vpc_in_private_subnets.get(vpc_id).index(subnet_cidr[0])
                        private_subnet_indices.append(private_subnet_index)
                if "public" in subnet_type:
                        public_subnet_index = vpc_in_public_subnets.get(vpc_id).index(subnet_cidr[0])
                        public_subnet_indices.append(public_subnet_index)
                        
            if "vpc" in dep:
                    if "public" in subnet_type:
                        for item in public_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.public_subnets" + "[" + str(item) + "]"
                    if "private" in subnet_type:
                        for item in private_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.private_subnets" + "[" + str(item) + "]"
                
            if "security-group" in dep:
                    ec2_sg_id = ec2_sg_id + 1
                    ec2_sg_ids = ec2_sg_ids + "," + "dependency." + dep + ".outputs.security_group_id"
                    
            if "ec2-instance" in dep:
                    instances = instances + 1
                    instances_ids = instance_ids + "," + "dependency." + dep + ".outputs.id[0]"
            
        r.update_dynamic_params("security_groups", "[" + ec2_sg_ids.replace(',','',1) + "]")
        r.update_dynamic_params("subnets", "[" + subnet_string.replace(',','',1) + "]")
        r.update_dynamic_params("instances", "[" + instance_ids.replace(',','',1) + "]")
        r.update_dynamic_params("number_of_instances", str(instances))
                
        
    if "s3-bucket" in r.type:
            r.update_dynamic_params("region", json.dumps(r.region))
    if "lambda" in r.type:
            r.update_dynamic_params("region", json.dumps(r.region))
    if "efs" in r.type:
            r.update_dynamic_params("region", json.dumps(r.region))
    if "sns" in r.type:
            r.update_dynamic_params("region", json.dumps(r.region))
    if "dynamodb" in r.type:
            r.update_dynamic_params("region", json.dumps(r.region))
            
    if "network-firewall" in r.type:
            subnet_string = ""
            vpc_id = ""
            private_subnet_indices = []
            public_subnet_indices = []
            for i in range(len(r.dependencies)):
                if "vpc" in r.dependencies[i]:
                    vpc_id = r.dependencies[i]
            for dep in r.dependencies:
                if "subnet" in dep:
                    subnet_type = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.type" %  dep[7:], data)
                    subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.cidr" %  dep[7:], data)
                    if "private" in subnet_type:
                        private_subnet_index = vpc_in_private_subnets.get(vpc_id).index(subnet_cidr[0])
                        private_subnet_indices.append(private_subnet_index)
                    if "public" in subnet_type:
                        public_subnet_index = vpc_in_public_subnets.get(vpc_id).index(subnet_cidr[0])
                        public_subnet_indices.append(public_subnet_index)
                        
                if "vpc" in dep:
                    if "public" in subnet_type:
                        for item in public_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.public_subnets" + "[" + str(item) + "]"
                    if "private" in subnet_type:
                        for item in private_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.private_subnets" + "[" + str(item) + "]"
                
            r.update_dynamic_params("subnet_id", '"' + subnet_string.replace(',','',1) + '"')
            r.update_dynamic_params("vpc_id", "dependency." + dep + ".outputs.vpc_id")
            
    if "ebs" in r.type:
            group = jmespath.search("nodeDataArray[?uid=='%s'].group" % r.uid, data)[0]
            group_id = jmespath.search("nodeDataArray[?uid=='%s'].uid" % group, data)[0]
            az_name = jmespath.search("nodeDataArray[?uid=='%s'].input_properties.name" % group_uid, data)[0]
            r.update_dynamic_params("availability_zone", f'"{az_name}"')
            for dep in r.dependencies:
                if "ec2-instance" in dep:
                    r.update_dynamic_params("instance_id", "dependency." + dep + ".outputs.id[0]")
                    
    if "eip" in r.type:
            for dep in r.dependencies:
                if "ec2-instance" in dep:
                    r.update_dynamic_params("instance_id", "dependency." + dep + ".outputs.id[0]")
        
    if "ec2-instance" in r.type:
            ec2_sg_id = 0
            ec2_sg_ids = ""
            subnet_string = ""
            vpc_id = ""
            private_subnet_indices = []
            public_subnet_indices = []
            for i in range(len(r.dependencies)):
                if "vpc" in r.dependencies[i]:
                    vpc_id = r.dependencies[i]
            for dep in r.dependencies:
                if "subnet" in dep:
                    subnet_type = jmespath.search("nodeDataArray[?uid=='%s'].input_properties.type" %  dep[7:], data)
                    subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s'].input_properties.cidr" %  dep[7:], data)
                    if "private" in subnet_type:
                        private_subnet_index = vpc_in_private_subnets.get(vpc_id).index(subnet_cidr[0])
                        private_subnet_indices.append(private_subnet_index)
                    if "public" in subnet_type:
                        public_subnet_index = vpc_in_public_subnets.get(vpc_id).index(subnet_cidr[0])
                        public_subnet_indices.append(public_subnet_index)
                        
                if "vpc" in dep:
                    if "public" in subnet_type:
                        for item in public_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.public_subnets" + "[" + str(item) + "]"
                    if "private" in subnet_type:
                        for item in private_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.private_subnets" + "[" + str(item) + "]"
                
                if "security-group" in dep:
                    ec2_sg_id = ec2_sg_id + 1
                    ec2_sg_ids = ec2_sg_ids + "," + "dependency." + dep + ".outputs.security_group_id"
            r.update_dynamic_params("vpc_security_group_ids", "[" + ec2_sg_ids.replace(',','',1) + "]")
            r.update_dynamic_params("subnet_id", "[" + subnet_string.replace(',','',1) + "]")
            
                    
    if "vpc" in r.type:
            for dep in r.dependencies:
                if "vpc" in dep:
                    r.update_dynamic_params("peer_vpc_id", "dependency." + dep + ".outputs.vpc_id")
                    r.update_dynamic_params("peer_owner_id", "dependency." + dep + ".outputs.vpc_owner_id")
                    
    if "vpc-endpoint" in r.type:
            for dep in r.dependencies:
                if "vpc" in dep:
                    r.update_dynamic_params("vpc_id", "dependency." + dep + ".outputs.vpc_id")
                    r.update_dynamic_params("public_route_table_ids", "dependency." + dep + ".outputs.public_route_table_ids")
                    
    if "nat-gateway" in r.type:
            subnet_string = ""
            vpc_id = ""
            private_subnet_indices = []
            public_subnet_indices = []
            for i in range(len(r.dependencies)):
                if "vpc" in r.dependencies[i]:
                    vpc_id = r.dependencies[i]
            for dep in r.dependencies:
                if "subnet" in dep:
                    subnet_type = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.type" %  dep[7:], data)
                    subnet_cidr = jmespath.search("nodeDataArray[?uid=='%s'.input_properties.cidr" %  dep[7:], data)
                    if "private" in subnet_type:
                        private_subnet_index = vpc_in_private_subnets.get(vpc_id).index(subnet_cidr[0])
                        private_subnet_indices.append(private_subnet_index)
                    if "public" in subnet_type:
                        public_subnet_index = vpc_in_public_subnets.get(vpc_id).index(subnet_cidr[0])
                        public_subnet_indices.append(public_subnet_index)
                        
                if "vpc" in dep:
                    if "public" in subnet_type:
                        for item in public_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.public_subnets" + "[" + str(item) + "]"
                    if "private" in subnet_type:
                        for item in private_subnet_indices:
                            subnet_string = subnet_string + "," + "dependency." + dep + ".outputs.private_subnets" + "[" + str(item) + "]"
                            
                if "eip" in dep:
                    r.update_dynamic_params("eip_id", "dependency." + dep + ".outputs.eip_id")
            
            r.update_dynamic_params("subnet_id", '' + subnet_string.replace(',','',1) + '')
            
            
            
def generate_dynamic_params_gcp(data, r):
    print("Test GCP")
    
def getAllSubnetsWithinVnet(r, data):
    az_subnets_keys = jmespath.search("nodeDataArray[?region=='%s' && resourcetype=='azsubnet'].uid" % r.region, data)
    az_subnets = []
    az_subnet_names = []
    az_subnet_uids = []
    
    for az_subnet_key in az_subnets_keys:
        group = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='azsubnet'].group" % az_subnet_key, data)[0]
        group_uid = jmespath.search("nodeDataArray[?key=='%s'].uid" % group, data)[0]
        group_name = jmespath.search("nodeDataArray[?uid=='%s'].resourcetype" % group, data)[0] + "-" + str(group_uid)
        if "vnet" in group_name:
            az_subnets.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='azsubnet'].input_properties.subnet_prefix" % az_subnet_key, data)[0])
            az_subnet_names.append(jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='azsubnet'].input_properties.subnet_name" % az_subnet_key, data)[0])
    return (az_subnets, az_subnet_names)

def getNSGAssociations(data, r):
    nsg_keys = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='network-security-group'].uid" % r.region, data)
    nsg_string = ""
    az_subnets_id = jmespath.search("nodeDataArray[?region=='%s' && resourcetype=='azsubnet'].uid" % r.region, data)
    for nsg_key in nsg_keys:
        for az_subnet_id in az_subnets_ids:
            dep_key = jmespath.search("nodeDataArray[?uid=='%d'].key" % az_subnet_id, data)[0]
            nsg_match_key = jmespath.search("linkDataArray[?to=='%d'].from" % dep_key, data)[0]
            nsg_match_id = jmespath.search("nodeDataArray[?key=='%d' && resourcetype=='network-security-group'].uid" % nsg_match_key, data)[0]
            if nsg_key == nsg_match_id:
                az_subnet_name = jmespath.search("nodeDataArray[?uid=='%s' && resourcetype=='azsubnet'].input_properties.subnet_name" % az_subnet_id, data)[0]
                nsg_id = "network-sercurity-group" + "-" + str(nsg_key)
                nsg_id_string = "dependency." + nsg_id + ".outputs.network_security_group_id"
                nsg_string = nsg_string + ", " + az_subnet_name + ": " +nsg_id_string
    nsg_string_final = "{ " + nsg_string[1:] + " }"
    return nsg_string_final

def generate_dynamic_params_azure(data, r):
    
    (az_subnets, az_subnet_names) = getAllSubnetsWithinVnet(r, data)
    
    if "vnet" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
                r.update_dynamic_params("nsg_ids", getNSGAssociations(data, r))
                r.update_dynamic_params("subnet_names", json.dumps(az_subnet_names))
                r.update_dynamic_params("subnet_prefixes", json.dumps(az_subnets))
        
    if "storage-account" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
    
    if "iot-hub" in r.type:
        for dep in r.dependencies:
            if "event-hub-namespace" in dep:
                r.update_dynamic_params("namespace_name", "dependency." + dep + ".outputs.name")
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
    
    if "waf" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
                
    if "mssql-server" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
    
    if "vnet-peering" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
            if "vnet" in dep:
                r.update_dynamic_params("remote_virtual_network_id", "dependency." + dep + ".outputs.id")
    
    
    if "az-subnet" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
            if "vnet" in dep:
                r.update_dynamic_params("virtual_network_name", "dependency." + dep + ".outputs.virtual_network_name")
            if "network-security-group" in dep:
                r.update_dynamic_params("network_security_group_id", "dependency." + dep + ".outputs.network_security_group_id")
            if "route-table" in dep:
                r.update_dynamic_params("route_table_id", "dependency." + dep + ".outputs.route_table_id")
                
    if "vmss" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
            if "az-subnet" in dep:
                r.update_dynamic_params("subnet_name", "dependency." + dep + ".outputs.name")
                r.update_dynamic_params("virtual_network_name", "dependency." + dep + ".outputs.virtual_network_name")
                
    
    if "route-table" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
            
    if "route" in r.type:
        for dep in r.dependencies:
            if "resource-group" in dep:
                r.update_dynamic_params("resource_group_name", "dependency." + dep + ".outputs.resource_group_name")
            if "route-table" in dep:
                r.update_dynamic_params("route_table_id", "dependency." + dep + ".outputs.route_table_id")
            
                
               
                
                