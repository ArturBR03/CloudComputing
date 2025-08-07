# terraform/main.tf

terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "openstack" {
  auth_url     = "https://stack.dhbw.cloud:5000/v3"
  domain_name  = "default"
  user_name    = "pfisterer-cloud-lecture"
  tenant_id    = "d11c8af5f24f4756a6d51b880162f71f"
  password     = "ss2025"
}

resource "openstack_compute_instance_v2" "k3s_master" {
  name            = "k3s-master"
  flavor_name     = "cb1.medium"
  image_name      = "Ubuntu 24.04 2025-01"
  key_pair        = "RK"
  security_groups = ["default"]

  network {
    name = "provider_912"
  }

  provisioner "remote-exec" {
    inline = [
      "curl -sfL https://get.k3s.io | K3S_TOKEN=mysecret sh -s - server --cluster-init"
    ]
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_ed25519")
      host        = self.access_ip_v4
    }
  }
}

resource "openstack_compute_instance_v2" "k3s_worker" {
  count           = 1
  name            = "k3s-worker-${count.index}"
  flavor_name     = "cb1.medium"
  image_name      = "Ubuntu 24.04 2025-01"
  key_pair        = "RK"
  security_groups = ["default"]

  network {
    name = "provider_912"
  }

  provisioner "remote-exec" {
    inline = [
      "curl -sfL https://get.k3s.io | K3S_URL=https://${openstack_compute_instance_v2.k3s_master.access_ip_v4}:6443 K3S_TOKEN=mysecret sh -"
    ]
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_ed25519")
      host        = self.access_ip_v4
    }
  }
}

resource "null_resource" "fetch_kubeconfig" {
  depends_on = [openstack_compute_instance_v2.k3s_master]

  provisioner "local-exec" {
    command = <<EOT
    ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 ubuntu@${openstack_compute_instance_v2.k3s_master.access_ip_v4} "sudo cat /etc/rancher/k3s/k3s.yaml" > k3s.yaml
    sed -i "s/127.0.0.1/${openstack_compute_instance_v2.k3s_master.access_ip_v4}/g" k3s.yaml
    EOT
  }
}

provider "kubernetes" {
  config_path = "${path.module}/k3s.yaml"
}

output "application_url" {
  value = "http://${openstack_compute_instance_v2.k3s_master.access_ip_v4}:30080"
}

output "master_ip" {
  value = openstack_compute_instance_v2.k3s_master.network.0.fixed_ip_v4
}

output "kubeconfig" {
  value = "${path.module}/k3s.yaml"
}