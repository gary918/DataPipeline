# Databricks notebook source
dbutils.widgets.text("input", "","")
#storage_account_name = "mlops3blob";
#storage_container_source_name = "rawdata";
#storage_container_target_name = "prepareddata";
#datafile = "sample.csv"

datafile = dbutils.widgets.get("input")
storage_account_name = getArgument("storage_account_name")
storage_container_source_name = getArgument("storage_container_name")
storage_container_target_name = getArgument("storage_container_target_name")

#mount the source blob storage that represents the source data
source_mount_point = "/mnt/rawdata"
if not any(mount.mountPoint == source_mount_point for mount in dbutils.fs.mounts()): 
  dbutils.fs.mount(
    source = "wasbs://"+storage_container_source_name+"@"+storage_account_name+".blob.core.windows.net",
    mount_point = source_mount_point,
    extra_configs = {"fs.azure.account.key."+storage_account_name+".blob.core.windows.net":dbutils.secrets.get(scope = "testscope", key = "StorageKey")})

#mount the target blob storage that represents the target data
target_mount_point = "/mnt/prepared"
if not any(mount.mountPoint == target_mount_point for mount in dbutils.fs.mounts()): 
  dbutils.fs.mount(
    source = "wasbs://"+storage_container_target_name+"@"+storage_account_name+".blob.core.windows.net",
    mount_point = target_mount_point,
    extra_configs = {"fs.azure.account.key."+storage_account_name+".blob.core.windows.net":dbutils.secrets.get(scope = "testscope", key = "StorageKey")})

# read the files with column information
df = spark.read.format("csv")\
.option("inferSchema", 'true')\
.option("header",'true') \
.load(source_mount_point+"/"+datafile)

# pick only 2 columns
df = df.select('MinTemp','MaxTemp')
filepath_to_save = '/dbfs' + target_mount_point + '/transformed.csv'
#print (filepath_to_save)
#print (storage_container_target_name)
#df.show()
df.toPandas().to_csv(filepath_to_save)


# COMMAND ----------

