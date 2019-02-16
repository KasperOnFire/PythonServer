import socket
import os
import datetime
from email.utils import formatdate

PORT = 8888


def run_server():
    for i in range(3):
        server_socket = create_socket(PORT)
        log_action("Listening on port: " + str(PORT))
        try:
            connecting_socket, addr = server_socket.accept()
            connecting_ip = ":".join(str(entry) for entry in addr)
            log_action(
                "Accepted incoming socket connection from " + connecting_ip)
            data = connecting_socket.recv(1024)
            # parse request and determine response
            request_line, request_headers = parse_request(
                data.decode())
            status_code, response_data = get_response_data(
                request_line.split(" ")[1].strip())
            # Log format for incoming requests:
            # ip user-id user [datetime] "requestline" responsecode responsesize
            log_action(" ".join([connecting_ip, "[" + get_current_date() + "]", "\""+str(
                request_line) + "\"", status_code.split(" ")[0], str(get_content_length(response_data))]))
            response_body = build_response(status_code, response_data)
            # send response
            connecting_socket.send(response_body.encode())
        finally:
            connecting_socket.close()
            server_socket.close()
            log_action("Closed connection to client.")


def create_socket(socket_port):
    """Create socket connection on given port and return it"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # to be able to reuse socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", socket_port))
    server_socket.listen(1)
    return server_socket


def parse_request(request_data):
    """ Parse an incoming HTTP Request and return request line and request headers"""
    # Trim whitespace and split on newline
    lines = [line.strip() for line in request_data.split('\n')]
    # Initialize values for request for handling
    request_line = lines[0]
    request_method, request_path, request_http_version = [
        word for word in request_line.split(" ")]
    request_body = lines[1:]
    request_headers = {}
    # Build dictionary of headers and values, exclude last 2 lines (empty)
    for header in request_body[:-2]:
        # Split only on first colon - user-agent can have colons in value
        content = header.split(':', 1)
        request_headers[content[0]] = content[1].strip()
    return request_line, request_headers


def get_response_data(request_path):
    """Return content of a requested file and status code 200 if it exists, otherwise return default data and 404 status code."""
    status_code = content = ""
    path = request_path[:1]
    fname = request_path[1:]
    # if asking for root, give index.html
    if path is "/" and len(fname) is 0:
        with open("index.html", "r") as requested_file:
            for line in requested_file.readlines():
                content += line
        status_code = "200 OK"
    # if asking for specific file, return contents if exists.
    # this handles exceptions for file not found, since this is a basic boolean check
    elif fname in os.listdir("."):
        with open(request_path[1:], "r") as requested_file:
            for line in requested_file.readlines():
                content += line
        status_code = "200 OK"
    else:
        content = "<h1>404 Not Found</h1>"
        status_code = "404 Not Found"
    return status_code, content


def build_response(status_code, response_data):
    """Build a valid HTTP response with the given status code containing the given data."""
    http_version = "HTTP/1.1"
    response_line = " ".join([http_version, status_code])
    # Build response headers - add more here if needed/for details
    response_headers = {}
    response_headers["Date"] = get_current_date()
    response_headers["Server"] = "ServerOnFire.py"
    response_headers["Content-Length"] = get_content_length(response_data)
    # Build lines with correct endings
    response_headers = "\r\n".join(["%s: %s" % kv
                                    for kv in response_headers.items()]) + "\r\n"
    response = "\r\n".join(
        [response_line, response_headers, response_data])
    return response


def get_current_date():
    """Return string current date in HTTP format, eg: Sun, 06 Nov 1994 22:34:04 +0100."""
    return formatdate(timeval=None, localtime=True)


def get_content_length(content):
    """Return an int containing the length of the input in bytes."""
    return len(content.encode("utf-8"))


def log_action(data, should_print=True):
    """ Add an action to the logfile and print it to the console, unless otherwise specificed."""
    with open("test.log", "a+") as log:
        line = str(datetime.datetime.now()) + " " + data+"\n"
        log.write(line)
        print(line)


if __name__ == "__main__":
    run_server()
