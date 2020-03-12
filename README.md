# Schedulus

### HPC Scheduling Simulator

The simulator is written in Python. Schedulus takes job events from a workload trace (e.g., the SWF format from the well-known Parallel Workload Archive at http://www.cs.huji.ac.il/labs/parallel/workload/). Based on the events, the simulator emulates job submission, allocation, and execution according to a specific scheduling policy.

Schedulus was originally developed by Dan Rauch and Nicholas Velcich (version 0.1.0) in 2020 under the supervision of Zhiling Lan at the Illinois Institute of Technology. Schedulus is an iteration on previous work done by Dongxu Ren, Wei Tang, Xu Yang, and Yuping Fan on their CQSim project having similar goals (http://bluesky.cs.iit.edu/cqsim/) (https://github.com/SPEAR-IIT/CQSim).

#### Build from Source

```sh
cd schedulus
virtualenv -p python3 venv
source ./venv/bin/activate
pip3 install --editable .
```

#### Run the Program

```sh
schedulus run fcfs -p data/input/test.swf -b none
```