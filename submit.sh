#!/bin/bash -l
#SBATCH --job-name=ilambhydro
#SBATCH --account=cli138
#SBATCH --time=3:00:00
#SBATCH --nodes=4
#SBATCH --output=%x.log

bash
module unload darshan-runtime
conda activate /ccs/proj/cli137/nate/ilamb272

export ILAMB_ROOT=/lustre/orion/cli137/world-shared/ILAMB
cd $SLURM_SUBMIT_DIR

srun -n 16 --cpu-bind=cores --distribution=cyclic ilamb-run \
     --config hydro.cfg \
     --model_setup models_cmip6.yaml \
     --title "ILAMB-Hydro" \
     --define_regions CONUS.nc CONUS_HUC2.nc \
     --regions global r01 r02 r03 r04 r05 r06 r07 r08 r09 r10 r11 r12 r13 r14 r15 r16 r17 r18 \
     --build_dir ./_build \
     --rmse_score_basis cycle \
