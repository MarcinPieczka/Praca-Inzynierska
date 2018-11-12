"""
TODO:
- add block height
- use Base58Check where appropriate
"""
from bitcoin.core.script import CScriptTruncatedPushDataError, CScriptInvalidError
from blockchain_parser.block import Block
from blockchain_parser.blockchain import get_blocks
from output_addresses import NonExistingTransactionOutputException

import logger


def get_block(block_info):
    for i, raw_block in enumerate(get_blocks(block_info.path)):
        if block_info.index == i:
            return Block(raw_block), block_info.height


class BlockToDict(object):

    def __init__(self, output_addresses):
        self.output_addresses = output_addresses

    def transform(self, block, height):
        try:
            timestamp = block.header.timestamp
            return {
                'hash': block.hash,
                'version': block.header.version,
                'height': height,
                'prev_hash': block.header.previous_block_hash,
                'merkle_root': block.header.merkle_root,
                'timestamp': timestamp,
                'n_tx': block.n_transactions,
                'size': block.size,
                'bits': block.header.bits,
                'nonce': block.header.nonce,
                'difficulty': block.header.difficulty,
                'transactions': [self.transaction_to_dict(tx, timestamp) for tx in block.transactions]
            }
        except:
            logger.Logger.log("exception for block: {}".format(block.hash))
            raise

    def transaction_to_dict(self, tx, timestamp):
        try:
            outputs = [self.output_to_dict(output, tx.hash) for output in tx.outputs]
            tx_hash = tx.hash
            self.output_addresses.add_from_outputs(tx_hash, timestamp, outputs)

            return {
                'hash': tx_hash,
                # 'version': tx.version,
                'locktime': tx.locktime,
                'outputs': outputs,
                'inputs': [self.input_to_dict(tx_input, tx_hash) for tx_input in tx.inputs],
            }
        except:
            logger.Logger.log('unknown exception when processing tx: {}'.format(tx.hash))
            raise

    def output_to_dict(self, output, tx_hash):
        try:
            return {
                'value': output.value,
                # 'script': output.script.script,
                'addresses': [self.adress_to_dict(addr) for addr in output.addresses],
            }
        except CScriptTruncatedPushDataError:
            """
            problem with script, cannot get addresses
            """
            logger.Logger.log('CScriptTruncatedPushDataError for tx hash: {}'.format(
                tx_hash
            ))
        except CScriptInvalidError:
            """problem with script, cannot get addresses"""
            logger.Logger.log('CScriptInvalidError for tx hash: {}'.format(
                tx_hash
            ))
        return {
            'value': output.value,
            # 'script': output.script.script,
            'addresses': [],
        }

    def input_to_dict(self, tx_input, parent_tx_hash):
        tx_hash = tx_input.transaction_hash
        tx_index = tx_input.transaction_index
        try:
            output_timestamp, addresses = self.output_addresses.get(tx_hash, tx_index)
            return {
                'transaction_hash': tx_hash,
                'transaction_index': tx_index,
                'addresses': addresses,
                'output_timestamp': output_timestamp,
            }
        except NonExistingTransactionOutputException:
            #logger.Logger.log('tx with non existing input: {}'.format(parent_tx_hash))
            return {
                'transaction_hash': tx_hash,
                'transaction_index': tx_index,
                'addresses': [],
                'output_timestamp': None,
            }

    def adress_to_dict(self, addr):
        return {
            'hash': addr.hash,
            'public_key': addr.public_key,
            'address': addr.address,
            'type': addr.type,
        }
