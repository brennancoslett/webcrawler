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

############### MsgPack Structures for saving the data ###############
class CrawledURL(Struct, array_like=True):
    """A msgpack struct describing the output of a crawled URL"""
    url: str
    timestamp: datetime
    relevance: dict

############### Database object ###############
class Database():
    """
    Object which handles keeping the state of all the threads for WebCrawling.
    It also handles reading to and from the storage file.
    """

    def __str__(self):
        """
        Provides a better way to represent the object
        when printed out using print().
        """
        to_print = "Database"
        for crawled_url in self.data:
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
        self.decoder = Decoder(List[CrawledURL])
        self.mutex = Lock()
        self.data = self.decode_file(self.input_file)
        self.read_only = False # Flag to ignore writing to a file, stops overwriting

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
        if Path(file).exists():
            try:
                data = Path(file).read_bytes()
                array = self.decoder.decode(data)
            except:
                pass
            if array == []:
                print("Decode failed, leaving original database")
                self.read_only = True

        else:
            print(f"File with name {file} not found.")
        return array

    def msgspec_current_time(self):
        """
        Provides a datetime.datetime object to be used by the
        database to determine when the values in the database are stale.
        This special version of datetime.now provides the tz.info value
        that msgspec requires to convert it to data that can be serialized.
        """
        return datetime.now(timezone.utc)

    def build_crawled_url(self, url: str, relevance: dict):
        """
        To correctly serialize the data, we need timestamps with tzinfo embedded.
        This function takes in the url and the relevance dictionary and returns a
        CrawledURL object with a valid timestamp
        """
        return CrawledURL(url=url, timestamp=self.msgspec_current_time(), relevance=relevance)

    def write_to_disk(self):
        """
        Output the encoded data to a file on disk.
        """
        with self.mutex:
            if not(self.read_only):
                output = self.encoder.encode(self.data)
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
                in_database = self.url_in_database(object.url)
                if in_database == -1 or force_add:
                    if force_add:
                        print(f"Forcing update of {object.url} in database.")
                        if in_database != -1:
                            self.data.pop(in_database)
                    self.data.append(object)
                else:
                    print(f"URL {object.url} is already in database. Did we crawl this twice?")

    def url_in_database(self, url: str):
        """
        Returns index of a CrawledURL if it already exists in the database
        else -1.
        """
        for crawled in self.data:
            if crawled.url == url:
                return self.data.index(crawled)
        return -1

    def data_stale(self, url: str):
        """
        Check if the timestamp on the given url is greater than 5 days
        """
        for crawled_url in self.data:
            if crawled_url.url == url:
                timediff = datetime.now() - crawled_url.timestamp
                days_old = timediff.days()
                if days_old > 5:
                    return True
                else:
                    break
        return False

    def remove(self, object):
        """
        Accepts either a string url or a CrawledURL object,
        finds it in the database if it exists, removes it from the array,
        and returns it.
        """
        with self.mutex:
            idx = None
            url_of_interest = None
            if type(object) is CrawledURL:
                idx = self.data.index(object)
                url_of_interest = object.url
            else:
                url_of_interest = object
                # Remove it with a string url value instead of the whole object
                for crawled_url in self.data:
                    if crawled_url.url == object:
                        idx = self.data.index()
            if idx is None:
                print(f"URL {url_of_interest} not in database.")
                return None
            else:
                return self.data.pop(idx)