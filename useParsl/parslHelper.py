import parsl
import os
from parsl.configs.local_threads import config
from parsl.data_provider.files import File
from parsl.config import Config
from parsl.executors import HighThroughputExecutor
from parsl.providers import SlurmProvider
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_hostname
from tools import methods
from parsl import python_app

def getConfig():
    # Campus Cluster Configuration
    CampusClusterConfig = Config(
         executors=[
              HighThroughputExecutor(
                   label="CC_htex",
                   worker_debug=False,
                   address=address_by_hostname(),
                   cores_per_worker=8.0,
                   provider=SlurmProvider(
                        partition='secondary-fdr', # partition
                        nodes_per_block=2, #number of nodes
                        init_blocks=1,
                        max_blocks=20,
                        scheduler_options='',
                        cmd_timeout=60,
                        walltime='01:00:00',
                        launcher=SrunLauncher(),
                        worker_init='conda activate /home/ekoning2/scratch/Parsl_test/envParsl37',
                   ),
              )
         ],
    )

    # NOTE: change this for use on other clusters
    return CampusClusterConfig

@python_app
def parslBuildTree(method, outputPath, **kwargs):
    print("building tree with parsl", flush=True)
    return methods.buildTree(method, outputPath, **kwargs)

