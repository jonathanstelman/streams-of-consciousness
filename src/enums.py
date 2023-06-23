from enum import Enum

class Distributor(Enum):
    CD_BABY = 'cd_baby'
    DISTRO_KID = 'distro_kid'

class Transaction(Enum):
    STREAM = 'stream'
    DOWNLOAD = 'download'
    ROYALTY = 'royalty'
    YOUTUBE_AUDIO = 'youtube_audio_tier'
