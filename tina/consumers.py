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
        print('received message from client: {}'.format(message['text']))
        socket_message = json.loads(message['text'])
        cart = message.http_session['cart']

        reply_success = True
        reply_context = {
            'action': 'toast',
            'content': ''
        }

        # Filter out all lib pk that don't exist
        lib_pks_that_exist = [
            pk
            for pk in socket_message['library_pks']
            if Library.objects.filter(pk=pk).exists()
        ]
        already_in_cart = set(cart).intersection(set(lib_pks_that_exist))
        need_to_add = set(lib_pks_that_exist).difference(set(cart))

        added = list()
        if need_to_add:
            for lib_pk in need_to_add:
                try:
                    cart.append(lib_pk)
                    added.append(lib_pk)
                except Exception as e:
                    reply_context['content'] = 'There was an error adding some libraries to your cart.\n'
                    continue  # Send detailed error log to admin email

            # If any libraries were added, this was a success so update cart size
            if added:
                reply_context['content'] += CartWebSockets.cart_add_success_message(added)
                reply_context['cartSize'] = len(message.http_session['cart'])
            else:
                reply_success = False

        # If all libraries are already in the cart
        else:
            reply_success = False
            if not lib_pks_that_exist:
                reply_context['content'] = 'Could not add libraries to cart because they do not exist.'
            elif len(already_in_cart) > 1:
                reply_context['content'] = 'All of those libraries are already in your cart.'
            elif len(already_in_cart) == 1:
                reply_context['content'] = 'The library {} is already in your cart.'.format(
                    Library.objects.get(pk=socket_message['library_pks'][0]).name
                )

        message.http_session.save()
        message.reply_channel.send(create_reply_message(
            success=reply_success,
            context=reply_context
        ))
