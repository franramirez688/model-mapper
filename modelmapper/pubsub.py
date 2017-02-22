# -*- coding: utf-8 -*-

import threading
import contextlib


class ReadWriteLock:
    """A lock object that allows many simultaneous read locks, but only one write lock."""

    # Basado en:
    #   https://github.com/launchdarkly/python-client/blob/master/ldclient/rwlock.py

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def rlock(self):
        """ Acquire a read lock. Blocks only if a thread has
        acquired the write lock. """
        with self._read_ready:
            self._readers += 1

    def runlock(self):
        """ Release a read lock. """
        with self._read_ready:
            self._readers -= 1
            if not self._readers:
                self._read_ready.notifyAll()

    def lock(self):
        """ Acquire a write lock. Blocks until there are no
        acquired read or write locks. """
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def unlock(self):
        """ Release a write lock. """
        self._read_ready.release()

    @contextlib.contextmanager
    def read_lock(self):
        self.rlock()
        try:
            yield None
        finally:
            self.runlock()

    @contextlib.contextmanager
    def write_lock(self):
        self.lock()
        try:
            yield None
        finally:
            self.unlock()


class PubSub(object):
    def __init__(self):
        self.locker = ReadWriteLock()
        self.channels = dict()

    def subscribe(self, method, topic):
        with self.locker.write_lock():
            try:
                channel = self.channels[topic]
            except KeyError:
                channel = self.channels[topic] = set()
            channel.add(method)

    def unsubscribe(self, method, topic):
        with self.locker.write_lock():
            if topic in self.channels:
                self.channels[topic].remove(method)

    def publish(self, topic, data=None):
        with self.locker.read_lock():
            for client in self.channels[topic]:
                client(topic, data)


__manager = PubSub()

subscribe = __manager.subscribe
unsubscribe = __manager.unsubscribe
publish = __manager.publish


if __name__ == '__main__':
    pass
