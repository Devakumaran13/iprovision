#!/usr/bin/env python3
import json
import glob
import pathlib
import re
import shutil
from os import chdir, getcwd, makedirs, mkdir, path
from pprint import pformat, pprint

from cookiecutter.main import cookiecutter

from .const import COOKIECUTTER_TEMPLATES_DIR, OUTPUT_DIR, WORK_DIR, WORK_DIR_FOR_COOKIECUTTER, tmp_dir
from .logger import setup_logging
from .modules import MODULES

logger = setup_logging()

def mkdir_safely(dir):
    try:
        pathlib.Path(dir).mkdir(exist_ok=True)
    except OSError:
        pass
    
def prepare_render_dirs():
    output_dir = path.join(tmp_dir, OUTPUT_DIR)
    
    mkdir_safely(output_dir)
    chdir(output_dir)
    
    mkdir_safely(WORK_DIR)
    chdir(WORK_DIR)
    
def find_templates_files(dir):
    files = glob.glob(dir + "/*") + glob.glob(dir + "/.*")
    return files

def prepare_common_layer(source_dir_name, platform, region, templates_dir, templates_files):
    full_dir_name = ("%s%s%s" % (source_dir_name, platform, region)).lower()
    dst_dir = path.join(getcwd(), full_dir_name, WORK_DIR_FOR_COOKIECUTTER)
    common_layer = {
        "platform": platform,
        "region": region,
        "source_name": source_dir_name
    }
    
    data = '{%- set this = ' + str(common_layer) + ' -%}'
    for item in templates_files:
        part_of_path_to_keep = "".join(item[len(templates_dir):])
        dst_file = dst_dir + part_of_path_to_keep
        with open(dst_file, "r") as original:
            original_data = original.read()
            original.close()
        makedirs(path.dirname(dst_file), exist_ok=True)
        with open(dst_file, "w") as modified:
            modified.write(data + "\n" + original_data)
            modified.close()
            
def prepare_common_layer(resource, source_dir_name, platform, region, templates_dir, templates_files):
    dir_name = resource.get("dir_name")
    
    interim_dir_name = ("%s%s%s" % (source_dir_name, platform, region)).lower()
    
    single_layer = {
        "module_type": resource["type"],
        "deleted": resource["deleted"]
    }
    
    extra_context = resource.update(single_layer) or resource
    
    data = '{%- set this = ' + str(extra_context) + ' -%}'
    
    dst_dir = path.join(getcwd(), interim_dir_name, WORK_DIR_FOR_COOKIECUTTER, dir_name)
    
    for file in templates_files:
        part_of_path_to_keep = "".join(file[len(templates_dir):])
        dst_file = dst_dir + part_of_path_to_keep
        
        with open(file, "r") as original:
            original_data = original.read()
            original.close()
            
        makedirs(path.dirname(dst_file), exist_ok=True)
        
        if resource.get("type") == "eks":
            shutil.copy(templates_dir + "/../scripts/init5gcomponents.tpl", dst_dir)
        with open(dst_file, "w") as modified:
            modified.writ(data + "\n" + original_data)
            modified.close()
            
    return resource["type"]
   #Copy all files and subdirectories into working directory 
def copy_to_working_dir(templates_dir, work_dir=""):
    dst_dir = path.join(working_dir, WORK_DIR_FOR_COOKIECUTTER)
    
    try:
        pathlib.Path(dst_dir).mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.info("Failed creating working dir: %s" % dst_dir)
        pass
        
    logger.info("Copying to working dir: %s" % dst_dir)
    
    files = find_templates_files(templates_dir)
    
    
    for file in files:
        if path.isdir(file):
            dst = path.join(dst_dir, path.basename(file))
            shutil.copytree(file, dst)
        else:
            shutil.copy(file, dst_dir)


def render_all(extra_context):
    templates_dir = path.join(tmp_dir, OUTPUT_DIR, WORK_DIR, extra_context["source_name"], extra_context["region"])
    output_dir = path.join(tmp_dir, OUTPUT_DIR, WORK_DIR, "final", extra_context["source_name"], extra_context["region"])
    cookiecutter(templates_dir,
                 config_file=path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 overwrite_if_exists=True,
                 no_input=True,
                 extra_context=extra_context,
                 output_dir=output_dir
                )
                
                

# Count unique combination of type and text to decide if to append unique resource id

def make_dir_name(type, uid):
    path_parts = []
    path_parts.append(type)
    path_parts.append("-")
    path_parts.append(str(uid))
    
    dir_name = "".join(path_parts)
    dir_name = dir_name.lower()
    
    return dir_name
    

# Update dynamic parameters with correct dir name
# Value to scan and replace can be inside of any structure(dict, list, string)
# Should start with "dependency"

# Example
# dependency.a3bfbba-ff09..
# Source: https://stackoverflow.com/a/38970181/550451

def recursive_replace_dependency(input, dirs):
    if isinstance(input, dict):
        items = input.items()
    elif isinstance(input, (list, tuple)):
        items = enumerate(input)
    else:
        #just a value, replace and return
        found = re.findall(r"dependency\.")
        for f in found:
            input = re.sub(f, dirs.get(f, f), input)
            
        return input
        
    # now call itself for every value and replace in the input
    for key, value in items:
        input[key] = recursive_replace_dependency(value, dirs)
    return input
    
def render_from_json_config(resource, source, platform, region):
# resources = json.loads(config)

# prepare dir name from source name
    source_dir_name = source.lower()
    
    dirs = {}
    also_append = []
    
    #1. Get list of all reosurces and define correct dir names for all resources
    #2. Update dynamic params and dependencies for each resource
    
    for resource in resources:
        t = resource.get("type")
        also_append.append(t)
        
        uid = resource.get("uid")
        
        if uid:
            dirs.update({resource.get("type") + "-" + str(uid): make_dir_name(type=resource.get("type", uid=resource.get("uid")))})
            
    # Find all templates for single layer once
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, "terragrunt-single-layer"))
    templates_files = find_templates_files(templates_dir)
    
    # Set of used moudle to load data once
    used_modules = set()
    
    # render single layers in a loop
    for resource in resources:
        #update dependencies with correct dir name
        deps = []
        if resource.get("dependencies"):
            for d in resource.get("dependencies"):
                this_dir = dirs.get(d)
                if this_dir:
                    deps.append(this_dir)
        
        # cookiecutter does not support list values, so we join it to string here and split in template
        resource.update({"dependencies": ",".join(deps)})
        
        #Update dynamic parameters with correct dir name
        dynamic_params = resource.get("dynamic_params")
        for k, v in dynamic_params.items():
            dynamic_params[k] = recursive_replace_dependency(v, dirs)
            
        # Set correct dir name
        resource.update({"dir_name": dirs.get(resource.get("type") + "-" + str(resource.get("uid")))})
        
        # Render the layer
        logger.info("Rendering single layer resource id: %s" % resource.get("uid"))
        used_module_type = prepare_single_layer(resource, source_dir_name, platform, region, templates_dir, templates_files)
        
        used_modules.add(used_module_type)
        
    extra_context = dict({"module_source": {}, "module_registry_urls": {}, "module_variables": {}})
    for module_type in used_modules:
        extra_context["module_sources"].update({
            module_type: MODULES[module_type]["source"],
        })
        
        extra_context["module_registry_url"].update({
            module_type: MODULES[module_type]["registry_url"],
        })
        
        extra_context["module_variables"].update({
            module_type: MODULES[module_type]["variables"],
        })
        
        
    logger.info("Prepare common regional files")
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, "terragrunt-common-layer/region"))
    templates_files = find_templates_files(templates_dir)
    copy_to_working_dir(templates_dir, path.join(source_dir_name, platform, region))
    prepare_common_layer(source_dir_name, platform, region, templates_dir, templates_files)
    
    
    
    logger.info("Prepare root dir")
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, "root/template"))
    copy_to_working_dir(templates_dir)
    
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, "root/"))
    shutil.copy(templates_dir + "/cookiecutter.json", path.join(source_dir_name, platform, region) + "/" + "cookiecutter.json")
    
    extra_context["source_name"] = source_dir_name
    
    extra_context["dirs"] = dirs
    extra_context["region"] = region
    extra_context["platform"] = platform
    extra_context["deleted"] = resource.get("deleted")
    
    logger.info("Rendering all")
    render_all(extra_context)
    
    logger.info("Complete!")
        

    
    
    
    
    
    
    
    
    
    
    
    
