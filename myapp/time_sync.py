# import json
# import datetime
# import random
# import time
# from django.core.cache import cache
# from django.contrib.auth.models import User
# import logging

# logger = logging.getLogger(__name__)

# class BerkeleyClock:
#     """
#     Implementation of Berkeley Clock Algorithm for time synchronization
#     between clients in the guestbook application.
#     """
    
#     @staticmethod
#     def get_current_time():
#         """Returns the current datetime with microsecond precision"""
#         return datetime.datetime.now()
    
#     @staticmethod
#     def get_time_offset():
#         """
#         Simulates slight time differences between clients
#         Returns a random time offset between -2 and 2 seconds
#         """
#         return random.uniform(-2, 2)
    
#     @classmethod
#     def get_local_time(cls, user_id):
#         """
#         Get the local time for a specific user, applying their stored offset
#         """
#         # Get the user's offset from cache or default to a new random one
#         offset_key = f"time_offset_{user_id}"
#         offset = cache.get(offset_key)
        
#         if offset is None:
#             offset = cls.get_time_offset()
#             cache.set(offset_key, offset, 3600)  # Store for 1 hour
            
#         # Return current time adjusted by the user's offset
#         return cls.get_current_time() + datetime.timedelta(seconds=offset)
    
#     @classmethod
#     def synchronize(cls, coordinator_id, participant_ids):
#         """
#         Implements the Berkeley algorithm to synchronize clocks
        
#         Args:
#             coordinator_id: User ID of the coordinator (sender)
#             participant_ids: List of User IDs for participants (recipients)
            
#         Returns:
#             Synchronized timestamp for the guestbook entry
#         """
#         # 1. Coordinator sends its time to all participants
#         coordinator_time = cls.get_local_time(coordinator_id)
        
#         # 2. Each participant calculates the time difference and sends back
#         time_diffs = []
#         for participant_id in participant_ids:
#             participant_time = cls.get_local_time(participant_id)
#             diff = (participant_time - coordinator_time).total_seconds()
#             time_diffs.append(diff)
            
#         # 3. Coordinator averages all time differences
#         if not time_diffs:
#             return coordinator_time  # No participants, use coordinator time
            
#         avg_diff = sum(time_diffs) / (len(time_diffs) + 1)  # +1 to include coordinator
        
#         # 4. Calculate the synchronized time
#         synchronized_time = coordinator_time + datetime.timedelta(seconds=avg_diff)
        
#         # 5. Log the synchronization results for debugging
#         logger.debug(f"Clock sync: coordinator={coordinator_id}, participants={participant_ids}")
#         logger.debug(f"Time differences: {time_diffs}")
#         logger.debug(f"Average diff: {avg_diff}")
#         logger.debug(f"Synchronized time: {synchronized_time}")
        
#         return synchronized_time


# class RPCHandler:
#     """
#     Handles Remote Procedure Calls between clients in the guestbook application.
#     """
    
#     @staticmethod
#     def call(method, params=None, user_id=None):
#         """
#         Simulates an RPC call to a remote method
        
#         Args:
#             method: Name of the method to call
#             params: Parameters to pass to the method
#             user_id: ID of the user making the call
            
#         Returns:
#             Result of the RPC call
#         """
#         if params is None:
#             params = {}
            
#         # Add caller identification
#         if user_id:
#             params['caller_id'] = user_id
            
#         # Simulate network latency
#         time.sleep(random.uniform(0.1, 0.3))
        
#         # Handle different RPC methods
#         if method == 'get_local_time':
#             return BerkeleyClock.get_local_time(params.get('user_id'))
            
#         elif method == 'synchronize_time':
#             return BerkeleyClock.synchronize(
#                 params.get('coordinator_id'),
#                 params.get('participant_ids', [])
#             )
            
#         elif method == 'create_guestbook_entry':
#             # This would actually create the entry in a real RPC implementation
#             # Here we just return success to simulate the operation
#             return {
#                 'success': True,
#                 'entry_id': random.randint(1000, 9999),
#                 'synchronized_time': params.get('synchronized_time').isoformat()
#             }
            
#         else:

#             raise ValueError(f"Unknown RPC method: {method}")
from django.utils import timezone
from datetime import datetime, timedelta
import requests
import logging
import time
import random
from django.conf import settings

from .load_balancer import RoundRobinLoadBalancer

logger = logging.getLogger(__name__)

class BerkeleyClock:
    """
    Implementation of the Berkeley Clock Algorithm for time synchronization
    """
    
    @staticmethod
    def synchronize_times(coordinator_time, participant_times):
        """
        Synchronize times using Berkeley Clock algorithm
        
        Args:
            coordinator_time: Timestamp of the coordinator
            participant_times: Dictionary of participant IDs to their local times
            
        Returns:
            synchronized_time: The calculated synchronized time
        """
        if not participant_times:
            return coordinator_time
            
        # Calculate time differences from coordinator
        time_diffs = {}
        for participant_id, participant_time in participant_times.items():
            if participant_time:
                # Calculate difference in seconds
                diff = (participant_time - coordinator_time).total_seconds()
                time_diffs[participant_id] = diff
        
        # If no valid differences, return coordinator's time
        if not time_diffs:
            return coordinator_time
            
        # Calculate average time difference
        avg_diff = sum(time_diffs.values()) / len(time_diffs)
        
        # Adjust coordinator's time by average difference
        synchronized_time = coordinator_time + timedelta(seconds=avg_diff)
        
        return synchronized_time


class RPCHandler:
    """
    Handles Remote Procedure Calls with load balancing
    """
    # Initialize the load balancer with default RPC servers
    _load_balancer = None
    
    @classmethod
    def get_load_balancer(cls):
        """Get or initialize the load balancer"""
        if cls._load_balancer is None:
            # Get RPC servers from settings or use default
            rpc_servers = getattr(settings, 'RPC_SERVERS', ['http://localhost:8001/rpc'])
            cls._load_balancer = RoundRobinLoadBalancer(rpc_servers)
        return cls._load_balancer
    
    @classmethod
    def call(cls, method, params=None, user_id=None, max_retries=3):
        """
        Make an RPC call to a service using round-robin load balancing
        
        Args:
            method: RPC method name
            params: Parameters for the method
            user_id: ID of the requesting user
            max_retries: Maximum number of retry attempts
            
        Returns:
            The result of the RPC call
        """
        params = params or {}
        if user_id:
            params['user_id'] = user_id
            
        load_balancer = cls.get_load_balancer()
        retries = 0
        last_error = None
        
        while retries < max_retries:
            # Get next available server using round-robin
            server = load_balancer.get_next_server()
            if not server:
                logger.error("No available RPC servers")
                raise Exception("No available RPC servers")
                
            try:
                logger.debug(f"Making RPC call to {server}: {method}")
                
                payload = {
                    'jsonrpc': '2.0',
                    'method': method,
                    'params': params,
                    'id': str(time.time())
                }
                
                # Make the actual RPC call
                response = requests.post(
                    server,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=(3.0, 10.0)  # (connect timeout, read timeout)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'error' in result:
                        logger.warning(f"RPC error: {result['error']}")
                        raise Exception(f"RPC error: {result['error']}")
                    return cls._process_result(method, result.get('result'))
                else:
                    # Mark server as down if it returns an error
                    logger.warning(f"RPC server {server} returned status {response.status_code}")
                    load_balancer.mark_server_down(server)
                    
            except requests.RequestException as e:
                # Mark server as down if connection fails
                logger.warning(f"RPC request to {server} failed: {e}")
                load_balancer.mark_server_down(server)
                last_error = e
                
            # Add exponential backoff before retrying
            wait_time = (2 ** retries) + random.uniform(0.1, 0.5)
            time.sleep(wait_time)
            retries += 1
            
        # If we've exhausted retries, raise the last error
        logger.error(f"RPC call failed after {max_retries} retries")
        if last_error:
            raise last_error
        raise Exception(f"RPC call to {method} failed after {max_retries} retries")
    
    @staticmethod
    def _process_result(method, result):
        """Process the result based on the method called"""
        if method == 'get_local_time' and result:
            # Convert string timestamp to datetime object
            if isinstance(result, str):
                try:
                    return datetime.fromisoformat(result)
                except ValueError:
                    pass
        
        if method == 'synchronize_time' and result:
            # Convert string timestamp to datetime object
            if isinstance(result, str):
                try:
                    return datetime.fromisoformat(result)
                except ValueError:
                    pass
                    
        return result