#!/bin/bash
#SBATCH --partition=<your-partition>
#SBATCH --time=03:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4
#SBATCH --account=<your-account>
#SBATCH --mail-user=<your-email>
#SBATCH --mail-type=END,FAIL
