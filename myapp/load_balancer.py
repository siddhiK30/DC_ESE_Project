class RoundRobinLoadBalancer:
    """
    A simple round-robin load balancer for distributing requests across multiple RPC servers.
    """
    
    def __init__(self, servers=None):
        """
        Initialize the load balancer with a list of server addresses.
        
        Args:
            servers (list): List of server addresses (strings) to balance load across
        """
        self.servers = servers or []
        self.current_index = 0
        self.active_servers = {server: True for server in self.servers}
    
    def get_next_server(self):
        """
        Get the next available server using round-robin algorithm.
        
        Returns:
            str: Server address or None if no servers are available
        """
        if not self.servers:
            return None
            
        # Count active servers
        active_count = sum(1 for server in self.servers if self.active_servers.get(server, False))
        if active_count == 0:
            return None
            
        # Find next active server
        for _ in range(len(self.servers)):
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            
            if self.active_servers.get(server, False):
                return server
                
        return None
    
    def mark_server_down(self, server):
        """Mark a server as inactive."""
        if server in self.active_servers:
            self.active_servers[server] = False
    
    def mark_server_up(self, server):
        """Mark a server as active."""
        if server in self.active_servers:
            self.active_servers[server] = True