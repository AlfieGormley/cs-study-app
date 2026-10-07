import socket, ssl

host = "www.rfc-editor.org"
ctx = ssl.create_default_context()

with socket.create_connection(
        (host, 443), timeout=10) as raw:
    with ctx.wrap_socket(
            raw, server_hostname=host) as tls:
        print(tls.version())
        print(tls.cipher()[0])
        cert = tls.getpeercert()
        subject = dict(
            x[0] for x in cert["subject"])
        print(subject)
