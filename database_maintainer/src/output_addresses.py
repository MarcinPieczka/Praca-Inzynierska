from collections import deque
from pprint import pprint

import sys

import constants


class NonExistingTransactionOutputException(Exception):
    pass


class OutputAddresses(object):

    def __init__(self, limit, mongo, logger):
        self.limit = limit
        self.mongo = mongo
        self.logger = logger
        self.addresses = dict()
        self.dict_keys_queue = deque()

    def add_from_outputs(self, tx_hash, timestamp, outputs):
        self.dict_keys_queue.append(tx_hash)
        if len(self.dict_keys_queue) > self.limit:
            del self.addresses[self.dict_keys_queue.popleft()]

        self.addresses[tx_hash] = (timestamp, [out['addresses'] for out in outputs])

    def get(self, tx_hash, index):
        if tx_hash == constants.genesis_hash:
            return None, [None]
        addresses = self.addresses.get(tx_hash)
        if addresses:
            timestamp, outputs = addresses
            return timestamp, outputs[index]
        else:
            projection = self.mongo.get_tx(tx_hash)
            if not projection:
                raise NonExistingTransactionOutputException
            self.logger.register_tx_cache_miss()
            self.logger.register_cache_length(len(self.dict_keys_queue))
            return (
                projection['timestamp'],
                projection['transactions'][0]['outputs'][index]['addresses']
            )
