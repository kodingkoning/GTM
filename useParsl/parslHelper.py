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
from parsl import bash_app
from tools import methods

def getConfig():
    # Campus Cluster Configuration
    CampusClusterConfig = Config(
         executors=[
              HighThroughputExecutor(
                   label="iqtree_htex",
                   address=address_by_hostname(),
                   cores_per_worker=1,
                   provider=SlurmProvider(
                        partition='secondary-fdr', # partition
                        nodes_per_block=2, #number of nodes
                        min_blocks=1,
                        init_blocks=0,
                        max_blocks=50,
                        scheduler_options='',
                        cmd_timeout=120,
                        walltime='01:30:00',
                        launcher=SrunLauncher(),
                        worker_init='conda activate parslEnv',
                   ),
              ),
              WorkQueueExecutor(
                   label="gtm_wq",
                   address=address_by_hostname(),
                   autolabel=True,
                   provider=LocalProvider(
                        channel=LocalChannel(),
                        init_blocks=1,
                        max_blocks=1,
                   ),
                   # NOTE: use the SlurmProvider if running from the login node, and use the LocalProvider if running from a work node
                   #provider=SlurmProvider(
                   #     partition='secondary-fdr', # partition
                   #     nodes_per_block=1, #number of nodes
                   #     init_blocks=0,
                   #     max_blocks=1,
                   #     min_blocks=1,
                   #     scheduler_options='',
                   #     cmd_timeout=120,
                   #     walltime='04:00:00', # may need a different queue for maximum runtime
                   #     launcher=SrunLauncher(),
                   #     worker_init='conda activate parslEnv',
                   #),
              ),
         ],
    )

    # NOTE: change this for use on other clusters
    return CampusClusterConfig

@python_app(executors=["iqtree_htex"])
def parslBuildTree(method, outputPath, **kwargs):
    #print("building tree with parsl", flush=True)
    return methods.buildTree(method, outputPath, **kwargs)

@python_app(executors=["gtm_wq"])
def parslBuildTreeWQ(method, outputPath, **kwargs):
    return methods.buildTree(method, outputPath, **kwargs)

