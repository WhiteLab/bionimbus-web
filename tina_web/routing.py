from channels.routing import route, include
from tina.consumers import CartWebSockets


cart_routing = [
    route('websocket.connect', CartWebSockets.connect),
    route('websocket.receive', CartWebSockets.receive)
]

channel_routing = [
    include(cart_routing, path=r'^/cart')
]