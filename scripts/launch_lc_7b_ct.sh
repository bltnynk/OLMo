#!/usr/bin/env bash

set -ex


NUM_NODES=4

gantry run \
  --workspace ai2/OLMo-training \
  --task-name long_contexts_7B_cont_train \
  --description "OLMo medium - 7B - long context continued pretraining" \
  --priority normal \
  --beaker-image petew/olmo-torch23-gantry \
  --cluster ai2/jupiter-cirrascale-2\
  --gpus 8 \
  --preemptible \
  --replicas "${NUM_NODES}" \
  --leader-selection \
  --host-networking \
  --budget ai2/oe-training \
  --no-nfs \
  --weka oe-training-default:/weka/oe-training-default \
  --env LOG_FILTER_TYPE=local_rank0_only \
  --env OMP_NUM_THREADS=8 \
  --env OLMO_TASK=model \
  --env NCCL_DEBUG=INFO \
  --env NCCL_IB_HCA="^=mlx5_bond_0" \
  --env NCCL_SOCKET_IFNAME=ib \
  --no-nfs \
  --env-secret WANDB_API_KEY=DUSTINS_WANDB_API_KEY \
  --env-secret AWS_ACCESS_KEY_ID=DUSTINS_AWS_ACCESS_KEY_ID \
  --env-secret AWS_SECRET_ACCESS_KEY=DUSTINS_AWS_SECRET_ACCESS_KEY \
  --shared-memory 10GiB \
  --venv base \
  --propagate-failure \
  --yes \
  --timeout=-1 \
  -- /bin/bash -c " scripts/beaker/lc_7b.sh \$BEAKER_LEADER_REPLICA_HOSTNAME ${NUM_NODES} \$BEAKER_REPLICA_RANK"
