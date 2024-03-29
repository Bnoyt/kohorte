# -*- coding: utf-8 -*-

import os
import sys
import socket
import select
import threading
import time
from timeit import default_timer as timer
from app.models import Noeud


from app.com.config import SERVER_PORT

class Main(threading.Thread):

    server_address = './com_socket'

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.clients = []
        self.infos = {}

    def run(self, *args, **kwargs):
        #define running code here
#        try:
#            os.unlink(Main.server_address)
#        except OSError:
#            if os.path.exists(Main.server_address):
#                raise
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', SERVER_PORT))
        sock.listen(5)
        while True:
            #print('    Thread %s is well and alive' % self.name)
            #Establish  connection with clients
            queries, wlist, xlist = select.select([sock], [], [], 0.05)
            for link in queries:
                client, infos = link.accept()
                if infos[0] == '127.0.0.1':
                    self.clients.append(client)
                    self.infos[client] = infos
                    print('Accepted connexion from %s on %s' % infos)
                else:
                    print('Rejected connection from %s on %s' % infos)
                    client.close()

            #Read from connected clients
            try:
                to_read, wlist, xlist = select.select(self.clients, [], [], 0.05)
            except select.error:
                #time.sleep(3)
                pass
            else:
                try:
                    for client in to_read:
                        print('Receinving from client %s on %s' % self.infos[client])
                        start_time = timer()
                        msg = client.recv(1024)
                        while msg:
                            print('    <%s>' % (msg.decode()))
                            msg = client.recv(1024)
                        end_time = timer()
                        print('Done with client %s on %s' % self.infos[client])
                        print('Done in %s' % (end_time - start_time))
                        #print('Sending close connection message ...'    )
                        #client.send(b'close')
                        strIds = ''.join([str(noeud.id) + '\n' for noeud in Noeud.objects.all()])
                        print("The nodes are :\n" + strIds)
                finally:
                    for client in to_read:
                        print('Closing connexion with %s on %s' % self.infos[client])
                        self.clients.remove(client)
                        del self.infos[client]
                        client.close()
        pass