#! /usr/bin/env python3

# msgspec dependencies for storing the data.
from msgspec import Struct
from msgspec.msgpack import Decoder, Encoder
from typing import List
# Dependencies for reading the byte information from
# the save file.
from pathlib import Path
# Handling timestamp information for data in Database.
from datetime import datetime, timezone
# Ensure only one thread attempts to update the database at a time.
from threading import Lock
# Used for a reproducible hash function instead of the default python hash() 
import hashlib

############### MsgPack Structures for saving the data ###############
class CrawledURL(Struct, array_like=True):
    """A msgpack struct describing the output of a crawled URL"""
    url: str
    timestamp: datetime
    relevance: dict

class DatabaseStruct(Struct, array_like=True):
    crawled_data: List[CrawledURL]
    url_hash_table: dict
    keyword_dict: dict

############### Database object ###############
class Database():
    """
    Object which handles keeping the state of all the threads for WebCrawling.
    It also handles reading to and from the storage file.
    """
    def hash(self, string):
        """
        https://stackoverflow.com/questions/30585108/disable-hash-randomization-from-within-python-program
        Default hash function is randomized which messes with the lookup table
        """
        return int.from_bytes(hashlib.sha256(string.encode("UTF-8")).digest()[:8], byteorder='big', signed=True)

    def __str__(self):
        """
        Provides a better way to represent the object
        when printed out using print().
        """
        to_print = "Database"
        len_data = len(self.data)
        if len_data <= 10:
            data_array = self.data
        else:
            to_print += " (More than 10 entries in database, only showing first 10)"
            data_array = self.data[:10]
        for crawled_url in data_array:
            to_print += f"\n  url: {crawled_url.url}\n    timestamp: {crawled_url.timestamp}\n    relevance: {crawled_url.relevance}"
        to_print += "\n"
        return to_print

    def __init__(self, input_file="database.msgpack", output_file=None):
        """
        Initializes the object, with values for encoding/decoding the msgpack
        arrays as well as handling input/output file names.
        """
        self.input_file = input_file
        if output_file is not None:
            self.output_file = output_file
        else:
            self.output_file = self.input_file
        self.encoder = Encoder()
        self.decoder = Decoder(DatabaseStruct)
        self.mutex = Lock()
        self.data, self.url_hash_table, self.keyword_dict = self.decode_file(self.input_file)
        self.read_only = False # Flag to ignore writing to a file, stops overwriting
        self.stale_url_days = 5

    def __len__(self):
        """
        When looking for the length of the database return the length
        of the data array.
        """
        return len(self.data)

    ######## "Private" functions ########
    def _msgspec_current_time(self):
        """
        Provides a datetime.datetime object to be used by the
        database to determine when the values in the database are stale.
        This special version of datetime.now provides the tz.info value
        that msgspec requires to convert it to data that can be serialized.
        """
        return datetime.now(timezone.utc)

    def _url_stale(self, crawled_url: CrawledURL):
        """
        Check if the timestamp on the given url is greater than self.stale_url_days
        """
        now = datetime.now(timezone.utc)
        timediff = now - crawled_url.timestamp
        days_old = timediff.days
        if days_old > self.stale_url_days:
            return True
        else:
            return False

    ######## Public functions ########
    def stale_urls(self):
        """
        Returns a list of objects which need to be re-crawled
        as the data in them is stale.
        """
        data = []
        for crawled_url in self.data:
            if self._url_stale(crawled_url):
                data.append(crawled_url.url)
        return data

    def urls_with_keyword(self, keyword: str):
        """
        Returns a tuple of urls + their relevance metric for
        a given keyword
        """
        array = []
        keyword_lower = keyword.lower()
        lower_keyword_dict = {k.lower():v for k,v in self.keyword_dict.items()}
        url_hashes = lower_keyword_dict.get(keyword_lower, [])
        for url_hash in url_hashes:
            data_idx = self.url_hash_table[url_hash]
            crawled_url = self.data[data_idx]
            url = crawled_url.url
            lowercase_rel = {k.lower():v for k,v in crawled_url.relevance.items()}
            relevance = lowercase_rel[keyword_lower]
            array.append((url, relevance))
        if len(array) == 0:
            print("No Matches Found")
            return []
        else:
            sorted_array = sorted(array, key=lambda tup: tup[1], reverse=True)
            return sorted_array
    
    def cleanup(self):
        """
        Provides a function for all tasks that need to be done to
        cleanly save all data in progress and updates the file on disk.
        """
        self.write_to_disk()

    def decode_file(self, file):
        """
        Attempts to decode the Database.decoder object.
        It marks the database as read_only when it cannot be correctly
        parsed otherwise the self.write_to_disk will overwrite the existing database
        with an empty array.
        """
        array = []
        url_hash_table = {}
        keyword_dict = {}
        print("Pulling in database from file.")
        if Path(file).exists():
            try:
                data = Path(file).read_bytes()
                database = self.decoder.decode(data)
                array = database.crawled_data
                url_hash_table = database.url_hash_table
                keyword_dict = database.keyword_dict
            except:
                pass
            if array == []:
                print("Decode failed, leaving original database")
                self.read_only = True
        else:
            print(f"File with name {file} not found.")
        return (array, url_hash_table, keyword_dict)

    def build_crawled_url(self, url: str, relevance: dict):
        """
        To correctly serialize the data, we need timestamps with tzinfo embedded.
        This function takes in the url and the relevance dictionary and returns a
        CrawledURL object with a valid timestamp
        """
        return CrawledURL(url=url, timestamp=self._msgspec_current_time(), relevance=relevance)

    def write_to_disk(self):
        """
        Output the encoded data to a file on disk.
        """
        with self.mutex:
            if not(self.read_only):
                db = DatabaseStruct(self.data, self.url_hash_table, self.keyword_dict)
                output = self.encoder.encode(db)
                # self.encode always outputs a single string
                with open(self.output_file, "wb+") as file:
                    file.write(output)

    def add(self, object: CrawledURL, force_add = False):
        """
        Adds a URL to the list if it isn't already in there.
        It shouldn't already be there as that means we crawled
        the same page twice, unless we loaded an existing database
        from a file. This can be overwritten with the `force_add` flag.
        """
        with self.mutex:
            if not(self.read_only):
                url_hash, in_database = self.url_in_database(object.url, return_hash=True)
                if in_database == -1 or force_add:
                    if force_add:
                        if in_database != -1:
                            old_object = self.data[in_database]
                            self.data[in_database] = object
                            # Leave the hash table alone as the hash is identical
                            # Update the values of the keywords for the old object
                            for keyword in old_object.relevance.keys():
                                # Returns the value of the keyword, unless it doesn't
                                # exist then it returns an empty array
                                value = self.keyword_dict.setdefault(keyword, [])
                                # Remove the keywords of the old object
                                val_idx = value.index(url_hash)
                                value.pop(val_idx)
                        # If not in the database we need to run the normal process
                        else:
                            self.data.append(object)
                            self.url_hash_table[url_hash] = int(len(self.data) - 1)
                    else:
                        self.data.append(object)
                        self.url_hash_table[url_hash] = int(len(self.data) - 1)
                    for keyword in object.relevance.keys():
                        # Returns the value of the keyword, unless it doesn't
                        # exist then it returns an empty array
                        value = self.keyword_dict.setdefault(keyword, [])
                        # Since we just pull a reference to the original array
                        # we can just append here.
                        value.append(url_hash)
                else:
                    print(f"URL {object.url} is already in database. Did we crawl this twice?")

    def url_in_database(self, url: str, return_hash = False):
        """
        Returns index of a CrawledURL if it already exists in the database
        else -1  as well as the hash of the inputted url.
        """
        hashed_url = self.hash(url)
        # Checks if the hashed url is in the table
        # if it is, then it should return the index of the
        # value in the array.
        # if it isn't then it returns -1
        index_in_array = self.url_hash_table.get(hashed_url, -1)
        if return_hash:
            return hashed_url, index_in_array
        else:
            return index_in_array