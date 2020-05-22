# Setting up a CI/CD data pipeline based on Azure DevOps, Azure Data Factory and Azure Databricks
<!-- TOC -->

- [Setting up a CI/CD data pipeline based on Azure DevOps, Azure Data Factory and Azure Databricks](#setting-up-a-cicd-data-pipeline-based-on-azure-devops-azure-data-factory-and-azure-databricks)
- [Introduction](#introduction)
- [Technology stack](#technology-stack)
    - [Azure DevOps](#azure-devops)
    - [Azure Data Factory](#azure-data-factory)
    - [Azure Databricks](#azure-databricks)
    - [Azure Blob Storage](#azure-blob-storage)
    - [Azure Key Vault](#azure-key-vault)
- [Architecture](#architecture)
    - [Version control](#version-control)
    - [Continuous Integration](#continuous-integration)
    - [Continuous Deployment](#continuous-deployment)
    - [Secured connections](#secured-connections)
    - [Future improvement](#future-improvement)
- [Get started with the sample project](#get-started-with-the-sample-project)
    - [Preparation](#preparation)
        - [Azure account](#azure-account)
        - [Azure DevOps](#azure-devops-1)
    - [Provision](#provision)
    - [Deploy](#deploy)
    - [Integration test](#integration-test)
    - [Summary](#summary)
- [References](#references)

<!-- /TOC -->
# Introduction 
In this article, we'll setup a data pipeline using Azure DevOps, Azure Data Factory and Azure Databricks. This data pipeline can be used not only as a part of the end to end machine learning pipeline, but also as a base for an A/B testing solution.

Please get the sample project source code [here](https://github.com/gary918/DataPipeline).

# Technology stack
The following Azure services are to be used to implement this data pipeline.
## Azure DevOps
Azure DevOps provides developer services to support teams to plan work, collaborate on code development, and build and deploy applications. Developers can work in the cloud using Azure DevOps Services or on-premises using Azure DevOps Server. Here we'll use Azure DevOps Services in the cloud. More specifically, the following services provided by Azure DevOps will be used for setting up the solution:
- **Azure Repos** provides Git repositories for source control of your code
- **Azure Pipelines** provides build and release services to support continuous integration and delivery of your apps
- **Azure Artifacts** allows teams to share Maven, npm, and NuGet packages from public and private sources and integrate package sharing into your CI/CD pipelines
## Azure Data Factory
Azure Data Factory is the cloud-based ETL and data integration service that allows you to create data-driven workflows for orchestrating data movement and transforming data at scale. 
## Azure Databricks
Azure Databricks is an Apache Spark-based analytics platform optimized for the Microsoft Azure cloud services platform. Designed with the founders of Apache Spark, Databricks is integrated with Azure to provide one-click setup, streamlined workflows, and an interactive workspace that enables collaboration between data scientists, data engineers, and business analysts.
## Azure Blob Storage
Azure Blob storage is Microsoft's object storage solution for the cloud. Blob storage is optimized for storing massive amounts of unstructured data. Unstructured data is data that doesn't adhere to a particular data model or definition, such as text or binary data.
## Azure Key Vault
Azure Key Vault is a tool for securely storing and accessing secrets. A secret is anything that you want to tightly control access to, such as API keys, passwords, or certificates. A vault is a logical group of secrets.
# Architecture
<div style="align: center">
<img src="images/architecture.PNG" alt="architecture">
</div>

<p style="text-align: center;">Figure 1. Architecture</p>

As you can see in the diagram of our sample project, we are using Azure Data Factory pipeline ("DataPipeline") to coordinate the activities for data ingestion and data preparation. The Azure Data Factory pipeline can be triggered manually or by pre-defined triggers (Schedule, Tumbling Window or Event). Also, Azure Pipeline can trigger the Azure Data Factory pipeline if the conditions are met.

In the sample project, "DataPipeline" consists 3 activities: "Copy Data", "Transformation" and "Model training & scoring". "Copy Data" copies the data from the original storage where the raw data or source data is stored, to Azure Blob Storage. The original storage could be on-premise or cloud storage such as AWS S3. After being copied to Azure Blob Storage, the data can be easily used by the following activities.

The second activity, "Transformation" will activate a Jupyter Notebook file running on Azure Databricks. The notebook file accesses the data copied to Azure Blob Storage, transforms the oringial data by keeping only the 2 columns that are needed for the model training.

The third activity, "Model training & scoring" will also run a Jupyter Notebook file which uses the transformed data to [train and score a simple machine learning model](https://towardsdatascience.com/a-beginners-guide-to-linear-regression-in-python-with-scikit-learn-83a8f7ae2b4f).

The pipeline can also be extended by adding more activities to do more data processing jobs. For instance, as the diagram shows, we can add a "Machine Learning Execute Pipeline Activity" to trigger an Azure Machine Learning pipeline to train, evaluate and register a machine learning model. 

Azure Repos works for source code version control. 

Azure Pipelines implements CI/CD pipelines for this use case. Starting from an Azure Resource Group for "Development", if needed, Azure Pipelines can help quickly deploy another Azure Resource Group for "Test" or "Production" by using different versions of variables and parameters.

## Version control
Azure Repos is used for the source file version control.

Azure Data Factory can be integrated with an Azure Repos Git organization repository for source control, collaboration, versioning, and so on. In order to do version control of Azure Data Factory pipelines, we can create a development data factory configured with Azure Repos Git, allowing relevant developers to author Azure Data Factory resources like pipelines and datasets. The developers can make changes in their feature branches and create a pull request from their feature branch to the master or collaboration branch to get their changes reviewed by peers. After a pull request is approved and changes are merged in the master branch, the changes can be published as Azure Resource Manager templates to "adf-publish" branch in the development factory.

Also, Git version control can be enabled for the Jupyter Notebook files running on Azure Databricks.
## Continuous Integration
Continuous integration (CI) is a development practice where developers integrate code into a shared repository frequently, preferably several times a day.

The sample project doesn't include the process of code linting and unit tests which can be done by using flake8 and pytest.

In the CI stage of this sample, the pipeline "checkout" the notebook file and publish it as an artifact named "notebook". In the meantime, the Azure Data Factory pipeline Resource Manager templates are also checked out through "adf_publish" branch and published as "adf-pipelines" artifact. Those two artifacts will be used by the following steps. 
## Continuous Deployment
Continuous deployment (CD) is a strategy for software releases wherein any code commit that passes the automated testing phase is automatically released into the production environment, making changes that are visible to the software's users.

In the CD stage, the generated artifact "notebook" will be deployed to Azure Databricks and the artifact "adf-pipeline" will be deployed to Azure Data Factory. Please note that we can deploy those artifacts into different Azure Databricks and Azure Data Factory environments by inputting different parameters defined in Azure DevOps Variable Group.
This feature can be used to implement an A/B testing environment by providing different datasets, libraries, algorithms, tuning methods for training different machine learning models.  
## Secured connections
Since we will integration Azure DevOps, Azure Data Factory, Azure Databricks and Azure Blob Storage together, we need to use Azure Databricks personal access token (PAT), Azure Blob Storage access keys. 

The best solution is to have these secret tokens or keys stored in Azure Key Vault. Why? Because Azure Key Vault can help us securely store and manage sensitive information such as keys, password, certificates, etc. in a centralized storage which are safeguarded by industry-standard algorithms, key lengths, and even hardware security modules. This prevents information exposure through source code, a common mistake that many developers make. Many developers leave sensitive information such as database connection strings, passwords, private keys, etc. in their source code which when gained by malicious users can result in undesired consequences. Access to a key vault requires proper authentication and authorization and with RBAC, we can have even fine granular control who has what permissions over the sensitive data.

Within Azure DevOps, we can create Variable Groups which contain variables linking to secrets from Azure Key Vaults. In this way, these secret tokens and keys can be used through variables in Azure DevOps pipelines, rather than being input into the source code with sensitive information.

In order to make Azure Data Factory able to access Azure Blob Storage and Azure Databricks, we need to create linked services which are able to connect to Azure Key Vault to get storage access key and Azure Databricks PAT.

Additionally, Azure Databricks needs to configure its secret scope for the Azure Key Vault, to make sure its notebook files are able to access the blob storage. 

Meanwhile, "Get" and "List" access policies for the Azure Data Factory and Azure Databricks need to be set for the Azure Key Vault. 
## Future improvement
If you want to build an end to end machine learning pipeline, you can consider another better solution, which is to use Azure Data Factory "Machine Learning Execute Pipeline" activity to run an Azure Machine Learning pipeline that handles the steps such as model training, model evaluation and registration. Then Azure Pipelines can be used for orchistrating deploying the model in Azure Container Instance, Azure WebApp or Azure Kubernetes Service.
[MLOps with Azure ML](https://github.com/Microsoft/MLOpsPython) is a highly recommended open source project for you to start that kind of work.   

# Get started with the sample project
## Preparation
Please use the following check list for the prerequisites to run this sample project.
### Azure account
If you don't have an Azure account, create one for free [here](https://azure.microsoft.com/en-us/free/).
### Azure DevOps
- Create a DevOps project
- Clone https://github.com/gary918/DataPipeline.git
- Set up Azure Service Connection named "azure_rm_connection"
- Create a Variable Group "datapipeline-vg" contains the following variables:

| Variable Name               | Suggested Value                    |
| --------------------------- | -----------------------------------|
| LOCATION                    | [Your resource location]           |
| RESOURCE_GROUP              | [Your resource group name]         |
| DATA_FACTORY_DEV_NAME       | [Azure Data Factory dev name]      |
| DATA_FACTORY_TEST_NAME      | [Azure Data Factory test name]     |
| ADF_PIPELINE_NAME           | DataPipeline                       | 
| DATABRICKS_NAME             | [Azure Databricks name]            |
| AZURE_RM_CONNECTION         | azure_rm_connection                |
| DATABRICKS_URL              | [Azure Databricks URL]             |
| STORAGE_ACCOUNT_NAME        | [Storage Account Name]             |
| STORAGE_CONTAINER_NAME      | [Storage Container Name]           |

## Provision
- Use Azure Portal or PowerShell scripts to provision the following resources in a Azure Resource Group.
    - Azure Blob Storage. In addition, create 2 containers with the names: 1) "rawdata", 2) "prepareddata"
    - Azure Databricks. Please refer to [this document](https://docs.microsoft.com/en-us/azure/databricks/security/secrets/secret-scopes) to create a secret scope named "testscope" within the Azure Databricks workspace.
    - Azure Key Vault
    - Azure Data Factory 
- Create a Variable Group "keys-vg" contains the following variables linking to the secrets in the Azure Key Vault:

| Variable Name               |
| --------------------------- |
| databricks-token            |
| StorageConnectString        |
| StorageKey                  |

## Deploy
- Install DevOps for Azure Databricks extension (https://marketplace.visualstudio.com/items?itemName=riserrad.azdo-databricks)
- Create a new Azure Pipeline using data_pipeline_ci_cd.yml
- Run this Azure Pipeline

## Integration test
- Create a new Azure Pipeline using data_pipeline_test.yml
- Test the data pipeline and see the result of running mynotebook.py in Azure Databricks
- To check if the data pipeline works properly, goto check Azure Databricks cluster's Driver Logs. You will see the following message if the machine learning model has been successfully trained.
```
Model trained.
Regressor intercept: 10.661852
Regressor coef: 0.920340
```
## Summary
In this article, we introduced how to set up a CI/CD data pipeline using Azure DevOps, Azure Data Factory and Azure Databricks.

# References
- [Azure DevOps](https://docs.microsoft.com/en-in/azure/devops/user-guide/what-is-azure-devops?view=azure-devops)
- [Azure Data Factory](https://docs.microsoft.com/en-in/azure/data-factory/introduction)
- [Azure Databricks](https://docs.microsoft.com/en-us/azure/azure-databricks/what-is-azure-databricks)
- [Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-overview)
- [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/key-vault-overview)
- [Branching policies](https://docs.microsoft.com/ja-jp/azure/devops/repos/git/branch-policies-overview?view=azure-devops&viewFallbackFrom=azdevops)
- [Continuous integration and delivery in Azure Data Factory](https://docs.microsoft.com/en-us/azure/data-factory/continuous-integration-deployment)
- [DevOps for a data ingestion pipeline](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-cicd-data-ingestion?view=azure-ml-py)
- [MLOps with Azure ML](https://github.com/Microsoft/MLOpsPython)
- [DevOps In Azure With Databricks And Data Factory](https://cloudarchitected.com/2019/04/devops-in-azure-with-databricks-and-data-factory/)
