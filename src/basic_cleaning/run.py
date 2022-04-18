#!/usr/bin/env python
"""
Download the raw dataset from W&B, apply data cleaning operations, export the result to a new artifact
"""
import os 
import sys
import argparse
# from ast import Str
import logging

import pandas as pd 
import wandb

from wandb_utils.log_artifact import log_artifact

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    logging.info(f"Start Preprocessing run ")
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info(f"Retrieving  {args.input_artifact} ...")
    artifact_local_path = run.use_artifact(args.input_artifact).file()


    logger.info(f"Read into Pandas dataframe.")
    df = pd.read_csv(artifact_local_path)

    #################################
    # Data Cleaning Operations      #
    #################################
    logger.info(f"Drop rows with price not between  {args.min_price} and {args.max_price}.")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()


    logger.info(f"Convert last_review date from string to datetime format.")
    df['last_review'] = pd.to_datetime(df['last_review'])


    logger.info(f"Write preprocessed data locally.")
    df.to_csv(args.output_artifact, index=False)

    #################################
    # Save and finish component run #
    #################################
    logger.info(f"Upload preprocessed data {args.output_artifact} to W&B")
    log_artifact(
        artifact_name = args.output_artifact,
        artifact_type = args.output_type,
        artifact_description = args.output_description,
        filename = args.output_artifact,
        wandb_run = run,
    )

    logger.info(f"End Preprocessing run")
    run.finish()




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Data Cleaning Component")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully qualified name for input artifact (raw dataset) (name:version)",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of output artifact (cleaned dataset)", 
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price cut-off amount",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price cut-off amount",
        required=True
    )


    args = parser.parse_args()

    go(args)
