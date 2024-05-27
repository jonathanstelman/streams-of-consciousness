from enum import Enum

class Distributor(Enum):
    """Supported distributors"""
    CD_BABY = 'cd_baby'
    DISTRO_KID = 'distrokid'

class Transaction(Enum):
    """Supported transaction types"""
    STREAM = 'stream'
    DOWNLOAD = 'download'
    ROYALTY = 'royalty'
    YOUTUBE_AUDIO = 'youtube_audio_tier'
