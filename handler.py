#!/usr/bin/env python3

import json
import os
import shutil
import jmespath
import sys
from pprint import pformat, pprint
from os import path

import requests
from library.const import FINAL_DIR, tmp_dir
from library.convert import convert_json_to_config, create_template_data
from library.logger import setup_logging
from library.render import prepare_render_dirs, render_from_json_config, mkdir_safely


class Data:
    def __init__(self, platform, region, subscription):
        self.platform = platform
        self.region = region
        self.subscription = subscription
        
    def content(self):
        return {
            "platform": self.platform,
            "region": self.region,
            "subscription": self.subscription            
        }
        
def validation_result(config):
    return True


def handler():
    ansible_input_elements = []
    with open(sys.argv[1]) as f:
        json_data = json.load(f)
    config = convert_json_to_config(json_data, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    prepare_render_dirs()
    platforms = jmespath.search("nodeDataArray[].platform", json_data)
    platforms = list(set(platforms))
    for platform in platforms:
        regions = jmespath.search("nodeDataArray[?paltform=='%s'].region" % platform, json_data)
        regions = list(set(regions))
        for region in regions:
            subscriptions = jmespath.search("nodeDataArray[?region=='%s' && platform=='%s'].subscription" % (region, platform), json_data)
            subscriptions = list(set(subscriptions))
            output_data = Data(platform,region,subscriptions[0])
            resources_list = json.loads(config)
            resources = [x for x in resources_list if (x['platform'] == platform and x['region'] == region)]
            source_dir = sys.argv[2] + "/" + sys.argv[3] + "/" + sys.argv[4] + "/" + sys.argv[5]
            render_from_json_config(resources, source_dir, platform, region)
            ansible_input_elements.append(output_data.content())
        
    ansible_roles = jmespath.search("nodeDataArray[].input_properties.ansible_role", json_data)
    ansible_roles = list(set(ansible_roles))
    
    ansible_roles_data = {}
    ansible_roles_data["roles"] = ansible_roles
    print(ansible_roles_data)
    
    aws_regions = jmespath.search("nodeDataArray[?paltform=='aws'].region", json_data)
    aws_regions = list(set(aws_regions))
    
    aws_regions_data = {}
    aws_regions_data["regions"] = aws_regions
    print(aws_regions_data)
    
    temp_dir = "archive_work_dir/"
    archive_dir = tmp_dir + "/output/work/" + FINAL_DIR + "/" + sys.argv[2] + "/" + sys.argv[3] + "/" + sys.argv[4] + "/" + sys.argv[5] + "/"
    mkdir_safely(temp_dir)
    shutil.copytree(archive_dir, temp_dir, ignore= shutil.ignore_patterns(".terra*"), dirs_exist_ok=True)
    
    if not os.environ.get("IS_LOCAL"):
        if os.path.isfile("archive.zip"):
            os.remove("archive.zip")
        shutil.make_archive("archive", "zip", archive_dir)
        
    ansible_input_data = {}
    ansible_input_data["data"] = ansible_input_elements
    print(ansible_input_data)
    
    with open('data_output.json', 'a') as f:
        f.truncate(0)
        f.write(json.dumps(ansible_input_data))
    with open('ansible_roles.json', 'a') as f:
        f.truncate(0)
        f.write(json.dumps(ansible_roles_data))
    with open('aws_regions.json', 'a') as f:
        f.truncate(0)
        f.write(json.dumps(aws_regions_data))
    isARMTemplate = jmespath.search("isARMTemplate", json_data)
    if isARMTemplate:
        config = create_template_data(json_data, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        
logger = setup_logging()
handler()