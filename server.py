import re

import Pyro4

# Administração de servidor de chat.
# Trata logins, logouts, canais e apelidos, 

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ChatBox(object):
    def __init__(self):
        self.channels = {} # canais registrados {canal --> (apelido, client callback) lista}
        self.nicks = []  # todos apelidos registrados

    def getChannels(self):
        return list(self.channels.keys())

    def getNicks(self):
        self.nicks

    # Função para criar um novo canal ou apelido
    def join(self, channel, nick, callback):
        if not channel or not nick:
            raise ValueError("canal ou apelido inválido")
        if nick in self.nicks:
            raise ValueError('esse apelido já está em uso')
        if channel not in self.channels:
            print('CRIANDO UM NOVO CANAL %s' % channel)
            self.channels[channel] = []
        self.channels[channel].append((nick, callback))
        self.nicks.append(nick)
        print("%s ENTROU %s" % (nick, channel))
        self.publish(channel, 'SERVIDOR', '** ' + nick + ' entrou **')
        return [nick for (nick, c) in self.channels[channel]]  # retorna todos os apelidos do canal

    # Função para saída do usuário e para limpar a lista com os usuários que saíram
    def leave(self, channel, nick):
        if channel not in self.channels:
            print('CANAL DESCONHECIDO IGNORADO %s' % channel)
            return
        for (n, c) in self.channels[channel]:
            if n == nick:
                self.channels[channel].remove((n, c))
                break
        self.publish(channel, 'SERVIDOR', '** ' + nick + ' saiu **')
        if len(self.channels[channel]) < 1:
            del self.channels[channel]
            print('CANAL REMOVIDO %s' % channel)
        self.nicks.remove(nick)
        print("%s SAIU %s" % (nick, channel))


    # Função para publicar as mensagens e remover canais ociosos
    def publish(self, channel, nick, msg):
        if channel not in self.channels:
            print('CANAL DESCONHECIDO IGNORADO %s' % channel)
            return

        match = re.match("^\#(\w+)\s(.+)", msg)

        for (n, c) in self.channels[channel][:]:
            # print(self.channels[channel][1])
            # print(getNicks())
            print("n -> %s\n c -> %s" % (n, c))

            try:
                if match == None:
                    c.message(nick, msg)  # oneway call
                elif match.group(1) == n:
                    print("Tentando mandar msg privada de {} para {}".format(nick, n))
                    m = "Privado de {}: {}".format(nick, match.group(2))
                    c.message(nick, m)  # oneway call

            except Pyro4.errors.ConnectionClosedError:
                # queda de conexão, remove o listener se ainda houver
                # checa a existência porque outra thread por ter finalizado.
                if (n, c) in self.channels[channel]:
                    self.channels[channel].remove((n, c))
                    print('Dead listener removidos %s %s' % (n, c))

    # Função para enviar as mensagens privadas para os usuários
    def private_publish(self, nick, msg):
        if nick not in self.nicks:
            print('USUÁRIO DESCONHECIDO IGNORADO %s' % nick)
            return
        for (n, c) in self.nicks[nick][:]:
            try:
                c_split = c.split()
                print(c_split[6][:57])
                uri_string = c_split[6][:57]
                c.pv_message(nick, msg, uri_string)
            except Pyro4.errors.ConnectionClosedError:
                if (n, c) in self.nicks[nick]:
                    self.nicks[nick].remove((n, c))
                    print('Dead listener removidos %s %s' % (n, c))
                    

Pyro4.Daemon.serveSimple(
    {
        ChatBox: "chatbox"
    },
    ns=True
)
