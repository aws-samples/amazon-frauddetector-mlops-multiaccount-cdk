# ***************************************************************************************
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                    *
#                                                                                       *
# Permission is hereby granted, free of charge, to any person obtaining a copy of this  *
# software and associated documentation files (the "Software"), to deal in the Software *
# without restriction, including without limitation the rights to use, copy, modify,    *
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to    *
# permit persons to whom the Software is furnished to do so.                            *
#                                                                                       *
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,   *
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A         *
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT    *
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION     *
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE        *
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                *
# ***************************************************************************************

import argparse
import logging
import os
import random
import string
import sys
from datetime import datetime

import numpy as np
import pandas as pd

FRAUD_DETECTOR_MANDATORY_TIMESTAMP = "EVENT_TIMESTAMP"

FRAUD_DETECTOR_MANDATORY_LABEL = "EVENT_LABEL"


class DemoDataTransformer:
    """
    This shows a simple skeleton data transformer pipeline for the default fraud detector dataset..

    """

    def __init__(self):
        pass

    def generate_random_data(self, size: int = 30000) -> pd.DataFrame:
        """
Generates random data
        :param size: The size of the dataset in terms of number of rows
        :return: 1 data frame
        """
        self._logger.info("Loading data..")

        df_train = pd.DataFrame(index=range(0, size)) \
            .pipe(self.generate_binary_label, FRAUD_DETECTOR_MANDATORY_LABEL) \
            .pipe(self.generate_random_date, FRAUD_DETECTOR_MANDATORY_TIMESTAMP) \
            .pipe(self.generate_random_email, "email") \
            .pipe(self.generate_random_ip, "ip")

        return df_train

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
Write data transformations here..
        :param df:
        """
        self._logger.info("Running transformations")
        # TODO: Write transformations
        return df

    def write_csv_s3(self, df: pd.DataFrame, file_name: str, s3_destination_uri: str) -> pd.DataFrame:
        """
Writes the dataframe to s3 in csv format
        :param s3_destination_uri: The s3 uri s3://mybucket/data.csv
        :param df:
        :param file_name:
        :return:
        """
        self._logger.info("Writing data to s3 {}".format(s3_destination_uri))

        s3_file_path = "{}/{}".format(s3_destination_uri.rstrip("/"), file_name.lstrip(os.path.sep))

        # write to s3
        df.to_csv(s3_file_path, header=True, index=False)
        return df

    def write_csv(self, df: pd.DataFrame, file_path: str) -> pd.DataFrame:
        """
Writes the dataframe to local file system in csv format
        :param df:
        :param file_path:
        :return:
        """
        self._logger.info("Writing data to  {}".format(file_path))

        # write to s3
        df.to_csv(file_path, header=True, index=False)
        return df

    def run_pipeline(self, **kwargs):
        """
        Run the entire data cleansing pipeline
        :return:
        """
        # Step1: Read data
        df_train = self.generate_random_data()

        # Step2: Apply transformations
        # TODO: run any transformation

        # Step 3: Write results
        self.write_csv_s3(df_train, "train.csv", **kwargs)

    @property
    def _logger(self):
        return logging.getLogger(__name__)

    def generate_random_ip(self, df, column_name):
        start = 1
        end = 255
        a = np.random.randint(start, end, df.shape[0])
        b = np.random.randint(start, end, df.shape[0])
        c = np.random.randint(start, end, df.shape[0])
        d = np.random.randint(start, end, df.shape[0])
        df[column_name] = [f"{t[0]}.{t[1]}.{t[2]}.{t[3]}" for t in zip(a, b, c, d)]

        return df

    def generate_random_date(self, df, column_name):
        ys = np.random.randint(2010, 2020, df.shape[0])
        ms = np.random.randint(1, 12, df.shape[0])
        ds = np.random.randint(1, 28, df.shape[0])
        hs = np.random.randint(0, 24, df.shape[0])
        df[column_name] = [datetime(y, m, d, h) for (y, m, d, h) in zip(ys, ms, ds, hs)]
        return df

    def generate_random_email(self, df, column_name):
        names = ["".join(random.sample(string.ascii_lowercase, 10)) for i in range(df.shape[0])]
        domains = ["".join(random.sample(string.ascii_lowercase, 5)) for i in range(df.shape[0])]

        df[column_name] = [f"{n}@{d}.com" for (n, d) in zip(names, domains)]
        return df

    def generate_binary_label(self, df, column_name):
        flag = np.random.randint(0, 2, df.shape[0])
        df[column_name] = flag
        return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--s3desturi", help="The s3 prefix to write to. e.g. s3://mybucket/prefix", required=True)

    parser.add_argument("--log-level", help="Log level", default="INFO", choices={"INFO", "WARN", "DEBUG", "ERROR"})
    args = parser.parse_args()
    print(args.__dict__)

    # Set up logging
    logging.basicConfig(level=logging.getLevelName(args.log_level), handlers=[logging.StreamHandler(sys.stdout)],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Run
    DemoDataTransformer().run_pipeline(s3_destination_uri=args.s3desturi)
