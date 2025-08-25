# Script for deploying MindSpore-DeepSeek. #

This deployment script is used to automatically deploy VLM+Mindspore DeepSeek R1 and V3. Scripts are written in Python and cover the entire process from image pulling, dependency installation, container deployment, and service starting. The scripts are designed to simplify the deployment process and improve the deployment efficiency and accuracy.

### 1. Environmental requirements ###

1.  **Operating system: OpenEuler22.03 LTS SP4 or later**
2.  **Software dependency:**
    
     *  `docker`Image download and container management;
     *  `Python3`\: used for script execution.
     *  `oedp`\: quick application installation and deployment platform;

### 2. Script execution ###

Configure the config.yaml file by referring to the DeepSeekV3&R1 Deployment Guide-Chapter 4 and run the following command:

```
oedp run install
```

### 3. FAQ ###

1. The downloaded weight is in the CKPT format. By default, the weight in the script is in the safetensor format. How to modify the weight?

```
#Modifying the Weight Type of the config.yaml Model
model_type: ckpt
```

