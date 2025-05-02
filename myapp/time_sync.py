import json
import datetime
import random
import time
from django.core.cache import cache
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class BerkeleyClock:
    """
    Implementation of Berkeley Clock Algorithm for time synchronization
    between clients in the guestbook application.
    """
    
    @staticmethod
    def get_current_time():
        """Returns the current datetime with microsecond precision"""
        return datetime.datetime.now()
    
    @staticmethod
    def get_time_offset():
        """
        Simulates slight time differences between clients
        Returns a random time offset between -2 and 2 seconds
        """
        return random.uniform(-2, 2)
    
    @classmethod
    def get_local_time(cls, user_id):
        """
        Get the local time for a specific user, applying their stored offset
        """
        # Get the user's offset from cache or default to a new random one
        offset_key = f"time_offset_{user_id}"
        offset = cache.get(offset_key)
        
        if offset is None:
            offset = cls.get_time_offset()
            cache.set(offset_key, offset, 3600)  # Store for 1 hour
            
        # Return current time adjusted by the user's offset
        return cls.get_current_time() + datetime.timedelta(seconds=offset)
    
    @classmethod
    def synchronize(cls, coordinator_id, participant_ids):
        """
        Implements the Berkeley algorithm to synchronize clocks
        
        Args:
            coordinator_id: User ID of the coordinator (sender)
            participant_ids: List of User IDs for participants (recipients)
            
        Returns:
            Synchronized timestamp for the guestbook entry
        """
        # 1. Coordinator sends its time to all participants
        coordinator_time = cls.get_local_time(coordinator_id)
        
        # 2. Each participant calculates the time difference and sends back
        time_diffs = []
        for participant_id in participant_ids:
            participant_time = cls.get_local_time(participant_id)
            diff = (participant_time - coordinator_time).total_seconds()
            time_diffs.append(diff)
            
        # 3. Coordinator averages all time differences
        if not time_diffs:
            return coordinator_time  # No participants, use coordinator time
            
        avg_diff = sum(time_diffs) / (len(time_diffs) + 1)  # +1 to include coordinator
        
        # 4. Calculate the synchronized time
        synchronized_time = coordinator_time + datetime.timedelta(seconds=avg_diff)
        
        # 5. Log the synchronization results for debugging
        logger.debug(f"Clock sync: coordinator={coordinator_id}, participants={participant_ids}")
        logger.debug(f"Time differences: {time_diffs}")
        logger.debug(f"Average diff: {avg_diff}")
        logger.debug(f"Synchronized time: {synchronized_time}")
        
        return synchronized_time


class RPCHandler:
    """
    Handles Remote Procedure Calls between clients in the guestbook application.
    """
    
    @staticmethod
    def call(method, params=None, user_id=None):
        """
        Simulates an RPC call to a remote method
        
        Args:
            method: Name of the method to call
            params: Parameters to pass to the method
            user_id: ID of the user making the call
            
        Returns:
            Result of the RPC call
        """
        if params is None:
            params = {}
            
        # Add caller identification
        if user_id:
            params['caller_id'] = user_id
            
        # Simulate network latency
        time.sleep(random.uniform(0.1, 0.3))
        
        # Handle different RPC methods
        if method == 'get_local_time':
            return BerkeleyClock.get_local_time(params.get('user_id'))
            
        elif method == 'synchronize_time':
            return BerkeleyClock.synchronize(
                params.get('coordinator_id'),
                params.get('participant_ids', [])
            )
            
        elif method == 'create_guestbook_entry':
            # This would actually create the entry in a real RPC implementation
            # Here we just return success to simulate the operation
            return {
                'success': True,
                'entry_id': random.randint(1000, 9999),
                'synchronized_time': params.get('synchronized_time').isoformat()
            }
            
        else:
            raise ValueError(f"Unknown RPC method: {method}")