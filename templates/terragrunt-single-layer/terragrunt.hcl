{%- set module_source = cookiecutter.module_sources[this.module_type] -%}
{%- set module_variables = cookiecutter.module_variables[this.module_type] -%}
{%- set module_registry_url = cookiecutter.module_registry_urls[this.module_type] -%}

locals {
    deleted = {{ this.deleted }}
}
terraform {
    source = "{{ module_source }}"
}

include {
    path = find_in_parent_folders()
}

{% if this.dependencies|default("") -%}
dependencies {
    paths = [
        {%- for value in this.dependencies.split(",") -%}
        "../{{ value }}"{%- if not loop.last -%}, {% endif -%}
        {%- endfor -%}
    ]
}

{% for value in this.dependencies.split(",") -%}
dependency "{{ value }}" {
    config_path = "../{{ value }}"
    mock_outputs = {
        {% if this.module_type == "ebs" %}
            {%- if value.startswith("ec2-instance") -%}
            id = ["id-dummy"]
            {%- elif value.startswith("vpc") -%}
            public_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            private_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            {%- endif -%}
        {% elif this.module_type == "ec2-instance" %}
            {%- if value.startswith("security-group") -%}
            security_group_id = "sg-dummy"
            {%- elif value.startswith("vpc") -%}
            public_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            private_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            {%- endif -%}
        {% elif this.module_type == "security-group" %}
            {%- if value.startswith("vpc") -%}
            vpc_id = "vpc-dummy"
            {%- endif -%}
        {% elif this.module_type == "eks" %}
            {%- if value.startswith("vpc") -%}
            vpc_id = "vpc-dummy"
            public_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            private_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            {%- endif -%}
        {% elif this.module_type == "autoscaling" %}
            {%- if value.startswith("vpc") -%}
            public_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            private_subnets = ["private-subnet-1-dummy","private-subnet-2-dummy","private-subnet-3-dummy"]
            {%- elif value.startswith("security-group") -%}
            security_group_id = "sg-dummy"
            {%- endif -%}
        {% elif this.module_type == "s3" %}
            region = us-east-1
        {% elif this.module_type == "lambda" %}
            region = us-east-1
        {% elif this.module_type == "dynamodb" %}
            region = us-east-1
        {% elif this.module_type == "efs" %}
            region = us-east-1
        {% elif this.module_type == "sns" %}
            region = us-east-1
        {% elif this.module_type == "vnet" %}
            {%- if value.startswith("network-security-group") -%}
                network-security-group_id = "/subscriptions/dummy/resourceGroups/dummy/providers/Microsoft.Network/networkSecurityGroups/nsg_dummy"
            {%- elif value.startwith("resource-group") -%}
                resource_group_name = "dummy"
            {%- endif -%}
        {% elif this.module_type == "az-subnet" %}
            {%- if value.startwith("resource-group") -%}
                resource_group_name = "dummy"
            {%- elif value.startswith("vnet") -%}
                virtual_network_name = "vnet-dummy"
            {%- elif value.startswith("network-security-group") -%}
                network-security-group_id = "/subscriptions/dummy/resourceGroups/dummy/providers/Microsoft.Network/networkSecurityGroups/nsg_dummy"
            {%- elif value.startswith("route-table") -%}
                route_table_id = "/subscriptions/dummy/resourceGroups/dummy/providers/Microsoft.Network/routeTables/route_dummy"
            {%- endif -%}
        {% elif this.module_type == "storage-accout" %}
            {%- if value.startwith("resource-group") -%}
                resource_group_name = "dummy" 
            {%- endif -%}
        {% elif this.module_type == "vmss" %}
            {%- if value.startwith("resource-group") -%}
                resource_group_name = "dummy"
            {%- elif value.startswith("az-subnet") -%}
                virtual_network_name = "vnet-dummy"
                name = "dummy"
            {%- endif -%}
        {% endif %}

    }
    mock_outputs_allowed_terraform_commands = ["init","plan"]
}

{% endfor %}
{%- endif -%}

{%- if module_registry_url -%}
###################################################################
# View all available inputs for this module:
#{{ module_registry_url }}?tab=inputs
###################################################################
{%- endif %}
inputs = {
    {% if this.module_type == "ec2-instance" %}
    count = local.deleted ? false : true
    {% elif this.module_type == "ecs" %}
    create = local.deleted ? false : true
    {% elif this.module_type == "security-group" %}
    create = local.deleted ? false : true
    {% elif this.module_type == "vpc" %}
    create_vpc = local.deleted ? false : true
    {% elif this.module_type == "s3-bucket" %}
    create_bucket = local.deleted ? false : true
    {% elif this.module_type == "autoscaling" %}
    create_asg = local.deleted ? false : true
    {% elif this.module_type == "elb" %}
    create_elb = local.deleted ? false : true
    {% elif this.module_type == "compute" %}
    nb_instances = local.deleted ? 0 : 1
    {% elif this.module_type == "eks" %}
    create = local.deleted ? 0 : 1
    {% endif %}

    {% for key, value in module_variables|dictsort -%}
    {%- if key in this.input_params -%}
    {%- set tmp_value = this.input_params[key] -%}
    {%- else -%}
    {%- set tmp_value = None -%}
    {%- endif -%}

    {# printing only required variables (required = no default value) and those which were set explicity #}
    {%- if value.default is not defined or tmp_value != None -%}
    {%- if tmp_value == None -%}
    {%- set this_value = value.default|default(value.variable_default) -%}
    {%- else -%}
    {%- set this_value = tmp_value -%}
    {%- endif -%}

    {#- Convert boolean values from Python (False, True) into HCL (false, true) -#}
    {%- if value.variable_value_format_function == "lower" -%}
    {%- set value_formatted = value.variable_value_format|format(this_value)|lower -%}
    {%- else -%}

    {%- if value.default is not string and (value.value_type.startswith("list") or value.value_type.startswith("map")) -%}
    {#- tojson is user to convert single quotes (Python) to double quotes (as in Deva) -#}
    {%- set value_formatted = this_value|tojson -%}
    {%- else -%}
    {%- set value_formatted = value.variable_value_format|format(this_value) -%}
    {%- endif -%}

    {#- Native HCL expression - Remove prefix "HCL:" and unquote after tojson -#}
    {%- if value_formatted.startswith("\"HCL:") -%}
    {%- set value_formatted = value_formatted[5:-1]|replace("\\\"", "\"") -%}
    {%- endif -%}

    {%- endif -%}

    {#- Override value with the dynamic dependency -#}
    {%- if key in this.dynamic_params -%}
    {%- set value_formatted = this.dynamic_params[key] -%}
    {%- endif %}

    {{ key }} = {{ value_formatted }}
    {% endif -%}

    {%- endfor %}

}
