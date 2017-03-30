# -*- coding: utf-8 -*-

import weakref
import threading
import contextlib
import collections


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
    """Publish/Subscriber pattern.

    Implementacion minima de patron publish/subscriber.

    Se utilizan referencias debiles a las instancias suscritas.
    Esto implica que la "desuscripcion" es automatica cuando las instancias
    se queden sin referencias.
    Esto permite no tener cuclos de referencias entre objetos y liberar de la
    labor de "accounting" al codigo cliente e implementar peligrosos "__del__".
    """
    def __init__(self):
        self._locker = ReadWriteLock()
        self._channels = collections.defaultdict(weakref.WeakKeyDictionary)

    def subscribe(self, method, topic):
        """Suscripcion a un 'topic'.

        "method": metodo de una instancia.
            Tiene que ser un metodo "normal.
            i.e.: No puede ser "lambda", "staticmethod", ni "classmethod".

        "topic": string. "topic" a suscribirse.
        """
        with self._locker.write_lock():
            self._channels[topic][method.__self__] = method.__name__

    def unsubscribe(self, method, topic):
        """Suscripcion a un 'topic'.

        "method": metodo de una instancia previamente suscrita.

        "topic": string. "topic".
        """
        with self._locker.write_lock():
            if topic in self._channels:
                del self._channels[topic][method.__self__]

    def publish(self, topic, data=None):
        """Publicacion de un "topic".

        "topic": string. Nombre del "topic".

        "data": object. Por defecto None.
            Argumentos a pasar a cada metodo de cada instancia subscrita a "topic".

        El orden de invocacion de los suscriptores es arbitrario y no se debe
        depender del mismo.

        Durante la recepcion del mensaje no se puede realizar invocar a
        "subscribe" ni "unsubscribe". Si se hace, se producira un deadlock.
        """
        with self._locker.read_lock():
            slot = self._channels[topic]
            for obj in slot:
                getattr(obj, slot[obj])(topic, data)

    # def dumper(self):
    #     foo = self._channels
    #     for item in foo:
    #         print(item, foo[item], len(foo[item]))


__manager = PubSub()

subscribe = __manager.subscribe
unsubscribe = __manager.unsubscribe
publish = __manager.publish
