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
1. **Install Terraform and adding Terraform in your System PATH**
**Installing Terraform**
Terraform v1.0+: Installed on the provisioning machine
Download Terraform on: https://developer.hashicorp.com/terraform/install

**Adding terraform.exe to Windows System PATH**

1. Download the Terraform `.zip` for Windows from the link above.
2. Extract `terraform.exe` to a folder of your choice, e.g., `C:\terraform`
3. Add this folder to your system's PATH:
   - Press `Win + S`, type `Environment Variables`, and select **Edit the system environment variables**.
   - In the System Properties window, click on the **Environment Variables** button.
   - In the "System variables" section, scroll to find the variable named `Path` and select it.
   - Click **Edit**, then click **New**, and enter the path where `terraform.exe` is located (e.g., `C:\terraform`).
   - Click **OK** on all windows to apply the changes.
4. Open a new terminal or PowerShell and run `terraform -version` to verify that it works from any folder.


2. **Upload your public Key on Openstack**
Generate a key on terminal with:
```hcl
ssh-keygen -t ed25519 -C "your_email@example.com"
```
Save the key and upload on Openstack
   
3. **Copy the Code and replace following Indicators**
```hcl
auth_url    = "https://stack.dhbw.cloud:5000/v3"
domain_name = "default"
user_name   = "pfisterer-cloud-lecture"
tenant_id   = "Your_Tenant_ID"       # Replace with actual tenant ID
password    = "Your_Cloud_Password"  # Replace with actual password
Key_pair    = "RK"                   # The Key pair which uploaded to OpenStack (In this Project is it RK)
```
### Terraform Deployment Steps

1. ### Initialize Terraform
   Run `terraform init` to initialize the working directory containing the Terraform configuration files.  
   This step downloads the necessary provider plugins and sets up the backend for state management.

2. ### Review the Execution Plan
   Execute `terraform plan` to create an execution plan.  
   This command shows what actions Terraform will perform to achieve the desired infrastructure state without making any changes.

3. ### Apply the Changes
   Use `terraform apply` to apply the changes required to reach the desired state of the configuration.  
   Terraform will prompt for confirmation before making any changes unless you pass the `-auto-approve` flag.

4. ### Verify the Deployment
   After applying, verify that the infrastructure has been provisioned correctly.  
   You can use Terraform output commands or check your cloud provider's console.

5. ### Manage State
   Terraform maintains the state of your infrastructure in a state file.

6. ### Destroy Infrastructure (Optional)
   To tear down the infrastructure, use `terraform destroy`.  
   This will remove all resources defined in your Terraform configuration.

### Updating Infrastructure with Terraform

1. ### Modify Configuration
   Change your Terraform configuration files (`.tf`) to reflect the desired updates to your infrastructure.

2. ### Review Changes
   Run `terraform plan` to see what changes Terraform will apply based on your updated configuration.

3. ### Apply Updates
   Execute `terraform apply` to apply the planned updates to your infrastructure.  
   Terraform will update existing resources, create new ones, or delete resources as needed to match the configuration.

4. ### Verify Changes
   Check the infrastructure and Terraform outputs to confirm that the updates have been applied correctly.

5. ### Manage State
   The Terraform state file will be updated to reflect the new infrastructure state.  
   Ensure the state file remains consistent and backed up if using remote backends.











### Screencast folgt
