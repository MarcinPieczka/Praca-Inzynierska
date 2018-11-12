import time

from blockchain_parser_enchancements import block_to_dict, get_block


def split_list(lst, n):
    """splits list to n lists as equally as possible"""
    splitted = []
    for i in reversed(range(1, n + 1)):
        split_point = len(lst) // i
        splitted.append(lst[:split_point])
        lst = lst[split_point:]
    return splitted


class FakeMongoCollection(object):

    def insert_one(self, sth):
        pass

    def find(self, sth):
        return self

    def sort(self, sth):
        return self

    def limit(self, sth):
        return self

    def count(self):
        return 0
