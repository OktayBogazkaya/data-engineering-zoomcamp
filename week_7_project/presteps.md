# Getting Started

In order to reproduce the repo, please follow all the steps below. 

## Pre-Requisites

We will be using the Google Cloud Platform and Services

### Google Cloud Platform Account

1. Go to [GCP](https://cloud.google.com/) and create an account if you do not have one (GCP offers $300 credits for 90 days)

2. Setup a new project from the GCP [console](https://console.cloud.google.com/) and write down your Project ID.

### Service Account

1. Go to [IAM & Admin](https://console.cloud.google.com/iam-admin) to create a Service Account

2. Assign following roles to the Service Account 

    * Viewer
    * Storage Admin
    * Storage Object Admin
    * BigQuery Admin

3. To create an API key, go to `IAM And Admin > Service Accounts > Click on the service account > KEYS tab > ADD KEY > Create a new key > JSON > Create` and donwload the service account keys (.json) for auth.

4. Open Google Console and anable following APIs for the project

    * IAM Service Account Credentials API
    * Identity and Access Management (IAM) API
    * Compute Engine API
    
    > **_Note_**: When we interact with GCP envioment from our local machine, we do not interact directly with the ressources ( e.g. BigQuery), it happens through API´s (e.g. IAM) which act as enabler of communication 

### Install Google Cloud SDK

1. Run following command from your terminal to check whether Google SDK is already installed your local machine (you can also download it from [here](https://cloud.google.com/sdk/docs/install-sdk))

```
    gcloud -v
```

2. Set environment variable to point to the downloaded auth-keys

```
export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
```

3. Verify the authentication with 

```
gcloud auth application-default login
```

### Setup Virtual Machine on GCP

1. Go to GCP Console > Compute Engine > VM instance > VM instances 

2. Click CREATE INSTANCE and configure your VM by defining 

    * **Name**: Choose any name 
    * **Region**: Pick your favorite region
    * **Series**: E2
    * **Machine type**: e2-standard-4 (4 vCPU, 16GB memory)
    * **Boot Disk**: Change to _Ubuntu_ and _Ubuntu 20.04 LTS_ with _30GB_ of storage

    > **_Note_**: I've used the same configuration like in the first week of the course, but you can configure the VM according your needs. 


### Setup SSH access to VM

To connect to the VM from the local machine, SSH key pair should be generated on the local machine 

1. First, make sure that that the gcloud SDK is configured correctly for the current project

    * Use `gcloud config list` to list all the current config details  
    * If the project doesn't match with the newly created project use `gcloud projects list` to list the projects available 
    * Use `gcloud config set project my-project` to change your current config to the correct project
    * Again, check `with gcloud config list`

2. Create a SSH key by follow the guide [here](https://cloud.google.com/compute/docs/connect/create-ssh-keys) 

> **_NOTE:_** Now on your local machine the folder _~/.ssh_ is created along with two keys (public and private key). Please, do not share your public key with anyone!

3. Get the content of the _gcp.pub_ file in _~/.ssh_ with

```
cat gcp.pub
```

4. Paste the content of the _gcp.pub_ file to GCP Console > Compute Engine > Metadata > SSH KEYS 

5. Go to the newly created VM instance and copy the External IP address 

6. Go back to the terminal and ssh to the VM with the following command from the home directory

```
ssh -i <path-to-private-key> <USER>@<External IP>
```

7. For a quicker log-in into the VM, go to the  _~/.ssh/_ folder on the local machine 

8. Create a config file for configuring SSH

```
touch config
```

9. Open the config file ( I'm using VSCode)

```
code config
```

10. Configure the SSH

```
Host dtc-de-zoomcap-project-vm  # Can be any name of your choosing
    HostName: <External IP of the VM>
    User: <username used when generating the SSH keys>
    IdentityFile: <absolute path to the private keys (eg., ~/.ssh/gcp)>
```

11. Now, use only the following command to ssh into the VM

```
ssh dtc-de-zoomcap-project-vm
```

To logout, just press CTR-D or type `logout`

12. Always shut down the VM in the GCP Console once the work is done in order to avoid unexpected costs. It can be also done via the terminal with

```
sudo shutdown now
```
## Installing Required Software on VM

I will not describe the part how we install Anaconda and Python on the VM, because it will provided with Docker image later on anyway. 

### (Optional) Configure VSCode to access VM

1. Download and install VSCode from [here](https://code.visualstudio.com/download)

2. Open VSCode and install the **Remote-SSH** extension from the Extensions Marketplace


![Install Remote-SSH in VSCode](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Install_RemoteSSH_in_VSCode.png?raw=true)

3. Click _Open a Remote Window_ icon at the bottom left-hand of VSCode UI

![Install Remote-SSH in VSCode](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Open_Remote_Window_VSCode.png?raw=true)

4. Click _Connect to Host_ > Select _Name of config file_

![Install Remote-SSH in VSCode](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Connect_to_Host_VSCode.png?raw=true)

![Install Remote-SSH in VSCode](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Select_Name_of_config_file.png?raw=true)

Now, VSCode can be used to ssh to the VM and open any folder or edit files.

![Install Remote-SSH in VSCode](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Remote-SSH_VSCode_ready.png?raw=true)

### Install Terraform

1. Go to the `bin/` folder and download latest binary file `AMD64 Version:1.4.5` (at the time of writting) for Linux from the official Github repo [here](https://developer.hashicorp.com/terraform/downloads)

```
wget https://releases.hashicorp.com/terraform/1.4.5/terraform_1.4.5_linux_amd64.zip
```

2. Unzip the file

```
unzip terraform_1.4.5_linux_amd64.zip
```

> You might have to install *unzip* with `
sudo apt-get install unzip
` 

3. Remove the zip file

rm terraform_1.4.5_linux_amd64.zip

### Upload Google Credentials to VM

The .json file created before (which contains the Service Account credentials) is on the local machine and needs to be copied to the VM 
as well.

1. On the local machine, navigate to the location of the credentials file 

2. Connect to VM with *sftp* using the hostname choosed when creating the config file for SSH (here **Setup SSH access to** VM)  

```
sftp dtc-de-zoomcap-project-vm
```

2. Create a folder to store the .json file from the local machine

```
mkdir .keys
```

3. Navigate to the directory

```
cd .keys
```

4. Transfer the .json file to the VM

```
put constant-haven-384713-7ff33136173a.json
```


