from gd.typing import Any, Dict, Iterable, LevelCollection, List, Optional, Tuple, Union

from gd.utils import search_utils as search
from gd.utils.text_tools import dumps, make_repr
from gd.utils.xml_parser import XMLParser

from gd.api.struct import LevelAPI
from gd.api.utils import get_default

__all__ = ("Part", "Database", "LevelCollection")


class Part(dict):
    def __init__(
        self, stream: str = Union[bytes, str], default: Optional[Dict[str, Any]] = None
    ) -> None:
        self.parser = XMLParser()

        if isinstance(stream, str):
            stream = stream.encode()

        try:
            loaded = self.parser.load(stream)

        except Exception:
            if default is None:
                default = {}

            loaded = default

        super().__init__(loaded)

    def __str__(self) -> str:
        return dumps(self, indent=4)

    def __repr__(self) -> str:
        info = {"outer_len": len(self)}
        return make_repr(self, info)

    def dump(self) -> str:
        """Dump the part and return a string."""
        return self.parser.dump(self)


class Database:
    def __init__(self, main: str = "", levels: str = "") -> None:
        self.main = Part(main, get_default("main"))
        self.levels = Part(levels, get_default("levels"))

    def __repr__(self) -> str:
        info = {"main": repr(self.main), "levels": repr(self.levels)}
        return make_repr(self, info)

    def __json__(self) -> Dict[str, Any]:
        return {"main": self.main, "levels": self.levels}

    def get_username(self) -> str:
        return self.main.get("GJA_001", "unknown")

    def get_password(self) -> str:
        return self.main.get("GJA_002", "unknown")

    def get_account_id(self) -> int:
        return self.main.get("GJA_003", 0)

    def get_player_id(self) -> int:
        return self.main.get("playerUserID", 0)

    def get_udid(self) -> str:
        return self.main.get("playerUDID", "S0")

    def get_bootup_amount(self) -> int:
        return self.main.get("bootups", 0)

    def _get_failsafe(self, key: str, is_level_part: bool = True, default: Any = None) -> Any:
        part = self.levels if is_level_part else self.main

        if default is None:
            default = {}

        if key not in part:
            part[key] = default

        return part[key]

    def _to_levels(self, level_dicts: List[Dict[str, Any]]) -> LevelCollection:
        return LevelCollection.launch(
            self,
            map(LevelAPI.from_mapping, filter(lambda thing: isinstance(thing, dict), level_dicts)),
        )

    def load_saved_levels(self, *, key: str = "GLM_03") -> LevelCollection:
        """Load "Saved Levels" into :class:`.api.LevelCollection`."""
        inner = self._get_failsafe(key, is_level_part=False)
        return self._to_levels(inner.values())

    def dump_saved_levels(self, levels: LevelCollection, *, key: str = "GLM_03") -> None:
        """Dump "Saved Levels" from :class:`.api.LevelCollection`."""
        self.main[key] = {str(level.id): level.to_map() for level in levels}

    def load_my_levels(self, *, key: str = "LLM_01") -> LevelCollection:
        """Load "My Levels" into :class:`.api.LevelCollection`."""
        inner = self._get_failsafe(key)
        return self._to_levels(inner.values())

    def dump_my_levels(self, levels: list, *, key: str = "LLM_01", prefix: str = "k_") -> None:
        """Dump "My Levels" from :class:`.api.LevelCollection`."""
        stuff = {"_isArr": True}
        stuff.update({prefix + str(n): level.to_map() for n, level in enumerate(levels)})
        self.levels[key] = stuff

    def dump(self) -> None:
        from gd.api.loader import save  # I hate circular imports. - nekit

        save.dump(self)

    def as_tuple(self) -> Tuple[Part, Part]:
        return (self.main, self.levels)


class LevelCollection(list):
    def __init__(self, *args) -> None:
        if len(args) == 1:
            args = args[0]
        super().__init__(args)
        self._callback = None

    def __repr__(self) -> str:
        return self.__class__.__name__ + super().__repr__()

    def get_by_name(self, name: str) -> Optional[LevelAPI]:
        return search.get(self, name=name)

    @classmethod
    def launch(cls, caller: Any, iterable: Iterable) -> LevelCollection:
        self = cls(iterable)
        self._callback = caller
        return self

    def _conf_api(self, api: Database) -> Optional[Database]:
        if api is None:
            return self._callback
        return api

    def dump(self, api: Optional[Database] = None) -> None:
        api = self._conf_api(api)
        api.dump_my_levels(self)

    def dump_to_saved(self, api: Optional[Database] = None) -> None:
        api = self._conf_api(api)
        api.dump_saved_levels(self)
