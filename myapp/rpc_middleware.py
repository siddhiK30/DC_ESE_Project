import json
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RPCMiddleware(MiddlewareMixin):
    """
    Middleware to handle RPC requests to the guestbook application.
    """
    
    def process_request(self, request):
        """
        Process incoming RPC requests identified by /api/rpc/ path
        """
        if request.path.startswith('/api/rpc/'):
            return self.handle_rpc_request(request)
        return None
    
    def handle_rpc_request(self, request):
        """
        Handle RPC requests by parsing the JSON-RPC format
        """
        if request.method != 'POST':
            return JsonResponse({
                'error': 'Method not allowed. Use POST for RPC calls.',
                'code': 405
            }, status=405)
            
        try:
            # Parse JSON-RPC request
            rpc_data = json.loads(request.body)
            
            # Validate JSON-RPC format
            if 'method' not in rpc_data:
                return JsonResponse({
                    'error': 'Invalid RPC request. Missing "method" parameter.',
                    'code': 400
                }, status=400)
                
            # Extract RPC parameters
            method = rpc_data.get('method')
            params = rpc_data.get('params', {})
            request_id = rpc_data.get('id')
            
            logger.debug(f"RPC request: method={method}, params={params}")
            
            # Handle the RPC method
            from .time_sync import RPCHandler
            
            result = RPCHandler.call(
                method=method,
                params=params,
                user_id=request.user.id if request.user.is_authenticated else None
            )
            
            # Return JSON-RPC response
            response = {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }
            
            return JsonResponse(response)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON in request body.',
                'code': 400
            }, status=400)
            
        except Exception as e:
            logger.exception(f"Error processing RPC request: {str(e)}")
            return JsonResponse({
                'error': str(e),
                'code': 500
            }, status=500)