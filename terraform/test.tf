# Define required providers
terraform {
required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

# Configure the OpenStack Provider

provider "openstack" {
  domain_name = "default"
  user_name   = "pfisterer-cloud-lecture"
  tenant_name = "admin"
  password    = "ss2025"
  auth_url    = "https://stack.dhbw.cloud:5000"
  region      = "RegionOne"
  tenant_id = "d11c8af5f24f4756a6d51b880162f71f"
}

# Create a web server
resource "openstack_compute_instance_v2" "test-server" {
    name = "artur-test"
    image_name = "Ubuntu 24.04 2025-01"
    flavor_name = "cb1.medium"
    key_pair = "ssh Artur"
    security_groups = ["default"]
    
    network {
        name = "provider_912"
    }
}


