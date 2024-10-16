#!/usr/bin/env python3
import json
import logging
from pickle import TRUE
import random
import string
import uuid
import jmespath
import requests
import petname
import re
from hashlib import md5
from pprint import pformat, pprint
from library.dynamicparams import generate_dynamic_params, generate_dynamic_params_aws, generate_dynamic_params_gcp, generate_dynamic_params_azure

class iotData:
    def __init__(self, platform, location, subscription, resourceName, kubernetsVersion, vnetAddressPrefix, networkSecurityGroupName, vnetName, virtualMachineName, virtualMachineSize, destinationPortRange, isARMTemplate, services, aks_uid):
        self.platform = platform
        self.location = location
        self.subscription = subscription
        self.resourceName = resourceName
        self.kubernetsVersion = kubernetsVersion
        self.vnetAddressPrefix = vnetAddressPrefix
        self.networkSecurityGroupName = networkSecurityGroupName
        self.vnetName = vnetName
        self.virtualMachineName =virtualMachineName
        self.virtualMachineSize =virtualMachineSize
        self.destinationPortRange = destinationPortRange
        self.isARMTemplate = isARMTemplate
        self.services = services
        self.aks_uid = aks_uid
        
    def conten(self):
        return {
            "platform": self.platform,
            "location": self.location,
            "subscription": self.subscription,
            "resourceName": self.resourceName,
            "kubernetsVersion": self.kubernetsVersion,
            "vnetAddressPrefix": self.vnetAddressPrefix,
            "networkSecurityGroupName": self.networkSecurityGroupName,
            "vnetName": self.vnetName,
            "virtualMachineName": self.virtualMachineName,
            "virtualMachineSize": self.virtualMachineSize,
            "destinationPortRange": self.destinationPortRange,
            "isARMTemplate": self.isARMTemplate,
            "msname": self.services,
            "aks_uid": self.aks_uid
        }

class iotCare:
    def __init__(self, platform, location, subscription, isARMTemplate):
        self.platform = platform
        self.location = location
        self.subscription = subscription
        #self.resourceName = resourceName
        #self.kubernetsVersion = kubernetsVersion
        #self.vnetAddressPrefix = vnetAddressPrefix
        #self.networkSecurityGroupName = networkSecurityGroupName
        #self.vnetName = vnetName
        #self.virtualMachineName =virtualMachineName
        #self.virtualMachineSize =virtualMachineSize
        #self.destinationPortRange = destinationPortRange
        self.isARMTemplate = isARMTemplate
        #self.services = services
        #self.aks_uid = aks_uid
        
    def conten(self):
        return {
            "platform": self.platform,
            "location": self.location,
            "subscription": self.subscription,
            #"resourceName": self.resourceName,
            #"kubernetsVersion": self.kubernetsVersion,
            #"vnetAddressPrefix": self.vnetAddressPrefix,
            #"networkSecurityGroupName": self.networkSecurityGroupName,
            #"vnetName": self.vnetName,
            #"virtualMachineName": self.virtualMachineName,
            #"virtualMachineSize": self.virtualMachineSize,
            #"destinationPortRange": self.destinationPortRange,
            "isARMTemplate": self.isARMTemplate,
            #"msname": self.services,
            #"aks_uid": self.aks_uid
        }
        
#Class that represent the resource
class Resource:
    def __init__(self, uid, ref_id, deleted, platform, type, region):
        self.uid = uid
        self.ref_id = ref_id
        self.type = type
        self.platform = platform
        self.region = region
        self.deleted = deleted
        self.input_params = {}
        self.output_params = {}
        self.dependencies = []
        self.dynamic_params = {}
        
    def append_dependency(self, key):
        self.dependencies.append(key)
        
    def update_dynamic_params(self, name, value):
        self.dynamic_params.update({name: value})
    
    def update_input_params(self, value):
        self.input_params.update(value)
        
    def update_output_params(self, value):
        self.output_params.update(value)
        
    def content(self):
        return {
            "uid": self.uid,
            "ref_id": self.ref_id,
            "type": self.type,
            "platform": self.platform,
            "region": self.region,
            "deleted": self.deleted,
            "input_params": self.input_params,
            "output_params": self.output_params,
            "dependencies": self.dependencies,
            "dynamic_params": self.dynamic_params
        }
def random_pet(words=2, separator="-"):
    return petname.generate(words, separator)
def create_template_data (data, project, application, environment, cloudinfraname):
    ansible_input_data = {}
    ansible_input_elements = []
    service_input = ['metadata', 'security', 'restsql', 'notification', 'ui', 'remoteaccess', 'audit', 'patchmanagement', 'devicemanagement']
    service_selected = []
    templateName = jmespath.search("templateName", data)
    if len(templateName) > 0:
        if "iot-platform" in templateName:
            platform = jmespath.search("nodeDataArray[?resourcetype=='resource-group'].platform", data)
            location = jmespath.search("nodeDataArray[?resourcetype=='resource-group'].region", data)
            subscription = jmespath.search("nodeDataArray[?resourcetype=='resource-group'].subscription", data)
            resourceName = jmespath.search("nodeDataArray[?resourcetype=='%s'].name" % ("resource-group"), data)
            kubernetsVersion = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.kubernetsVersion", data)
            vnetAddressPrefix = jmespath.search("nodeDataArray[?resourcetype=='vnet'].input_properties.address_space", data)
            vnetName = jmespath.search("nodeDataArray[?resourcetype=='vnet'].input_properties.vnet_name", data)
            vnetSubnetPrefix = jmespath.search("nodeDataArray[?resourcetype=='azsubnet'].input_properties.subnet_prefix", data)
            networkSecurityGroupName = jmespath.search("nodeDataArray[?resourcetype=='network-security-group'].input_properties.security_group_name", data)
            virtualMachineName = jmespath.search("nodeDataArray[?resourcetype=='compute'].input_properties.vm_hostname", data)
            virtualMachineSize = jmespath.search("nodeDataArray[?resourcetype=='compute'].input_properties.vm_size", data)
            destinationPortRange = jmespath.search("nodeDataArray[?resourcetype=='network-security-group'].input_properties.destinationPortRange", data)
            aks_uid = jmespath.search("nodeDataArray[?resourcetype=='aks'].uid", data)
            all_services = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.care_services", data)
            if len(all_services) > 0:
                if all_services[0].lower() == "yes":
                    service_selected = services_input
            else:
                audit = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.audit", data)
                if len(audit) > 0:
                    if audit[0].lower() == "yes":
                        service_selected.append("audit")
                restsql = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.restsql", data)
                if len(restsql) > 0:
                    if restsql[0].lower() == "yes":
                        service_selected.append("restsql")
                notification = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.notification", data)
                if len(notification) > 0:
                    if notification[0].lower() == "yes":
                        service_selected.append("notification")
                ui = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.ui", data)
                if len(ui) > 0:
                    if ui[0].lower() == "yes":
                        service_selected.append("ui")
                remoteaccess = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.remoteaccess", data)
                if len(remoteaccess) > 0:
                    if remoteaccess[0].lower() == "yes":
                        service_selected.append("remoteaccess")
                patchmanagement = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.patchmanagement", data)
                if len(patchmanagement) > 0:
                    if patchmanagement[0].lower() == "yes":
                        service_selected.append("patchmanagement")
                devicemanagement = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.devicemanagement", data)
                if len(devicemanagement) > 0:
                    if devicemanagement[0].lower() == "yes":
                        service_selected.append("devicemanagement")
                security = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.security", data)
                if len(security) > 0:
                    if security[0].lower() == "yes":
                        service_selected.append("security")
                metadata = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.metadata", data)
                if len(metadata) > 0:
                    if metadata[0].lower() == "yes":
                        service_selected.append("metadata")
            
            print ( platform[0] )
            print ( location[0] )
            print ( subscription[0] )
            print ( resourceName[0] )
            print ( kubernetsVersion[0] )
            print (vnetAddressPrefix[0] )
            print ( vnetSubnetPrefix[0] )
            print ( networkSecurityGroupName[0] )
            print ( vnetName[0] )
            print ( virtualMachineName[0] )
            print ( virtualMachineSize[0] )
            print ( destinationPortRange[0] )
            print ( service_selected[0] )
            print ( aks_uid[0] )
            output_data = iotData (platform[0], location[0], subscription[0], resourceName[0], kubernetsVersion[0], vnetAddressPrefix[0], vnetSubnetPrefix[0], resourceName[0] + "-" + networkSecurityGroupName[0], resourceName[0] + "-" + vnetName[0], resourceName[0] + "-" + virtualMachineName[0], virtualMachineSize[0], destinationPortRange[0], TRUE, service_selected, aks_uid[0])
            
            ansible_input_elements.append(output_data.content())
            
            ansible_input_data["data"] = ansible_input_elements
        
        if "careawstest" in templateName:
            platform = jmespath.search("nodeDataArray[?resourcetype=='resource-group'].platform", data)
            region = jmespath.search("nodeDataArray[?resourcetype=='resource-group'].region", data)
            subscription = jmespath.search("nodeDataArray[?resourcetype=='resource-group'].subscription", data)
            #resourceName = jmespath.search("nodeDataArray[?resourcetype=='%s'].name" % ("resource-group"), data)
            #kubernetsVersion = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.kubernetsVersion", data)
            #vnetAddressPrefix = jmespath.search("nodeDataArray[?resourcetype=='vnet'].input_properties.address_space", data)
            #vnetName = jmespath.search("nodeDataArray[?resourcetype=='vnet'].input_properties.vnet_name", data)
            #vnetSubnetPrefix = jmespath.search("nodeDataArray[?resourcetype=='azsubnet'].input_properties.subnet_prefix", data)
            #networkSecurityGroupName = jmespath.search("nodeDataArray[?resourcetype=='network-security-group'].input_properties.security_group_name", data)
            #virtualMachineName = jmespath.search("nodeDataArray[?resourcetype=='compute'].input_properties.vm_hostname", data)
            #virtualMachineSize = jmespath.search("nodeDataArray[?resourcetype=='compute'].input_properties.vm_size", data)
            #destinationPortRange = jmespath.search("nodeDataArray[?resourcetype=='network-security-group'].input_properties.destinationPortRange", data)
            #aks_uid = jmespath.search("nodeDataArray[?resourcetype=='aks'].uid", data)
            #all_services = jmespath.search("nodeDataArray[?resourcetype=='aks'].input_properties.care_services", data)
            
            print ( platform[0] )
            print ( region[0] )
            print ( subscription[0] )
            output_data = iotCore(platform[0], region[0], subscription[0], TRUE)
            
            ansible_input_elements.append(output_data.content())
            
            ansible_input_data["data"] = ansible_input_elements
            
    with open('data_output.json', 'a') as f:
            f.truncate(0)
            f.write(json.dumps(ansible_input_data))
    print(ansible_input_data)
    
def convert_json_to_config(data, project, application, environment, cloudinfraname):
    keys = []
    deleted = []
    resources = []
    resources_list = []
    warnings = set()
    
    query = "nodeDataArray[].uid"
    uids = jmespath.search(query, data)
    dependencies_not_supported = ["region", "az", "subnet", "azsubnet"]
    supported_resource_type = ["ec2-instance", "elb", "security-group", "vpc", "sql-server", "s3-bucket", "autoscaling", "resource-group", "storage-account", "compute", "vnet", "network-sercurity-group", "eks", "aks", "route-table", "route", "vmss"]
    for uid in uids:
        keys = jmespath.search("nodeDataArray[?uid=='%d'].key" % uid,data)
        key = keys[0]
        deleted = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].isdeleted" % (key, uid), data)
        resource_type = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].resourcetype" % (key, uid), data)
        platform = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].platform" % (key, uid), data)
        region = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].region" % (key, uid), data)
        print (region)
        tags = { "project": project, "application": application, "environment": environment, "cloudinfraname": cloudinfraname }
        if len(deleted) > 0:
            if deleted[0]:
                warnings.add("component with ID %d is deleted on UI" % uid)
            r = Resource(uid, key, str(deleted[0]).lower(), platform[0], resource_type[0], region[0])
            print("Deleted Resource Flag")
            print(str(uid) + ":" + r.deleted)
        else:
            if resource_type[0] not in supported_resource_types:
                warnings.add("node type %s is not implemented yet" % uid)
                continue
            r = Resource(uid, key, "false", platform[0], resource_type[0], region[0])
        input_properties = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties" % (key, uid), data)
        if len(input_properties) > 0:
            name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.name" % (key, uid), data)
            ansible_role = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.ansible_role" % (key, uid), data)
            if len(ansible_role) > 0:
                tags.update({"ansible_role": ansible_role[0]})
            if len(name) <= 0:
                #update_name = project + "-" + application + "-" + name[0]
                #update_name = random_pet(words=3)
                #input_properties[0].pop('name')
                input_properties[0].update({"name": random_pet(words=3)})
                
            if "security-group" in resource_type:
                sg_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.name" % (key, uid), data)
                ingress_cidr_blocks_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.ingress_cidr_blocks" % (key, uid), data)
                ingress_rules_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.ingress_rules" % (key, uid), data)
                egress_cidr_blocks_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.egress_cidr_blocks" % (key, uid), data)
                egress_rules_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.egress_rules" % (key, uid), data)
                
                ingress_cidr_blocks = (re.sub("[\"]","", ingress_cidr_blocks_input[0]))[1:-1]
                ingress_rules = (re.sub("[\"]","", ingress_rules[0]))[1:-1]
                egress_cidr_blocks = (re.sub("[\"]","", egress_cidr_blocks[0]))[1:-1]
                egress_rules = (re.sub("[\"]","", egress_rules[0]))[1:-1]
                
                ingress_with_cidr_blocks_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.ingress_with_cidr_blocks" % (key, uid), data)
                
                r.update_input_params({"name": sg_name[0]})
                r.update_input_params({"tags": tags})
                if len(ingress_with_cidr_blocks_input) > 0:
                    ingress_with_cidr_blocks = (re.sub("[\"]", "", ingress_cidr_blocks_input[0]))
                    r.update_input_params({"ingress_cidr_blocks": ingress_cidr_blocks.split(","),"ingress_rules": ingress_rules.split(","), "egress_cidr_blocks": egress_cidr_blocks.split(","), "egress_rules": egress_rules.split(","), "ingress_with_cidr_blocks": ingress_with_cidr_blocks })
                else:
                    r.update_input_params({"ingress_cidr_blocks": ingress_cidr_blocks.split(","),"ingress_rules": ingress_rules.split(","), "egress_cidr_blocks": egress_cidr_blocks.split(","), "egress_rules": egress_rules.split(",") })
            elif "network-security-group" in resource_type:
                nsg_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.security_group_name" % (key, uid), data)
                custom_rules = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.custom_rules" % (key, uid), data)
                
                r.update_input_params({"security_group_name": nsg_name[0]})
                r.update_input_params({"tags": tags[0]})
                r.update_input_params({"resource_group_name": region[0]})
                r.update_input_params({"custom_rules": custom_rules[0]})
            elif "elb" in resource_type:
                internal = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.internal" % (key, uid), data)
                r.update_input_params({
                    "listener": [{
                        "instance_port": "80",
                        "instance_protocol": "http",
                        "lb_port": "80",
                        "lb_protocol": "http"
                    }],
                    "health_check": {
                        "target": "HTTP:80/",
                        "interval": 30,
                        "healthy_threshold": 2,
                        "unhealthy_threshold": 2,
                        "timeout": 5,
                    }
                })
                r.update_input_params({"tags": tags})
                r.update_input_params({"name": name[0], "internal": internal[0]})
            
            elif "autoscaling" in resource_type:
                r.update_input_params(input_properties[0])
                r.update_input_params({"tags_as_map": tags})
                r.update_input_params({"lt_name": name[0]})
                r.update_input_params({"create_lt": True})
                r.update_input_params({"use_lt": True})
                
            elif "vnet" in resource_type:
                virtual_network_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.vnet_name" % (key, uid), data)
                virtual_network_address_space_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.address_space" % (key, uid), data)
                if len(virtual_network_address_space_input) > 0:
                    virtual_network_address_space = (re.sub("[\"]","",virtual_network_address_space_input[0]))[1:-1]
                    r.update_input_params({"virtual_network_address_space": virtual_network_address_space.split(",")})
                resource_group_location = jmespath.search("nodeDataArray[?resourcetype=='vnet'].region", data)
                r.update_input_params({"virtual_network_name": virtual_network_name[0], "resource_group_location": resource_group_location[0]})
                r.update_input_params({"tags": tags})
                
            elif "resource-group" in resource_type:
                resource_group_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.rg_name" % (key, uid), data)
                resource_group_location = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.rg_location" % (key, uid), data)
                r.update_input_params({"resource_group_name": resource_group_name[0], "resource_group_location": resource_group_location[0]})
                r.update_input_params({"tags": tags})
            elif "storage-account" in resource_type:
                location = jmespath.search("nodeDataArray[?resourcetype=='storage-account'].region", data)
                sa_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.name" % (key, uid), data)
                account_tire = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.performance" % (key, uid), data)
                account_replication_type = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.redundancy" % (key, uid), data)
                min_tls_version = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.min_tls_version" % (key, uid), data)
                nfsv3_enabled = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.nfsv3_enabled" % (key, uid), data)
                sftp_enabled = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.sftp_enabled" % (key, uid), data)
                hns_enabled = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.hns_enabled" % (key, uid), data)
                container_access_type = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.container_access_type" % (key, uid), data)
                shared_access_key_enabled = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.shared_access_key_enabled" % (key, uid), data)
                access_tire = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.access_tire" % (key, uid), data)
                azurerm_storage_container_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.container_name" % (key, uid), data)
                r.update_input_params({"location": location[0], "sa_name": sa_name[0], "account_tire": account_tire[0], "account_replication_type": account_replication_type[0], "min_tls_version": min_tls_version[0], "nfsv3_enabled": nfsv3_enabled[0], "sftp_enabled": sftp_enabled[0], "hns_enabled": hns_enabled[0], "container_access_type": container_access_type[0], "shared_access_key_enabled": shared_access_key_enabled[0], "access_tire": access_tire[0], "azurerm_storage_container_name": azurerm_storage_container_name[0]})
                r.update_input_params({"tags": tags})
            elif "az-subnet" in resource_type:
                subnet_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.subnet_name" % (key, uid), data)
                subnet_prefix_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.subnet_prefix" % (key, uid), data)
                if len(subnet_prefix_input) > 0:
                    subnet_prefix = (re.sub("[\"]","", subnet_prefix_input[0]))[1:-1]
                    r.update_input_params({"subnet_prefix": subnet_prefix.split(",")})
                service_endpoints_input = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.service_endpoints" % (key, uid), data)
                if len(service_endpoints_input) > 0:
                    service_endpoints = (re.sub("[\"]","", service_endpoints[0]))[1:-1]
                    r.update_input_params({"service_endpoints": service_endpoints.split(",")})
                r.update_input_params({"subnet_name": subnet_name[0]})
                r.update_input_params({"tags": tags})
            elif "vmss" in resource_type:
                vmscaleset_name = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.vmscaleset_name" % (key, uid), data)
                os_flavor = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.os_flavor" % (key, uid), data)
                source_image_id = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].input_properties.source_image_id" % (key, uid), data)
                r.update_input_params({"vmscaleset_name": vmscaleset_name[0], "os_flavor": os_flavor[0], "source_image_id": source_image_id[0]})
                r.update_input_params({"tags": tags})
            else:
                r.update_input_params(input_properties[0])
                r.update_input_params({"tags": tags})
        output_properties = jmespath.search("nodeDataArray[?key=='%d' && uid=='%d'].output_properties.vmscaleset_name" % (key, uid), data)
        if len(output_properties) > 0:
            r.update_output_params(output_properties[0])
        dependencies = []
        key_other = key
        to_s = jmespath.search("linkDataArray[?from=='%d'].to" % key_other, data)
        is_sg_link = False
        for m in to_s:
            linked_resource_type = jmespath.search("nodeDataArray[?key=='%d'].resourcetype" % m,data)
            sg_link = jmespath.search("nodeDataArray[?key=='%d'].resourcetype" % key_other,data)
            if len(sg_link) > 0:
                if "security-group" in sg_link:
                    is_sg_link = True
            m_uid = jmespath.search("nodeDataArray[?key=='%d'].uid" % m,data)
            if len(linked_resource_type) > 0:
                if ( "ec2" in linked_resource_type[0] and not is_sg_link ) or "subnet" in linked_resource_type[0] or "azsubnet" in linked_resource_type[0] or "autoscaling" in linked_resource_type[0] or "route-table" in linked_resource_type[0] or "az-subnet" in linked_resource_type[0] or "network-security-group" in linked_resource_type[0]:
                    dependencies.append("-" + str(m_uid[0]))
        from_s = jmespath.search("linkDataArray[?from=='%d'].from" % key_other, data)
        for p in form_s:
            linked_resource_type = jmespath.search("nodeDataArray[?key=='%d'].resourcetype" % p,data)
            p_uid = jmespath.search("nodeDataArray[?key=='%d'].uid" % p,data)
            if len(linked_resource_type) > 0:
                if "security-group" in linked_resource_type[0] or "ec2-instance" in linked_resource_type[0] or "event-hub-namespace" in linked_resource_type[0] or "private-dns-zone" in linked_resource_type[0] or "recovery-services-vault" in linked_resource_type[0] or "resource-group" in linked_resource_type[0] or "public-ip" in linked_resource_type[0]:
                    dependencies.append("-" + str(p_uid[0]))
                    
        i = 0
        uid_other = uid
        group = jmespath.search("nodeDataArray[?key=='%d'].group" % uid_other,data)
        while len(group) > 0:
            group_uid = jmespath.search("nodeDataArray[?key=='%s'].uid" % group[0],data)
            group_resource_type = jmespath.search("nodeDataArray[?key=='%s'].resourcetype" % group_uid[0],data)
            if not dependencies_not_supported(group_resource_type, dependencies_not_supported):
                dependencies.append("-" + str(group_uid[0]))
            uid_other = group_uid[0]
            group = jmespath.search("nodeDataArray[?uid=='%d'].group" % uid_other,data)
            if len(group) > 0:
                break
            
        for k in dependencies:
            dep_resource_type = jmespath.search("nodeDataArray[?uid=='%s'].resourcetype" % k.replace("-",""),data)
            r.append_dependency(dep_resource_type[0] + str(k))
            
        resources.append(r.content())
        resources_list.append(r)
        i = i + 1
        
        
        for r in resources_list:
            generate_dynamic_params(data, r)
    logging.info(pformat(resources))
    
    if len(warnings):
        logging.warning("; ".join(warnings))
        
    return json.dumps(resources)

def dependencies_in_not_supported(resource_type, dependencies_not_supported):
    item = 0
    while item <= len(dependencies_not_supported):
        if dependencies_not_supported[item] in resource_type:
            return True
        break
    item = item + 1
                
            
            
                
            
            
            
            
                    
