import pytest


def sync_signal(source: str, *, number: int):
    emit = yield
    return emit(source, number)


async def async_signal(source: str, *, number: int):
    emit = yield
    await emit(source, number)


@pytest.fixture
def sig():
    from signalbus import create_signal

    return create_signal(sync_signal)


@pytest.fixture
def asig():
    from signalbus import create_signal

    return create_signal(async_signal)


def test_create_signal(sig, asig):
    from signalbus import Signal, AsyncSignal

    assert isinstance(sig, Signal)
    assert isinstance(asig, AsyncSignal)


def test_register_signal(sig):
    @sig.register
    def cb1(source: str, number: int):
        ...

    @sig.register("cart")
    def cb2(source: str, number: int):
        ...

    assert len(sig._callbacks) == 2
    assert sig._callbacks == [(cb1, ()), (cb2, ("cart",))]


def test_unregister_signal(sig):
    @sig.register
    def cb1(source: str, number: int):
        ...

    @sig.register("cart")
    def cb2(source: str, number: int):
        ...

    sig.unregister(cb1)
    assert sig._callbacks == [(cb2, ("cart",))]


def test_sync_signal(sig):
    signals = []

    @sig.register
    def cb1(source: str, number: int):
        signals.append(("cb1", source, number))

    @sig.register("cart")
    def cb2(source: str, number: int):
        signals.append(("cb2", source, number))

    sig("user", number=24)
    sig("cart", number=42)

    assert signals == [
        ("cb1", "user", 24),
        ("cb1", "cart", 42),
        ("cb2", "cart", 42),
    ]


async def test_async_signal(asig):
    signals = []

    @asig.register
    async def cb1(source: str, number: int):
        signals.append(("cb1", source, number))

    @asig.register("cart")
    async def cb2(source: str, number: int):
        signals.append(("cb2", source, number))

    await asig("user", number=24)
    await asig("cart", number=42)

    assert signals == [
        ("cb1", "user", 24),
        ("cb1", "cart", 42),
        ("cb2", "cart", 42),
    ]
