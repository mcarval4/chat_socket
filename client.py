import sys
import threading
import Pyro4
import Pyro4.socketutil


if sys.version_info < (3, 0):
    input = raw_input()


# O processo está rodando seu próprio thread, para lidar com o servidor
# com as mensagens de retorno enquanto o thread principal está processando
# as mensagens de entrada dos usuários.
class Chatter(object):
    def __init__(self):
        self.chatbox = Pyro4.core.Proxy('PYRONAME:chatbox')
        self.abort = 0

    @Pyro4.expose
    @Pyro4.oneway

    # Formato de print da mensagem
    def message(self, nick, msg):
        if nick != self.nick:
            print('[{0}] {1}'.format(nick, msg))

    def pv_message(self, nick, msg, obj):
        if nick != self.nick:
            print('[{0}] {1}'.format(nick, msg))


    # Inicia o processo do chat após o login/cadastramento do usuário
    def start(self):
        nicks = self.chatbox.getNicks()
        if nicks:
            print('Os seguintes usuários estão no servidor: %s' % (', '.join(nicks)))
        channels = sorted(self.chatbox.getChannels())
        if channels:
            print('Os seguintes canais já existem: %s' % (', '.join(channels)))
            self.channel = input('Escolha um canal ou crie um novo: ').strip()
        else:
            print('O servidor não possui canais ativos.')
            self.channel = input('Nome para o novo canal: ').strip()
        self.nick = input('Escolha um apelido: ').strip()
        people = self.chatbox.join(self.channel, self.nick, self)
        print('Entrou no canal %s como %s' % (self.channel, self.nick))
        print('Pessoas no canal: %s' % (', '.join(people)))
        print('Pronto para mensagens! Digite /quit para sair')
        try:
            try:
                while not self.abort:
                    line = input('> ').strip()
                    if line == '/quit':
                        break
                    # if line == line.startswith('#%s' % self.nick):
                    #     self.chatbox.private_publish(self.nick, line)
                    if line:
                        self.chatbox.publish(self.channel, self.nick, line)
            except EOFError:
                pass
        finally:
            self.chatbox.leave(self.channel, self.nick)
            self.abort = 1
            self._pyroDaemon.shutdown()


# Cria o processo rodando em segundo plano
class DaemonThread(threading.Thread):
    def __init__(self, chatter):
        threading.Thread.__init__(self)
        self.chatter = chatter
        self.setDaemon(True)

    def run(self):
        with Pyro4.core.Daemon() as daemon:
            daemon.register(self.chatter)
            daemon.requestLoop(lambda: not self.chatter.abort)


chatter = Chatter()
daemonthread = DaemonThread(chatter)
daemonthread.start()
chatter.start()
print('Exit.')
