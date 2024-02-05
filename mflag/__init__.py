__version__ = "1.7.1"

from mflag.src.flag import Flag, JobManager
from mflag.src.rcmng.server import run as RMServer
from mflag.src.rcmng.client import Client as RMClient
from mflag.src.rcmng.submit import Submit as RMSubmit
from mflag.src.lock import LockManager
