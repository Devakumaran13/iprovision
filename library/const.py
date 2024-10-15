#!/usr/bin/env python3
import os
import tempfile

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

COOKIECUTTER_TEMPLATES_DIR = os.path.join(BASE_PATH, "../templates")

OUTPUT_DIR = "output"
WORK_DIR = "work"
WORK_DIR_FOR_COOKIECUTTER = "{{ cookiecutter.dir_name }}"

FINAL_DIR = "final"

if os.environ.get("IS_LOCAL"):
    tmp_dir = os.getcwd()
elif os.environ.get("WORKSPACE"):
    tmp_dir = os.environ.get("WORKSPACE")
else:
    tmp_dir = tempfile.gettempdir()

print("temp dir:" + tmp_dir)