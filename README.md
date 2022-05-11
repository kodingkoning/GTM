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

See `useParsl/parslHelper.py` for the default configuration and to update the configuration for your own use.

At minimum, change the flag for `run_pipeline.py` to `--parsl True`, set the partition in the config to the queue you would like to use, and change the path for the conda environment activation. Check that the maximum blocks and scheduler options work for your account and system.

### What parameters should I use for Parsl?

The ideal Parsl parameters depend on the hardware you are using, how busy your machine is, and the size of the tree you are working with. The parameters in __bold__ are mandatory to check/change.

- Executor
        - Currently, GTM uses a HighThroughputExecutor labeled "iqtree_htex" for the subtree steps, and then a WorkQueueExecutor to run the other tree building steps. This allows the steps building the large trees to be assigned more hardware resources than the steps building the subtrees.
- __Provider__
	- By default, GTM will use a SlurmProvider for the subtree building step and a LocalProvider for building the other trees. Using the SlurmProvider allows the resources used by the software to expand during the embarassingly parallel phase of building the subtrees. Using the LocalProvider for the other steps means that the other tree building steps will use the node allocated for the job. In the future, we will implement an option that will allow for running the Python script on a login node and start jobs for all the expensive computation.
	- If you are on a different sort of machine, such as a aprun machine or laptop, Parsl has [configuration documentation](https://parsl.readthedocs.io/en/stable/userguide/configuring.html) to help select which provider and parameters could be suitable for that machine.
- __Memory per worker__
		- In GB, this is the minimum memory required per worker. This depends on the software you are using and the size of the trees they are estimating. This will need to be higher for the WorkQueueExecutor since it is handling the starting tree and can be much lower for the HighThroughputExecutor for the subtrees. 
- Label
	- The label for each of the executors is used by Parsl to decide which of the executors to use for a given step. If you change the executors, these names need to be changed as well. If you want to rename them or add more executors, you can do so in `pipeline/pipeline_operations.py`.
- Parallelism
	- Parsl's documentation provides a description of the [parallelism parameter](https://parsl.readthedocs.io/en/stable/userguide/execution.html?highlight=executors#parallelism). A higher level of parallelism will conserve resources, and a lower level of parallelism will request additional blocks more eagerly.
- HighThroughputExecutor SlurmProvider (some fields will also apply to other provider types)
	- __Partition__
		- The partition for the Slurm provider MUST match your account and your machine. This is the queue that will be used by Parsl to request resources when this executor is used. You should use a queue that has the nodes you would like to use, and ideally one with short wait times. If there are long wait times, then the main work stream will need to wait on the resources.
	- Nodes per block
		- This is the number of nodes you would like to request at one time. This depends on both your job size and machine. A high number of nodes in a block means that Parsl will start fewer jobs, but it could also mean that some of the resources may sit idle. One or two may be good numbers of nodes in many situations since no task performed in GTM will be able to use multiple nodes on its own.
	- Init blocks
		- In most cases, this should be 0. Starting with no blocks allows the initial steps of building and decomposing the starting tree to execute without extra resources sitting idle.
	- __Max blocks__
		- The maximum number of blocks completely depends on the size of the tree you are estimating and the resources available to you. If you will be estimating many subtrees, it will be useful to have a higher block maximum. If you set it too low and do not maximize the parallelism, then the additional tasks will run after the first set of tasks has completed. If you set it too high, then not all of the blocks will be requested. Setting this too high instead of too low is useful for GTM to complete as quickly as possible.
	- Scheduler options
		-These are the options needed for Slurm. There may be none, but if you have particular `#SBATCH` arguments to include, this is where to add them.
	- Command timeout
		- This is the amount of time that Parsl will wait between calling srun and the resources being allocated. Setting a longer amount of time will make GTM more robust to busy queues.
	- __Walltime__
		- This is the amount of time that Parsl wil request each block for. The minimum time to request would be the time required for building a subtree. The maximum time is the maximum for the queue you are using. Choosing a time shorter than needed to build a single subtree will be fatal. Choosing too long of a time will mean that all of the blocks will keep their resources until the end of GTM's execution, and therefore resources will be wasted. If you are not refining the tree after merging the trees, that time will be negligible. If you are refining the trees, then that could mean large numbers of nodes are sitting idle. A good medium amount of time in the case where the maximum blocks * maximum tasks per block exceeds the number of subtrees would be the maximum time for computing a subtree. In the case where the number of subtrees is larger than the subtrees that will be estimated at the same time, a good amount of time would be `(max time for subtree) * (number of subtrees) / ( (max blocks) * (nodes per block) * (jobs per node) )`. Jobs per node depends on the number of threads given to each of the jobs.
	- __Launcher__
		- Srun works for Slurm machines. This parameter depends on the management of the machine you are using, so look to Parsl's documentation for selection your launcher.
	- Cores per worker
		- This is the number of cores to give each task. This depends on which subtree application you are using, and the size of each job. If you are using IQ-TREE, then it is parallelized across the length of the sequences. You may want to try an experimental run with some of your sequences to see how many threads IQ-TREE or the application used for this step can efficiently use. For example, with IQ-TREE and RNASim sequences, it can only use one thread efficiently, so this should be set to 1. You should also check the amount of memory that each subtree task will require and make sure the number of subtrees per node * memory required for each < memory per node.

- - - -

## Things to Keep in Mind

* dendropy's memory usage starts to become excessive when approaching one million taxa. Future work will optimize GTM to deal with this.
