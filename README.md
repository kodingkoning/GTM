# GTM
Guide Tree Merger - a tool for merging disjoint trees.

- - - -

## Dependencies
GTM requires
* Python 3
* dendropy Python package

- - - -

## Getting Started

Please navigate to the "example" directory to get started.\
GTM's commandline arguments are as follows:  

`-s` specifies the path to the guide tree (AKA starting tree)\
`-t` specifies the list of subtrees being merged\
`-o` specifies the path to the output tree

We can run our example merge with the following command, which will save the result as gtm\_tree.tre:

`python3 ../gtm.py -s guide_tree.tre -t subtrees/subset_tree_0.tre subtrees/subset_tree_1.tre subtrees/subset_tree_10.tre subtrees/subset_tree_11.tre subtrees/subset_tree_12.tre subtrees/subset_tree_13.tre subtrees/subset_tree_2.tre subtrees/subset_tree_3.tre subtrees/subset_tree_4.tre subtrees/subset_tree_5.tre subtrees/subset_tree_6.tre subtrees/subset_tree_7.tre subtrees/subset_tree_8.tre subtrees/subset_tree_9.tre -o gtm_tree.tre`

To run the entire pipeline in one command, we can use run\_pipeline.py and specify the software to use for the subsets.

`python3 ../run_pipeline.py -a aln.fas -o gtm_tree.tre -s fasttree --maxsubsetsize 1000 --trees iqtree --polytomies none --branchlengths none --parsl False`
- - - -

## Using parallelism

In order to use Parsl parallelism, you must have [Parsl installed](https://parsl.readthedocs.io/en/stable/quickstart.html) in a conda environment. Then, modify useParsl/parslHelper.py for the appropriate configuration based on the machine you are running on. The `getConfig()` function must return the configuration suitable for your system. The example given is for UIUC's Campus Cluster. Similar configurations will work for other slurm-managed machines. Parsl's documentation has [examples from many different machines](https://parsl.readthedocs.io/en/stable/userguide/configuring.html)

For your conda environment, we recommend using Python 3.7.

```
# excerpted from useParsl/parslHelper.py

def getConfig():
    # Campus Cluster Configuration
    CampusClusterConfig = Config(
         executors=[
              HighThroughputExecutor(
                   label="CC_htex",
                   worker_debug=False,
                   address=address_by_hostname(),
                   cores_per_worker=16.0,
                   provider=SlurmProvider(
                        partition='secondary-fdr', # partition
                        nodes_per_block=2, #number of nodes
                        init_blocks=1,
                        max_blocks=50,
                        scheduler_options='',
                        cmd_timeout=60,
                        walltime='04:00:00',
                        launcher=SrunLauncher(),
                        worker_init='conda activate /home/ekoning2/scratch/Parsl_test/envParsl37',
                   ),
              )
         ],
    )

    # NOTE: change this for use on other clusters
    return CampusClusterConfig
```

At minimum, change the flag for `run_pipeline.py` to `--parsl True`, set the partition in the config to the queue you would like to use, and change the path for the conda environment activation. Check that the maximum blocks and scheduler options work for your account and system.

- - - -

## Things to Keep in Mind

* dendropy's memory usage starts to become excessive when approaching one million taxa. Future work will optimize GTM to deal with this.
