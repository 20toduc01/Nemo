import re

def emote_request(message):
    '''
    Returns the emote name if a message is an emote request, None otherwise
    '''
    msg = message.content
    print(msg)
    if msg.startswith(':') and msg.find(' ') == -1 and not msg.endswith('>'):
        if msg.endswith(':'):
            return msg[1:-1]
        else:
            return msg[1:]
    return None


def emotes_from_message(message):
    '''
    Return a list of emotes from a message.
    '''
    custom_emotes = re.findall(r'<:\w*:\d*>', message.content)
    name = [e.split(':')[1] for e in custom_emotes]
    id = [e.split(':')[2].replace('>', '') for e in custom_emotes]
    return name, id


def animated_emotes_from_message(message):
    '''
    Return a list of animated emotes from a message.
    '''
    custom_emotes = re.findall(r'<a:\w*:\d*>', message.content)
    name = [e.split(':')[1] for e in custom_emotes]
    id = [e.split(':')[2].replace('>', '') for e in custom_emotes]
    return name, id