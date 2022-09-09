import parsl
import os
from parsl.configs.local_threads import config
from parsl.data_provider.files import File
from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.executors import WorkQueueExecutor
from parsl.providers import SlurmProvider
from parsl.providers import LocalProvider
from parsl.channels import LocalChannel
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_hostname
from parsl import python_app
from tools import methods

def getConfig():
    # Campus Cluster Configuration
    CampusClusterConfig = Config(
         executors=[
              #HighThroughputExecutor(
              #     label="iqtree_htex",
              #     address=address_by_hostname(),
              #     cores_per_worker=1,
              #     provider=SlurmProvider(
              #          partition='secondary-fdr', # partition
              #          nodes_per_block=2, #number of nodes
              #          min_blocks=1,
              #          init_blocks=0,
              #          max_blocks=50,
              #          scheduler_options='',
              #          cmd_timeout=120,
              #          walltime='04:00:00',
              #          launcher=SrunLauncher(),
              #          worker_init='conda activate /home/ekoning2/scratch/Parsl_test/envParsl37',
              #     ),
              #),
              WorkQueueExecutor(
                   label="gtm_wq",
                   address=address_by_hostname(),
                   autolabel=True,
                   #provider=LocalProvider(
                   #     channel=LocalChannel(),
                   #     init_blocks=1,
                   #     max_blocks=1,
                   #),
                   # NOTE: use the SlurmProvider if running from the login node, and use the LocalProvider if running from a work node
                   provider=SlurmProvider(
                        partition='secondary-fdr', # partition
                        nodes_per_block=1, #number of nodes
                        init_blocks=0,
                        max_blocks=50,
                        min_blocks=0,
                        scheduler_options='',
                        cmd_timeout=120,
                        walltime='04:00:00', # may need a different queue for maximum runtime
                        launcher=SrunLauncher(),
			worker_init='module load python/3; module load anaconda/3; . /usr/local/anaconda/5.2.0/python3/etc/profile.d/conda.sh; conda activate /home/ekoning2/scratch/Parsl_test/env_new_test',
                   ),
		   worker_options="--time=14340", # 4 hours - 1 minute for startup costs
              ),
         ],
	 strategy="simple",
         #max_idletime=30.0, # maximum time leaving a block idle before relinquishing it
    )

    # NOTE: change this for use on other clusters
    return CampusClusterConfig

#@python_app(executors=["gtm_wq"]) # NOTE: you can activate this as a parsl call if you want it to create an item in the queue, but then you need to make sure the walltime is long enough
#def parslBuildTree(method, outputPath, parsl_resource_specification={'cores': 2, 'memory': 1000, 'disk': 1000, 'running_time_min': 18000}, stdout="parslGTM.out", **kwargs):
def parslBuildTreeWQ(method, outputPath, **kwargs):
    #print("building tree with parsl", flush=True)
    return methods.buildTree(method, outputPath, **kwargs)

@python_app(executors=["gtm_wq"])
def parslBuildTree(method, outputPath, parsl_resource_specification={'cores': 1, 'running_time_min': 600}, **kwargs):
    return methods.buildTree(method, outputPath, **kwargs)

