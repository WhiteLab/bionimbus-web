import json

from channels.auth import channel_and_http_session

from tina.models import Library


def create_reply_message(success, context=None):
    context = context or dict()
    context.update({'success': bool(success)})
    return {'text': json.dumps(context)}


class CartWebSockets(object):
    @staticmethod
    def cart_add_success_message(libs_added_to_cart):
        # TODO Wow this is a messy function, and should it even live here?
        if len(libs_added_to_cart) == 1:
            return '{} was successfully added to your cart.'.format(
                Library.objects.get(pk=libs_added_to_cart[0]).name
            )
        elif len(libs_added_to_cart) == 2:
            return '{} and {} were successfully added to your cart.'.format(
                Library.objects.get(pk=libs_added_to_cart[0]).name,
                Library.objects.get(pk=libs_added_to_cart[1]).name
            )
        elif len(libs_added_to_cart) <= 5:
            return '{}, and {} were successfully added to your cart.'.format(
                ', '.join([lib.name for lib in Library.objects.filter(pk__in=libs_added_to_cart[:-1])]),
                Library.objects.get(pk=libs_added_to_cart[-1]).name
            )
        else:
            num_unnamed_libs = len(libs_added_to_cart) - 5
            return '{}, and {} other {} were successfully added to your cart.'.format(
                ', '.join([lib.name for lib in Library.objects.filter(pk__in=libs_added_to_cart[:5])]),
                str(num_unnamed_libs),
                'library' if num_unnamed_libs == 1 else 'libraries'
            )

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
        socket_message = json.loads(message['text'])
        # library_pk = socket_message['library_pks']
        # library_name = str(Library.objects.get(pk=library_pk))
        cart = message.http_session['cart']
        libs_added_to_cart = list()
        # TODO If socket_message['library_pks'] is of size 0
        for library_pk in socket_message['library_pks']:
            if library_pk not in cart:
                cart.append(library_pk)
                libs_added_to_cart.append(library_pk)

        if libs_added_to_cart:
            try:
                message.http_session.save()
                reply_message = create_reply_message(
                    success=True,
                    context={
                        'cartSize': len(message.http_session['cart']),
                        'action': 'toast',
                        'content': CartWebSockets.cart_add_success_message(libs_added_to_cart)
                    }
                )
            except Exception:
                reply_message = create_reply_message(
                    success=False,
                    context={
                        'action': 'toast',
                        'content': 'There was an error adding to your cart.'
                    }
                )
        else:
            if len(socket_message['library_pks']) > 1:
                toast_message = 'All of those libraries are already in your cart.'
            else:
                toast_message = 'The library {} is already in your cart.'.format(
                    Library.objects.get(pk=socket_message['library_pks'][0]).name
                )
            reply_message = create_reply_message(
                success=False,
                context={
                    'action': 'toast',
                    'content': toast_message
                }
            )

        # Send a reply message across the socket
        message.reply_channel.send(reply_message)




        # if library_pk not in cart:
        #     try:
        #         cart.append(library_pk)
        #         message.http_session.save()
        #
        #         reply_message = {
        #             'success': True,
        #             'cartSize': len(message.http_session['cart'])
        #         }
        #     except Exception:
        #         reply_message = {
        #             'success': False,
        #             'information': 'There was an error adding {} to your cart.'.format(library_name)
        #         }
        # else:
        #     reply_message = {
        #         'success': False,
        #         'information': 'The library {} is already in your cart.'.format(library_name)
        #     }
        # message.reply_channel.send({'text': json.dumps(reply_message)})


