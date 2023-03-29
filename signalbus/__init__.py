from __future__ import annotations

from inspect import isasyncgenfunction, isgeneratorfunction
from logging import INFO, getLogger
from typing import TYPE_CHECKING, Any, Generic, List, overload, Tuple
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from typing import AsyncGenerator, Callable, Generator

logger = getLogger("signals")
logger.setLevel(INFO)

P = ParamSpec("P")


class BaseSignal(Generic[P]):
    __slots__ = ("_callbacks", "_genfn", "_name")

    def __init__(self, genfn: Callable[P, Any]):
        self._name = genfn.__name__
        self._genfn = genfn
        self._callbacks: List[Tuple[Callable[P, Any], Tuple]] = []

    def register(self, *args) -> Callable[[Callable[P, Any]], Any]:
        if args and callable(args[0]):
            self._callbacks.append((args[0], args[1:]))
            return args[0]

        def wrapper(callback: Callable[P, Any]):
            self._callbacks.append((callback, args))
            return callback

        return wrapper

    def unregister(self, callback: Callable):
        self._callbacks = [(cb, args) for cb, args in self._callbacks if cb != callback]

    def __filter__(self, *call_args) -> Generator[Callable[P, Any], None, None]:
        for cb, cb_args in self._callbacks:
            if not cb_args or cb_args == call_args[: len(cb_args)]:
                yield cb


class Signal(BaseSignal[P]):
    __slots__ = ("_callbacks", "_genfn")

    def __init__(self, genfn: Callable[P, Generator]):
        assert isgeneratorfunction(genfn), "Signal must be a generator function"
        super().__init__(genfn)

    def __emit__(self, *args: P.args, **kwargs: P.kwargs):
        logger.debug("Emitting signal '%s' with args %r", self._name, args)
        return [cb(*args, **kwargs) for cb in self.__filter__(*args)]

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        gen = self._genfn(*args, **kwargs)
        gen.send(None)
        try:
            gen.send(self.__emit__)
        except StopIteration as exc:
            return exc.value
        finally:
            gen.close()

        raise RuntimeError("Invalid signal function")


class AsyncSignal(BaseSignal[P]):
    def __init__(self, genfn: Callable[P, AsyncGenerator]):
        assert isasyncgenfunction(genfn), "Signal must be a generator function"
        super().__init__(genfn)

    async def __emit__(self, *args: P.args, **kwargs: P.kwargs):
        logger.debug("Emitting signal '%s' with args %r", self._name, args)
        return [await cb(*args, **kwargs) for cb in self.__filter__(*args)]

    async def __call__(self, *args: P.args, **kwargs: P.kwargs):
        gen = self._genfn(*args, **kwargs)
        await gen.asend(None)
        try:
            await gen.asend(self.__emit__)
        except StopAsyncIteration:
            return
        finally:
            await gen.aclose()

        raise RuntimeError("Invalid signal function")


@overload
def create_signal(fn: Callable[P, Generator]) -> Signal[P]:
    ...


@overload
def create_signal(fn: Callable[P, AsyncGenerator]) -> AsyncSignal[P]:
    ...


def create_signal(fn):
    if isasyncgenfunction(fn):
        return AsyncSignal(fn)

    if isgeneratorfunction(fn):
        return Signal(fn)

    raise TypeError("Signal must be a generator function")


__all__ = ["create_signal", "Signal", "AsyncSignal"]
