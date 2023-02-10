#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Cenab Batu Bora https://github.com/cenab
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

PORT = 80 #default port

CONTENT_TYPE = "application/x-www-form-urlencoded"
#USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
#https://user-agents.net/string/mozilla-5-0-x11-ubuntu-linux-x86-64-rv-96-0-gecko-20100101-firefox-96-0
USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def parse_url(self,url):
        #https://stackoverflow.com/questions/50499273/urlparse-fails-with-simple-url
        try:
            #parse the url and check with failsafe
            if not re.search(r'^[A-Za-z0-9+.\-]+://', url):
                url = 'http://{0}'.format(url)
            url_netloc = urllib.parse.urlparse(url).netloc
            #domain or ip address
            if ":" in url_netloc:
                host = url_netloc.split(":")[0]
                port = int(url_netloc.split(":")[1])
            else:
                host = socket.gethostbyname(url_netloc)
                port = PORT
            return host, port, urllib.parse.urlparse(url)
        except:
            return None, None, None

    def connect(self, host, port):
        # establish a socket connection and connect to the host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_status = self.socket.connect((host, port))
        return socket_status

    def get_code(self, data):
        try:
            code = int(data.split()[1])
        except:
            code = None
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        try:
            return data.split("\r\n")[-1]
        except:
            return ""
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, url_parsed = self.parse_url(url)
        path = url_parsed.path

        if host == None:
            return HTTPResponse(404, None)
        elif port == None:
            return HTTPResponse(404, None)

        if self.connect(host, port) == 0:
            raise Exception('Ehem ehem, socket failed to connect! Probably there is problem with the way the user is running.')


        if path == "": path = "/"

        query = url_parsed.query

        if args != None:
            #args is a dictionary
            for arg in args:
                if query == "": query += str(arg) + "=" + str(args[arg])
                else: query += "&" + str(arg) + "=" + str(args[arg])

        if query != "": query = "?" + query

        headers = ""
        headers += "HTTP/1.1\r\n"
        headers += "Host: {}\r\n".format(url_parsed.netloc)
        headers += "Accept: */*\r\n"
        headers += "User-Agent: {}\r\n".format(USER_AGENT)
        headers += "Connection: close\r\n"

        self.sendall("GET {} {}\r\n".format(path + query, headers))
        data = self.recvall(self.socket)

        self.close()

        print("Data for the request:\n", data, "\n**********************************************************")
        body = self.get_body(data)
        code = self.get_code(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, url_parsed = self.parse_url(url)
        path = url_parsed.path

        if host == None:
            return HTTPResponse(404, None)
        elif port == None:
            return HTTPResponse(404, None)

        if self.connect(host, port) == 0:
            raise Exception('Ehem ehem, socket failed to connect! Probably there is problem with the way the user is running.')
        
        if path == "": path = "/"

        post_data = ""

        if args != None:
            for arg in args:
                if post_data == "": post_data += str(arg) + "=" + str(args[arg])
                else: post_data += "&" + str(arg) + "=" + str(args[arg])

        headers = ""
        headers += "HTTP/1.1\r\n"
        headers += "Host: {}\r\n".format(url_parsed.netloc)
        headers += "Accept: */*\r\n"
        headers += "Content-Type: {}\r\n".format(CONTENT_TYPE)
        headers += "Content-Length: {}\r\n".format(len(post_data.encode('utf-8')))
        headers += "User-Agent: {}\r\n".format(USER_AGENT)
        headers += "Connection: close\r\n"

        self.sendall("POST {} {}\r\n{}".format(path, headers, post_data))
        data = self.recvall(self.socket)

        self.close()

        print("Data for the request:\n", data, "\n**********************************************************")
        body = self.get_body(data)
        code = self.get_code(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
