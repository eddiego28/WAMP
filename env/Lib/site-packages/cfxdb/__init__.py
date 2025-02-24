###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

# monkey patch eth_abi for master branch (which we need for python 3.11)
# https://github.com/ethereum/eth-abi/blob/master/docs/release_notes.rst#breaking-changes
# https://github.com/ethereum/eth-abi/pull/161
# ImportError: cannot import name 'encode_single' from 'eth_abi' (/home/oberstet/cpy311_2/lib/python3.11/site-packages/eth_abi/__init__.py)
import eth_abi
if not hasattr(eth_abi, 'encode_abi') and hasattr(eth_abi, 'encode'):
    eth_abi.encode_abi = eth_abi.encode
if not hasattr(eth_abi, 'encode_single') and hasattr(eth_abi, 'encode'):
    eth_abi.encode_single = eth_abi.encode

# monkey patch web3 for master branch / upcoming v6 (which we need for python 3.11)
# AttributeError: type object 'Web3' has no attribute 'toChecksumAddress'. Did you mean: 'to_checksum_address'?
import web3
if not hasattr(web3.Web3, 'toChecksumAddress') and hasattr(web3.Web3, 'to_checksum_address'):
    web3.Web3.toChecksumAddress = web3.Web3.to_checksum_address
if not hasattr(web3.Web3, 'isConnected') and hasattr(web3.Web3, 'is_connected'):
    web3.Web3.isConnected = web3.Web3.is_connected
if not hasattr(web3.Web3, 'toBytes') and hasattr(web3.Web3, 'to_bytes'):
    web3.Web3.toBytes = web3.Web3.to_bytes
if not hasattr(web3.Web3, 'toInt') and hasattr(web3.Web3, 'to_int'):
    web3.Web3.toInt = web3.Web3.to_int

import txaio

txaio.use_twisted()

from ._version import __version__  # noqa
from ._exception import InvalidConfigException  # noqa
from .common import address  # noqa
from .common import uint256, unpack_uint256, pack_uint256  # noqa
from .common import uint128, unpack_uint128, pack_uint128  # noqa
from .common import uint64, unpack_uint64, pack_uint64  # noqa
from . import meta, mrealm, xbr, xbrmm, xbrnetwork  # noqa
from . import globalschema, mrealmschema, cookiestore, realmstore  # noqa

__all__ = (
    '__version__',
    'meta',
    'mrealm',
    'cookiestore',
    'realmstore',
    'xbr',
    'xbrmm',
    'xbrnetwork',
    'address',
    'uint256',
    'pack_uint256',
    'unpack_uint256',
    'uint128',
    'pack_uint128',
    'unpack_uint128',
    'uint64',
    'pack_uint64',
    'unpack_uint64',
    'globalschema',
    'mrealmschema',
    'InvalidConfigException',
)
