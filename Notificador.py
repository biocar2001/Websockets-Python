# -*- coding: utf-8 -*-
from tornado import web, ioloop, websocket
import json
import logging

from sockjs.tornado import SockJSRouter, SockJSConnection

################################################################################################
#     Class: EchoConnection                                                                    #
#     Parameters: SockJSConnection                                                             #
#     Description: Class for tetsing messages received in   SockJS                             #
#                                                                                              #
################################################################################################
class EchoConnection(SockJSConnection):
    def on_message(self, msg):
        self.send(msg)

################################################################################################
#     Class: NotificacionesConnection                                                          #
#     Parameters: SockJSConnection                                                             #
#     Description: Class for opening sockects in HTML 5 with diferents clients
#                                                                                              #
################################################################################################
class NotificacionesConnection(SockJSConnection):
    clientConnenected = {}
    clientConnenectedSub = {}
    _connected = set()
    logging.getLogger().setLevel(logging.DEBUG)

    # Operaciones a realizar cuando se abre una conexion de un socket:
    # Log de usuario conectado
    # Añadimos el objeto socket del nuevo usuario conectado a un set para controlar los usuarios conectados
    def on_open(self, request):
        self._connected.add(self)
        logging.info("User Connected")

    # Operaciones a realizar cuando se recibe un mensaje de un socket, ya sea browser o python_
    # Si es un browser: El indicador 'tip' es distinto de 1, se trata de la llamada que se hace por un usuario desde el navegador,
    #                   almacenamos la conexion del usuario con su idUser, quedando a la espera de notificaciones para ese idUser
    # Si es un cliente python u otro proceso: El indicador 'tip' es 1, se trata de una llamada con contenido JSON y por tanto hecha desde un proceso Python u otro cleinte
    def on_message(self, data):
        data = json.loads(data)
        tip = data["tip"]          #Origen del mensaje (Browser or Python)
        logging.info("Tip User: %r ", tip)
        #flag = 0
        # Si es 1, se trata de una llamada con contenido JSON y por tanto hecha desde un proceso Python
        if tip == '1':
            '''print "USUARIOS CONECTADOS -- CONEXION TIPO 1 "
            for k1 in self.clientConnenected.keys():
                flag = flag +1
                logging.info("number: %r ", flag)
                logging.info("k1 value: %r ", k1)'''

            nameJ = data['name']        #user
            logging.info("User Json para el usuario: %r recibido", nameJ)
            messageJ = data['message']  #content
            logging.info("Message Json: %r ", messageJ)
            enviar = 0
            #Buscamos dentro de todos los usuario conectados al socket por user para enviarle el mensaje que hemos recibido
            for k1 in self.clientConnenected.keys():
                logging.info("k1 value: %r ", k1)
                if(enviar >0):
                   logging.info("NOTIFICACION FUE ENVIADA")
                   break
                for user, client in self.clientConnenected[k1].iteritems():
                    logging.info("USER value: %r ", user)
                    logging.info("CLIENT value: %r ", client)
                    # Si el user coincide le enviamos el JSON a este socket indicandole que es un JSON a parsear
                    if user == nameJ:
                        logging.info("User Json para el usuario: %r recibido y encontrado, listo para enviar informacion al cliente", nameJ)
                        try:
                            respuesta = {
                                "clave": 'json',
                                "message": json.dumps(messageJ),
                            }
                            k1.send(json.dumps(respuesta))
                            logging.info("Session with Json Enviado JSON: %r", k1)
                            logging.info("User Json Enviado JSON: %r", user)
                            logging.info("Message Json Enviado JSON: %r", messageJ)
                            enviar = 1
                            break

                        except:
                            logging.error("Error sending message", exc_info=True)

        #Si es distinto de 1, se trata de la llamada que se hace por un usuario desde el navegador, almacenamos la conexion del usuario con su idUser, quedando a la espera de notificaciones
        else:
            nameC = data['name']        #user
            messageC = data['message']  #content
            #flag2 = 0
            #almacenamos la conexion del usuario con su idUser, quedando a la espera de notificaciones
            self.clientConnenectedSub = dict()
            self.clientConnenectedSub[nameC] = self
            self.clientConnenected[self] = self.clientConnenectedSub
            '''print "USUARIOS CONECTADOS -- CONEXION TIPO 0 "
            for k1 in self.clientConnenected.keys():
                flag2 = flag2 +1
                logging.info("number: %r ", flag2)
                logging.info("k1 value: %r ", k1)'''
            logging.info("Websocket client with User : %r Conectado a Websocket", nameC)
            #respondemos al navegador indicandole que es un cliente y por tanto no debe hacer nada en la respuesta
            respuesta = {
                "clave": 'client',
                "message": json.dumps(messageC),
            }
            self.send(json.dumps(respuesta))

    # Operaciones a realizar cuando se cierra una conexion de un socket
    def on_close(self):
        logging.info("Llegamos al on_close")
        #User websockect desconectado, listo para ser eliminado del diccionario de socket abiertos
        for k1 in self.clientConnenected.keys():
                for user, client in self.clientConnenected[k1].iteritems():
                    if self == client:
                        self.clientConnenected.pop(k1)
                        logging.info("Websocket client with User : %r Eliminado", user)
                        break
        self._connected.remove(self)
        '''flag3 = 0
        print "USUARIOS CONECTADOS -- POST ELIMINAR "
        for k1 in self.clientConnenected.keys():
                flag3 = flag3 +1
                logging.info("number: %r ", flag3)
                logging.info("k1 value: %r ", k1)'''
#Metodo necesario para arrancar el servidor tornado y cargar nuestra clase gestora de sockets
if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    EchoRouter = SockJSRouter(EchoConnection, '/echo4',
                            user_settings=dict(response_limit=4096))
   
    TickerRouter = SockJSRouter(NotificacionesConnection, '/echo')
    print EchoRouter.urls

    app = web.Application(EchoRouter.urls +
                          TickerRouter.urls
                          )

    app.listen(9999)
    logging.info(" [*] Listening on 0.0.0.0:9999")
    ioloop.IOLoop.instance().start()