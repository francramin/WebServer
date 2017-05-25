###########################################################################
# Concurrent server - webserver3g.py                                      #
#                                                                         #
# Tested with Python 2.7.9 & Python 3.4 on Ubuntu 14.04 & Mac OS X        #
###########################################################################
import errno
import os
import signal
import socket

SERVER_ADDRESS = (HOST, PORT) = '', 8888
REQUEST_QUEUE_SIZE = 1024


def grim_reaper(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(
                -1,  # Wait for any child process
                os.WNOHANG  # Do not block and return EWOULDBLOCK error
            )
        except OSError:
            return

        if pid == 0:  # no more zombies
            return


def handle_request(client_connection):
    request = client_connection.recv(1024)
    clientRequest = (request.split(' ', 1)[0])
    rootPath = "/home/francisco-ramos/Desktop/"
    clientPath = (request.split(' ')[1])[1:]
    http_response = "HTTP/1.1 200 OK\n" \
                    "Content-Type: text/html\n\n"

##############################GET###########################################

    if clientRequest == 'GET':
        if os.path.exists(rootPath + clientPath):
            if os.path.isfile(rootPath + clientPath):
                file = open(rootPath + clientPath)
                http_response += file.read()
            if os.path.isdir(rootPath + clientPath):
                http_response += "<html>\n" \
                                 "<body>\n" \
                                 "<h1>" + clientPath + "</h1>\n"
                for subPath in os.listdir(rootPath + clientPath):
                    http_response += "<p><a href= " + clientPath + "/" + subPath + ">" + subPath + "</a></p>\n"
                http_response += "</body>\n</html>"
        else:
            http_response += "<html>\n" \
                             "<body>\n" \
                             "<h1>404</h1>\n" \
                             "</body>\n" \
                             "</html>"

###############################PUT#########################################

    elif clientRequest == 'PUT':
        if os.path.exists(rootPath + clientPath):
            if os.path.isfile(rootPath + clientPath):
                file = open(rootPath + clientPath,"w")
                file.write(request.split("\n")[-1])#contenido del archivo
                http_response += "<html>\n" \
                                 "<body>\n" \
                                 "<h1>File created</h1>\n" \
                                 "</body>\n" \
                                 "</html>\n"
            if os.path.isdir(rootPath + clientPath):
                http_response += "<html>\n" \
                                 "<body>\n" \
                                 "<h1>Error: Can not create a directory</h1>\n" \
                                 "</body>\n" \
                                 "</html>\n"
        else:
            file = open(rootPath + clientPath, "w")
            file.write(request.split("\n")[-1])  # contenido del archivo
            http_response += "<html>\n" \
                             "<body>\n" \
                             "<h1>File created</h1>\n" \
                             "</body>\n" \
                             "</html>\n"
##############################POST###########################################

    elif clientRequest == 'POST':
        if os.path.exists(rootPath + clientPath):
            if os.path.isfile(rootPath + clientPath):
                file = open(rootPath + clientPath)
                http_response += file.read()
            if os.path.isdir(rootPath + clientPath):
                http_response += "<html>\n" \
                                 "<body>\n" \
                                 "<h1>" + clientPath + "</h1>\n"
                for subPath in os.listdir(rootPath + clientPath):
                    http_response += "<p><a href= " + clientPath + "/" + subPath + ">" + subPath + "</a></p>\n"
                http_response += "</body>\n</html>\n"
        else:
            http_response += "<html>\n" \
                             "<body>\n" \
                             "<h1>404</h1>\n" \
                             "</body>\n" \
                             "</html>\n"

##############################DELETE###########################################

    elif clientRequest == 'DELETE':
        if os.path.exists(rootPath + clientPath):
            if os.path.isfile(rootPath + clientPath):
                os.remove(rootPath + clientPath)
                http_response += "<html>\n" \
                                 "<body>\n" \
                                 "<h1>File Deleted</h1>\n" \
                                 "</body>\n" \
                                 "</html>\n"
            if os.path.isdir(rootPath + clientPath):
                http_response += "<html>\n" \
                                 "<body>\n" \
                                 "<h1>Error: Can not delete directory</h1>\n" \
                                 "</body>\n" \
                                 "</html>\n"
        else:
            http_response += "<html>\n" \
                             "<body>\n" \
                             "<h1>404</h1>\n" \
                             "</body>\n" \
                             "</html>\n"

##############################HEAD###########################################

    elif clientRequest == 'HEAD':
        http_response = "HTTP/1.1 200 OK\n"
    print(request.decode())
    client_connection.sendall(http_response)
    


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))
    signal.signal(signal.SIGCHLD, grim_reaper)
    while True:
        try:
            client_connection, client_address = listen_socket.accept()
        except IOError as e:
            code, msg = e.args
            # restart 'accept' if it was interrupted
            if code == errno.EINTR:
                continue
            else:
                raise
        pid = os.fork()
        if pid == 0:  # child
            listen_socket.close()  # close child copy
            handle_request(client_connection)
            client_connection.close()
            os._exit(0)
        else:  # parent
            client_connection.close()  # close parent copy and loop over


if __name__ == '__main__':
    serve_forever()