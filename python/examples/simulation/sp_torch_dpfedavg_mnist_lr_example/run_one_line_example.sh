#!/usr/bin/env bash

WORKER_NUM=$1

PROCESS_NUM=`expr $WORKER_NUM + 1`
echo $PROCESS_NUM

hostname > mpi_host_file

mpirun -np $PROCESS_NUM \
-hostfile mpi_host_file \
python torch_fedavg_defense_mnist_lr_one_line_example.py --cf config/fedml_config.yaml