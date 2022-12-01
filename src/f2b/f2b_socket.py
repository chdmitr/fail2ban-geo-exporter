import socket
from pickle import dumps, loads, HIGHEST_PROTOCOL


CSPROTO = {
    "EMPTY": b"",
    "END": b"<F2B_END_COMMAND>",
    "CLOSE": b"<F2B_CLOSE_COMMAND>"
}


class F2BSocket:
    def __init__(self, sock_path, timeout=-1):
        self.__csock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__deftout = self.__csock.gettimeout()
        if timeout != -1:
            self.set_timeout(timeout)
        self.__csock.connect(sock_path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def send(self, msg, nonblocking=False, timeout=None):
        obj = dumps(msg, HIGHEST_PROTOCOL)
        self.__csock.send(obj)
        self.__csock.send(CSPROTO['END'])
        return self.receive(self.__csock, nonblocking, timeout)

    def set_timeout(self, timeout):
        self.__csock.set_timeout(timeout if timeout != -1 else self.__deftout)

    def close(self):
        if not self.__csock:
            return
        try:
            self.__csock.sendall(CSPROTO['CLOSE'] + CSPROTO['END'])
            self.__csock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        try:
            self.__csock.close()
        except socket.error:
            pass
        self.__csock = None

    def receive(self, sock_path, nonblocking=False, timeout=None):
        msg = CSPROTO['EMPTY']
        if nonblocking:
            sock_path.setblocking(0)
        if timeout:
            sock_path.set_timeout(timeout)
        bufsize = 1024
        while msg.rfind(CSPROTO['END'], -32) == -1:
            chunk = sock_path.recv(bufsize)
            if not len(chunk):
                raise socket.error(104, 'Connection reset by peer')
            if chunk == CSPROTO['END']:
                break
            msg = msg + chunk
            if bufsize < 32768:
                bufsize <<= 1
        return loads(msg)
