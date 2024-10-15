locals {
    workspace = path_relative_to_include()
    source = replace("{{ this.source_name }}", "/", "-")
}

terraform {
    extra_arguments "disable_input" {
        commands = get_terraform_commands_that_need_input()
        arguments = ["-input=false"]
    }
    before_hook "create_ns" {
        commands = ["init"]
        execute = ["sh", "-c", "kubectl create ns ${local.source} > /dev/null 2>&1 || true"]
    }
    before_hook "workspace" {
        commands = ["plan", "state", "apply", "destroy", "refresh"]
        execute = ["sh", "-c", "tofu workspace select ${local.workspace} || tofu workspace new ${local.workspace}"]

    }
}

remote_state {
    backend = "pg"
    disable_dependency_optimization = true
    config = {
        conn_str = "postgres://postgress:tfbackend123@postgres-pgpool.rapid-platform.svc.cluster.local:5432/terraform_backend?sslmode=disable"
        schema_name = format("%s", "{{ this.source_name }}")

    }
    generate = {
        path = "_backend.tf"
        if_exists = "overwrite"
    }
}

generate "main_providers" {
    path = "main_providers.tf"
    if_exists = "overwrite"
    contents = <<EOF
    {% if "aws" in this.platform -%}
    provider "aws" {
        region = "{{ this.region }}"
        skip_metadata_api_check = true
        skip_region_validation = true
        skip_credentials_validation = true
    }
    {% elif "azure" in this.platform -%}
    provider "azurerm" {
        version = "3.116.0"
        features {}
    }
    {%- endif %}
    EOF
}