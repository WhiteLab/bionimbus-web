import json

from channels.auth import channel_and_http_session

from .models import Library


class CartWebSockets(object):
    @staticmethod
    @channel_and_http_session
    def connect(message):
        print('made connection with client')
        message.reply_channel.send({'accept': True})

    @staticmethod
    @channel_and_http_session
    def receive(message):
        """
        When modifying http session, note that a new session can't be created from here. So that
        probably means I need to ensure a blank session exists the moment the user interacts with Tina.
        """
        print('received message from client')
        msg_content = json.loads(message['text'])
        library_pk = int(msg_content['library_pk'])
        library_name = str(Library.objects.get(pk=library_pk))
        cart = message.http_session['cart']
        if library_pk not in cart:
            try:
                cart.append(library_pk)
                message.http_session.save()

                reply_message = {
                    'success': True,
                    'cartSize': len(message.http_session['cart'])
                }
            except Exception:
                reply_message = {
                    'success': False,
                    'information': 'There was an error adding {} to your cart.'.format(library_name)
                }
        else:
            reply_message = {
                'success': False,
                'information': 'The library {} is already in your cart.'.format(library_name)
            }
        message.reply_channel.send({'text': json.dumps(reply_message)})


