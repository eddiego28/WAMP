##############################################################################
#
#                        Crossbar.io Database
#     Copyright (c) typedef int GmbH. Licensed under MIT.
#
##############################################################################

import pprint

import flatbuffers
import numpy as np
from zlmdb import table, MapStringFlatBuffers

from cfxdb.gen.xbrmm import IPFSFile as IPFSFileGen


class _IPFSFileGen(IPFSFileGen.IPFSFile):
    @classmethod
    def GetRootAsIPFSFile(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = _IPFSFileGen()
        x.Init(buf, n + offset)
        return x


class IPFSFile:
    """
    Record of downloaded files from Infura
    """
    def __init__(self, from_fbs=None):
        self._from_fbs = from_fbs
        # string (multihash)
        self._file_hash = None
        # bool
        self._downloaded = None
        # uint32
        self._retries = None
        # uint64 (timestamp)
        self._errored_at = None

    def marshal(self):
        obj = {
            'file_hash': self.file_hash,
            'downloaded': self.downloaded,
            'retries': self.retries,
            'errored_at': self.errored_at,
        }

        return obj

    def __str__(self):
        return '\n{}\n'.format(pprint.pformat(self.marshal()))

    @property
    def file_hash(self) -> str:
        """
        IPFS Multihash pointing to a RDF/Turtle file
        """
        if self._file_hash is None and self._from_fbs:
            _hash = self._from_fbs.FileHash()
            if _hash:
                self._file_hash = _hash.decode('utf8')
        return self._file_hash

    @file_hash.setter
    def file_hash(self, value):
        assert value is None or type(value) == str
        self._file_hash = value

    @property
    def downloaded(self) -> bool:
        """
        Whether the file for the given IPFS has was downloaded
        """
        if self._downloaded is None and self._from_fbs:
            self._downloaded = self._from_fbs.Downloaded()
        return self._downloaded

    @downloaded.setter
    def downloaded(self, value: bool):
        assert value is None or type(value) == bool
        self._downloaded = value

    @property
    def retries(self) -> int:
        """
        Number of retries to download the file from Infura
        """
        if self._retries is None and self._from_fbs:
            self._retries = self._from_fbs.Retries()
        return self._retries or 0

    @retries.setter
    def retries(self, value: int):
        assert value is None or type(value) == int
        self._retries = value

    @property
    def errored_at(self) -> np.datetime64:
        """
        Time of last time when downloaded errorred.
        """
        if self._errored_at is None and self._from_fbs:
            self._errored_at = np.datetime64(self._from_fbs.ErroredAt(), 'ns')
        return self._errored_at

    @errored_at.setter
    def errored_at(self, value: np.datetime64):
        assert value is None or isinstance(value, np.datetime64)
        self._errored_at = value

    @staticmethod
    def cast(buf):
        return IPFSFile(_IPFSFileGen.GetRootAsIPFSFile(buf, 0))

    def build(self, builder):
        file_hash = self.file_hash
        if file_hash:
            file_hash = builder.CreateString(file_hash)

        IPFSFileGen.IPFSFileStart(builder)

        if self.errored_at:
            IPFSFileGen.IPFSFileAddErroredAt(builder, int(self.errored_at))

        if self.retries:
            IPFSFileGen.IPFSFileAddRetries(builder, self.retries)

        if file_hash:
            IPFSFileGen.IPFSFileAddFileHash(builder, file_hash)

        IPFSFileGen.IPFSFileAddDownloaded(builder, self.downloaded or False)

        final = IPFSFileGen.IPFSFileEnd(builder)

        return final


@table('def3af4e-190c-4852-93da-731934deef90', build=IPFSFile.build, cast=IPFSFile.cast)
class IPFSFiles(MapStringFlatBuffers):
    """
    Persisted IPFS files download log

    Map :class:`zlmdb.MapStringFlatBuffers` from ``file_hash`` to :class:`cfxdb.xbrmm.IPFSFile`
    """
