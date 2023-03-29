# Signalbus

Simple and small library to broadcast signals with typing support

[![Tests Status](https://github.com/klen/signalbus/workflows/tests/badge.svg)](https://github.com/klen/signalbus/actions)

Features:

* Async support
* Full typing support (get errors)
* Small (around 100 lines of code) and fast
* You may incapsulate some logic inside a signal

## Why another library?

Other signals library don't have a good typing support.

## Installation

    $ pip install signalbus

## Usage

```python

from signalbus import create_signal

# Create a signals
# Just define a (generator) function and wrap it with `signalbus.create_signal`

@create_signal
def order_changed(order_status: str, *, order_id: int):  # 
    """
    The function contains the signal code.
    Feel free to do some operations before and after the sending.

    Pay attention to the function's params
    All receivers for the signal have to be able to accept the same params.
    Typing libraries will show you errors.
    """
    # first, you have to get `emit` to be able to send the signal
    emit = yield   

    # then send the signal to the receivers (you may want to skip it in some cases)
    res: list = emit(order_status, order_id=order_id)

    # you may check the results, do some additional work, etc


# Register a receiver for the signal
# The receiver has to have the same params (types will be checked)
@order_changed.register
def notify_user(order_status: str, *, order_id: int):
    ...


@order_changed.register
def update_stats(order_status: str, *, order_id: int):
    ...


# To send the signal just call it like a function with all required params
order_changed('done', order_id=42)

```


### Async Signals

Everything is almost the same except async/await

```python

from signalbus import create_signal

@create_signal
async def order_changed(order_status: str, *, order_id: int):
    emit = yield
    res: list = await emit(order_status, order_id=order_id)


# Receiver has to be async too
@order_changed.register
async def notify_user(order_status: str, *, order_id: int):
    ...


@order_changed.register
async def update_stats(order_status: str, *, order_id: int):
    ...


# Do not forget to await the signal
await order_changed('done', order_id=42)
```

### Filter signals by arguments

You may set any arguments to filter a receiver with the register function. The
receiver would be called only when corresponding arguments match.

Let's consider the following example:

```python
from signalbus import create_signal

@create_signal
async def order_changed(order_status: str, *, order_id: int):
    emit = yield
    res: list = await emit(order_status, order_id=order_id)


# pay attention to that we define an attribute in register
@order_changed.register('done')
async def notify_user(order_status: str, *, order_id: int):
    ...


@order_changed.register
async def update_stats(order_status: str, *, order_id: int):
    ...


await order_changed('done', order_id=42)  # both the receivers above will be called
await order_changed('cancel', order_id=42)  # only update stats will be called
```


### Mypy support

For better typing with mypy, you have to set correct returning type for your signals:
```python
from signalbus import create_signal

from typing import Generator, AsyncGenerator

@create_signal
def sync_signal() -> Generator:
    emit = yield
    res: list = await emit()


@create_signal
async def async_signal() -> AsyncGenerator:
    emit = yield
    res: list = await emit()
```

No need to do it with Pyright, because the Pyright calculates the types correctly

## Bug tracker

If you have any suggestions, bug reports or annoyances please report them to
the issue tracker at https://github.com/klen/signalbus/issues


## Contributing

Development of The Knocker happens at: https://github.com/klen/signalbus


##  License

Licensed under a [MIT license](https://opensource.org/license/mit/)
