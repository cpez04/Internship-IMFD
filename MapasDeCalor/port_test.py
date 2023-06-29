import socket

def test_port(host, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a timeout for the connection attempt
        sock.settimeout(2)
        
        # Attempt to connect to the host and port
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print(f"Port {port} is open on {host}")
        else:
            print(f"Port {port} is blocked on {host}")
        
        # Close the socket connection
        sock.close()
    except socket.error as e:
        print(f"Error while testing port {port}: {str(e)}")

# Example usage: Test port 80 on localhost
test_port("s02.imfd.cl", 201)
