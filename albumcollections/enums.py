import enum


class albumcollectionsEnum(enum.Enum):
    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class MusicType(albumcollectionsEnum):
    track = 0
    album = 1


class RoundStatus(albumcollectionsEnum):
    submit = 0
    listen = 1
    revealed = 2


class SnoozinRecType(albumcollectionsEnum):
    random = 0
    similar = 1
