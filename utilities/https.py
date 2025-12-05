# HTTPS helper for Interstate 75 W
# The Pimoroni requests module doesn't support HTTPS, so we use raw sockets

import socket
import ssl
import json


def decode_chunked(data):
    """
    Decode HTTP chunked transfer encoding.

    Chunked format:
    <chunk-size-in-hex>\r\n
    <chunk-data>\r\n
    ...
    0\r\n
    \r\n
    """
    result = []
    pos = 0

    while pos < len(data):
        # Find the end of the chunk size line
        line_end = data.find("\r\n", pos)
        if line_end == -1:
            break

        # Parse chunk size (hex)
        try:
            chunk_size = int(data[pos:line_end].strip(), 16)
        except ValueError:
            break

        if chunk_size == 0:
            # End of chunks
            break

        # Extract chunk data
        chunk_start = line_end + 2
        chunk_end = chunk_start + chunk_size

        if chunk_end > len(data):
            # Incomplete chunk, take what we have
            result.append(data[chunk_start:])
            break

        result.append(data[chunk_start:chunk_end])

        # Move past chunk data and trailing \r\n
        pos = chunk_end + 2

    return "".join(result)


def https_get(host, path, timeout=10):
    """
    Make an HTTPS GET request and return the response body.

    Args:
        host: Hostname (e.g., "api.example.com")
        path: URL path (e.g., "/api/data")
        timeout: Socket timeout in seconds

    Returns:
        Response body as string, or None on error
    """
    s = None
    ss = None

    try:
        # Create socket and connect
        s = socket.socket()
        s.settimeout(timeout)
        addr = socket.getaddrinfo(host, 443)[0][-1]
        s.connect(addr)

        # Wrap with SSL - include server_hostname for SNI (Server Name Indication)
        # This is required for many modern servers to complete TLS handshake
        ss = ssl.wrap_socket(s, server_hostname=host)

        # Send HTTP request with browser-like headers
        # Must match what FR24 library uses to avoid 403
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36\r\n"
            "Accept: application/json\r\n"
            "Accept-Encoding: identity\r\n"
            "Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7\r\n"
            "Cache-Control: no-cache\r\n"
            "Origin: https://www.flightradar24.com\r\n"
            "Referer: https://www.flightradar24.com/\r\n"
            "Sec-Fetch-Dest: empty\r\n"
            "Sec-Fetch-Mode: cors\r\n"
            "Sec-Fetch-Site: same-site\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        ss.write(request.encode())

        # Read response
        response = b""
        while True:
            chunk = ss.read(1024)
            if not chunk:
                break
            response += chunk

        # Parse response
        response = response.decode('utf-8')

        # Split headers and body
        if "\r\n\r\n" in response:
            headers, body = response.split("\r\n\r\n", 1)
        else:
            return None

        # Check for redirect
        if "301" in headers or "302" in headers:
            for line in headers.split("\r\n"):
                if line.lower().startswith("location:"):
                    new_path = line.split(":", 1)[1].strip()
                    # Handle relative redirects
                    if new_path.startswith("/"):
                        ss.close()
                        s.close()
                        return https_get(host, new_path, timeout)
                    # Handle absolute redirects
                    elif new_path.startswith("https://"):
                        new_url = new_path[8:]  # Remove https://
                        new_host = new_url.split("/")[0]
                        new_path = "/" + "/".join(new_url.split("/")[1:])
                        ss.close()
                        s.close()
                        return https_get(new_host, new_path, timeout)

        # Check status code
        status_line = headers.split("\r\n")[0]
        if "200" not in status_line:
            print(f"HTTP error: {status_line}")
            return None

        # Check for chunked transfer encoding
        is_chunked = "transfer-encoding: chunked" in headers.lower()
        if is_chunked:
            body = decode_chunked(body)

        return body

    except Exception as e:
        print(f"HTTPS error: {e}")
        return None

    finally:
        if ss:
            try:
                ss.close()
            except:
                pass
        if s:
            try:
                s.close()
            except:
                pass


def https_get_json(host, path, timeout=10):
    """
    Make an HTTPS GET request and return parsed JSON.

    Args:
        host: Hostname
        path: URL path
        timeout: Socket timeout

    Returns:
        Parsed JSON as dict/list, or None on error
    """
    body = https_get(host, path, timeout)
    if body:
        try:
            # Strip whitespace and find the JSON object/array bounds
            body = body.strip()
            # Find the actual JSON end (last } or ])
            if body.startswith('{'):
                end_idx = body.rfind('}')
                if end_idx != -1:
                    body = body[:end_idx + 1]
            elif body.startswith('['):
                end_idx = body.rfind(']')
                if end_idx != -1:
                    body = body[:end_idx + 1]
            return json.loads(body)
        except Exception as e:
            # Show first/last chars to help debug truncation
            preview = body[:100] if len(body) > 100 else body
            end = body[-50:] if len(body) > 50 else ""
            print(f"JSON parse error: {e}")
            print(f"  Body length: {len(body)}, starts: {preview[:50]}...")
            if end:
                print(f"  ends: ...{end}")
    return None


def http_get(host, path, timeout=10):
    """
    Make a plain HTTP (non-SSL) GET request and return the response body.

    Args:
        host: Hostname (e.g., "api.example.com")
        path: URL path (e.g., "/api/data")
        timeout: Socket timeout in seconds

    Returns:
        Response body as string, or None on error
    """
    s = None

    try:
        # Create socket and connect (port 80 for HTTP)
        s = socket.socket()
        s.settimeout(timeout)
        addr = socket.getaddrinfo(host, 80)[0][-1]
        s.connect(addr)

        # Send HTTP request
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "User-Agent: FlightTracker/1.0\r\n"
            "Accept: application/json\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        s.send(request.encode())

        # Read response
        response = b""
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            response += chunk

        # Parse response
        response = response.decode('utf-8')

        # Split headers and body
        if "\r\n\r\n" in response:
            headers, body = response.split("\r\n\r\n", 1)
        else:
            return None

        # Check for redirect
        status_line = headers.split("\r\n")[0]
        if "301" in status_line or "302" in status_line:
            for line in headers.split("\r\n"):
                if line.lower().startswith("location:"):
                    new_url = line.split(":", 1)[1].strip()
                    s.close()
                    # If redirected to HTTPS, use https_get instead
                    if new_url.startswith("https://"):
                        new_url = new_url[8:]  # Remove https://
                        new_host = new_url.split("/")[0]
                        new_path = "/" + "/".join(new_url.split("/")[1:]) if "/" in new_url else "/"
                        print(f"Following redirect to HTTPS: {new_host}{new_path}")
                        return https_get(new_host, new_path, timeout)
                    # If redirected to HTTP, follow it
                    elif new_url.startswith("http://"):
                        new_url = new_url[7:]  # Remove http://
                        new_host = new_url.split("/")[0]
                        new_path = "/" + "/".join(new_url.split("/")[1:]) if "/" in new_url else "/"
                        return http_get(new_host, new_path, timeout)
                    # Relative redirect
                    elif new_url.startswith("/"):
                        return http_get(host, new_url, timeout)
            print(f"HTTP redirect but no location header")
            return None

        # Check status code
        if "200" not in status_line:
            print(f"HTTP error: {status_line}")
            return None

        # Check for chunked transfer encoding
        is_chunked = "transfer-encoding: chunked" in headers.lower()
        if is_chunked:
            body = decode_chunked(body)

        return body

    except Exception as e:
        print(f"HTTP error: {e}")
        return None

    finally:
        if s:
            try:
                s.close()
            except:
                pass


def http_get_json(host, path, timeout=10):
    """
    Make a plain HTTP GET request and return parsed JSON.

    Args:
        host: Hostname
        path: URL path
        timeout: Socket timeout

    Returns:
        Parsed JSON as dict/list, or None on error
    """
    body = http_get(host, path, timeout)
    if body:
        try:
            return json.loads(body)
        except Exception as e:
            print(f"JSON parse error: {e}")
    return None
