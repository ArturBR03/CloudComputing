terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}


provider "openstack" {
  auth_url    = "https://stack.dhbw.cloud:5000/v3"
  domain_name ="default"
  user_name   ="pfisterer-cloud-lecture"
  tenant_id ="d11c8af5f24f4756a6d51b880162f71f"
  password    ="ss2025"
}


resource "openstack_compute_instance_v2" "web_server_rk" {
    name = "rk-demo-bigdata"
    image_name = "Ubuntu 24.04 2025-01"
    flavor_name = "cb1.medium"
    key_pair = "BIP-Key"
    security_groups = ["default"]

  network {
    name = "provider_912"
  }
}

resource "local_file" "floating_ip" {
  content  = openstack_compute_instance_v2.web_server_rk.network.0.fixed_ip_v4
  filename = "${path.module}/openstack-inventory.txt"
}