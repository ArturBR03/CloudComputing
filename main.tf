terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {
  auth_url    = "https://stack.dhbw.cloud:5000/v3"
  domain_name = "default"
  user_name   = "pfisterer-cloud-lecture"
  tenant_id   = "admin"      # Replace with actual tenant ID
  password    = "ss2025" # Replace with actual password
}

resource "openstack_compute_instance_v2" "ar-instance" {
  name            = "ar-instance"
  image_name      = "Ubuntu 24.04 2025-01" # Immutable core attribute
  flavor_name     = "cb1.medium"
  key_pair        = "ARCC"                  # Pre-uploaded SSH key
  security_groups = ["default"]           # Firewall rules

  network {
    name = "provider_912"                 # Public network
  }
}
