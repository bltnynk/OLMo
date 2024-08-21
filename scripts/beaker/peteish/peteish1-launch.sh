#!/usr/bin/env bash

set -ex

NUM_NODES=2

gantry run \
  --workspace ai2/sewonm \
  --task-name peteish1-baseline \
  --description "Pete-ish 1B" \
  --priority normal \
  --preemptible \
  --beaker-image petew/olmo-torch23-gantry \
  --cluster ai2/jupiter-cirrascale-2 \
  --gpus 8 \
  --replicas "${NUM_NODES}" \
  --leader-selection \
  --host-networking \
  --budget ai2/oe-training \
  --no-nfs \
  --weka oe-training-default:/weka/oe-training-default \
  --propagate-failure \
  --propagate-preemption \
  --synchronized-start-timeout 90m \
  --no-python \
  --env LOG_FILTER_TYPE=local_rank0_only \
  --env OMP_NUM_THREADS=8 \
  --env OLMO_TASK=model \
  --env R2_PROFILE=R2 \
  --env S3_PROFILE=S3 \
  --env WEKA_PROFILE=WEKA \
  --env-secret AWS_CONFIG=SEWONM_AWS_CONFIG \
  --env-secret AWS_CREDENTIALS=SEWONM_AWS_CREDENTIALS \
  --env-secret WANDB_API_KEY=SEWONM_WANDB_API_KEY \
  --shared-memory 10GiB \
  --yes \
  --allow-dirty \
  --timeout=-1 \
  -- /bin/bash -c "scripts/beaker/peteish/peteish1.sh \$BEAKER_LEADER_REPLICA_HOSTNAME ${NUM_NODES} \$BEAKER_REPLICA_RANK"
