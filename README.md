# Immutable Infrastructure Deployment with Terraform on OpenStack

## Introduction
This project implements the principles of **Immutable Infrastructure** using Terraform on OpenStack. Immutable Infrastructure ensures that deployed components are never modified after deployment. Instead, updates are handled by replacing entire components with new, versioned instances. This approach enhances security by preventing configuration drift, improves consistency through versioned artifacts, and simplifies rollbacks by maintaining previous deployable states.

## Technology Choice: Terraform
### Justification
Terraform was selected as the infrastructure-as-code (IaC) tool for this implementation due to its core alignment with immutable infrastructure principles:

1. **Declarative Model**  
   Terraform configurations define the desired end-state of infrastructure, enabling automatic reconciliation of changes without procedural scripts. This eliminates manual intervention and ensures consistent environments.

2. **Resource Replacement Enforcement**  
   Terraform automatically destroys and recreates resources when core attributes (e.g., VM image, flavor) are modified. This native behavior enforces immutability by design.

3. **State Management**  
   The `terraform.tfstate` file tracks resource dependencies and attributes, providing precise control over updates and rollbacks while maintaining a versioned history of infrastructure changes.

4. **OpenStack Integration**  
   Native support through the official `openstack` provider enables seamless interaction with OpenStack APIs for compute, network, and storage resources.

5. **Idempotency Guarantee**  
   Operations produce identical results regardless of execution frequency, which is critical for maintaining consistent immutable deployments.

## Immutable Component Design
### Component: Stateless Web Server (`rk-demo-bigdata`)
#### Immutability Strategy
- **Versioned Golden Images**  
  The VM boots exclusively from versioned OS images (`Ubuntu 24.04 2025-01`) stored in OpenStack Glance. Application updates require building new images (e.g., using Packer), not runtime modifications.

- **Disposable Infrastructure**  
  Changes to core attributes (image, flavor, network) trigger automatic resource replacement. The lifecycle follows:  
  `Create → Verify → Destroy` instead of in-place updates.

- **No Runtime Modifications**  
  SSH access for ad-hoc changes is architecturally discouraged. All configurations must be baked into new images or managed through declarative orchestration.

- **Ephemeral Storage**  
  VMs use transient storage with no local persistence. Stateful data is stored externally in OpenStack Volumes or object storage.

## Implementation Workflow
### Prerequisites
#### OpenStack Credentials
```hcl
auth_url    = "https://stack.dhbw.cloud:5000/v3"
domain_name = "default"
user_name   = "pfisterer-cloud-lecture"
tenant_id   = "Your_Tenant_ID"       # Replace with actual tenant ID
password    = "Your_Cloud_Password"  # Replace with actual password

Key pair which is uploaded to OpenStack (In this Project is it RK)

Terraform v1.0+: Installed on the provisioning machine

### Screencast folgt
