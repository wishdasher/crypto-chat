from message import Message
import base64
from time import sleep
from threading import Thread
from Crypto.Cipher import AES
from Crypto.Signature import PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto import Random
from base64 import b64encode
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA

TYPE_KEY = 1
TYPE_MESSAGE = 2
NAME_LEN = 32
SIG_LEN = 128
ALL = "A"

class Conversation:
    '''
    Represents a conversation between participants
    '''
    def __init__(self, c_id, manager):
        '''
        Constructor
        :param c_id: ID of the conversation (integer)
        :param manager: instance of the ChatManager class
        :return: None
        '''
        self.id = c_id  # ID of the conversation
        self.all_messages = []  # all retrieved messages of the conversation
        self.printed_messages = []
        self.last_processed_msg_id = 0  # ID of the last processed message
        from chat_manager import ChatManager
        assert isinstance(manager, ChatManager)
        self.manager = manager # chat manager for sending messages
        self.run_infinite_loop = True
        self.msg_process_loop = Thread(
            target=self.process_all_messages
        ) # message processing loop
        self.msg_process_loop.start()
        self.msg_process_loop_started = True
        self.KEY = b'0123456789abcdef0123456789abcdef'
        self.secret_key = self.KEY

    def append_msg_to_process(self, msg_json):
        '''
        Append a message to the list of all retrieved messages

        :param msg_json: the message in JSON encoding
        :return:
        '''
        self.all_messages.append(msg_json)

    def append_msg_to_printed_msgs(self, msg):
        '''
        Append a message to the list of printed messages

        :param msg: an instance of the Message class
        :return:
        '''
        assert isinstance(msg, Message)
        self.printed_messages.append(msg)

    def exit(self):
        '''
        Called when the application exists, breaks the infinite loop of message processing

        :return:
        '''
        self.run_infinite_loop = False
        if self.msg_process_loop_started == True:
            self.msg_process_loop.join()

    def process_all_messages(self):
        '''
        An (almost) infinite loop, that iterates over all the messages received from the server
        and passes them for processing

        The loop is broken when the application is exiting
        :return:
        '''
        while self.run_infinite_loop:
            for i in range(0, len(self.all_messages)):
                current_msg = self.all_messages[i]
                msg_raw = ""
                msg_id = 0
                owner_str = ""
                try:
                    # Get raw data of the message from JSON document representing the message
                    msg_raw = base64.decodestring(current_msg["content"])
                    # Base64 decode message
                    msg_id = int(current_msg["message_id"])
                    # Get the name of the user who sent the message
                    owner_str = current_msg["owner"]
                except KeyError as e:
                    print "Received JSON does not hold a message"
                    continue
                except ValueError as e:
                    print "Message ID is not a valid number:", current_msg["message_id"]
                    continue
                if msg_id > self.last_processed_msg_id:
                    # If the message has not been processed before, process it
                    self.process_incoming_message(msg_raw=msg_raw,
                                                  msg_id=msg_id,
                                                  owner_str=owner_str)
                    # Update the ID of the last processed message to the current
                    self.last_processed_msg_id = msg_id
                sleep(0.01)

    def setup_conversation(self):
        '''
        Prepares the conversation for usage, only called by the initial conversation creator
        :return:
        '''
        # You can use this function to initiate your key exchange
        # Useful stuff that you may need:
        # - name of the current user: self.manager.user_name
        # - list of other users in the converstaion: list_of_users = self.manager.get_other_users()
        # You may need to send some init message from this point of your code
        # you can do that with self.process_outgoing_message("...") or whatever you may want to send here...

        # Since there is no crypto in the current version, no preparation is needed, so do nothing
        # replace this with anything needed for your key exchange


        # self.secret_key = Random

        self.secret_key = b'abcdef01234567890123456789abcdef'

        users = self.manager.get_other_users()


        RSA_public_keys = open('users_public_RSA.json', 'rb')
        publicRSAs = json.load(RSA_public_keys)
        RSA_public_keys.close()

        for u in users:
            pubkey = RSA.importKey(publicRSAs[u])
            cipher = PKCS1_OAEP.new(pubkey)
            key    = RSA.importKey(publicRSAs[u])
            msg    = cipher.encrypt(self.secret_key)
            msg    = self.format_and_sign_message(TYPE_KEY, self.manager.user_name, u, msg)
            self.manager.post_message_to_conversation(base64.encodestring(msg))

    def enter_conversation(self):
        '''
        Called by everyone when they enter the conversation
        '''
        pass


    def check_signature(self, content, sender, signature):
        '''
        :param content: message that was signed
        :param sender: sender of message. Look up their public key in file
        :param signature: signature to verify
        :return: bool
        '''

        h = SHA.new()
        h.update(content)

        key_file = open('users_public_RSA.json', 'rb')
        public_keys = json.load(keyFile)
        key_file.close()

        p_key = RSA.importKey(publicKeys[sender])
        verifier = PCKS1_PSS.new(p_key)

        return verifier.verify(h, signature)

    def process_incoming_message(self, msg_raw, msg_id, owner_str):
        '''
        Process incoming messages
        :param msg_raw: the raw message
        :param msg_id: ID of the message
        :param owner_str: user name of the user who posted the message
        :param user_name: name of the current user
        :param print_all: is the message part of the conversation history?
        :return: None
        '''

        # process message here
		# example is base64 decoding, extend this with any crypto processing of your protocol
        decoded_msg = base64.decodestring(msg_raw)

        msg_type, sender, receiver, content, signature = self.unformat_message(decoded_msg)

        if receiver != self.manager.user_name and receiver != ALL:
            return

        if not self.check_signature(content, sender, signature):
            return

        if msg_type == TYPE_KEY:
            cipher = PKCS1_OAEP.new(self.manager.RSA_private)
            self.secret_key = cipher.decrypt(message)
        else:
            iv = decoded_msg[0:AES.block_size]
            enc_msg = decoded_msg[AES.block_size:]
            cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
            dec_msg = cipher.decrypt(enc_msg)
            dec_msg = depad_TLS(dec_msg)

            # print message and add it to the list of printed messages
            self.print_message(
                msg_raw=dec_msg,
                owner_str=owner_str
            )

    def process_outgoing_message(self, msg_raw, originates_from_console=False):
        '''
        Process an outgoing message before Base64 encoding

        :param msg_raw: raw message
        :return: message to be sent to the server
        '''

        msg_padded = pad_TLS(AES.block_size, msg_raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        msg_content = iv + cipher.encrypt(msg_padded)


        # if the message has been typed into the console, record it, so it is never printed again during chatting
        if originates_from_console:
            # message is already seen on the console
            m = Message(
                owner_name=self.manager.user_name,
                content=msg_raw
            )
            self.printed_messages.append(m)

        # process outgoing message here
		# example is base64 encoding, extend this with any crypto processing of your protocol
        msg_formatted = self.format_and_sign_message(TYPE_MESSAGE, self.manager.user_name, ALL, msg_content)
        encoded_msg = base64.encodestring(msg_formatted)

        # post the message to the conversation
        self.manager.post_message_to_conversation(encoded_msg)

    def print_message(self, msg_raw, owner_str):
        '''
        Prints the message if necessary

        :param msg_raw: the raw message
        :param owner_str: name of the user who posted the message
        :return: None
        '''
        # Create an object out of the message parts
        msg = Message(content=msg_raw,
                      owner_name=owner_str)
        # If it does not originate from the current user or it is part of conversation history, print it
        if msg not in self.printed_messages:
            print msg
            # Append it to the list of printed messages
            self.printed_messages.append(msg)

    def __str__(self):
        '''
        Called when the conversation is printed with the print or str() instructions
        :return: string
        '''
        for msg in self.printed_messages:
            print msg

    def get_id(self):
        '''
        Returns the ID of the conversation
        :return: string
        '''
        return self.id

    def get_last_message_id(self):
        '''
        Returns the ID of the most recent message
        :return: number
        '''
        return len(self.all_messages)


    def format_and_sign_message(self, msg_type, sender, receiver, content):
        h = SHA.new()
        h.update(content)
        signer = PKCS1_PSS.new(self.manager.RSA_private)
        signature = signer.sign(h)
        message = str(msg_type) + pad_TLS(NAME_LEN, sender) + pad_TLS(NAME_LEN, receiver) + content + signature
        return message

    def unformat_message(self, message):
        msg_type = int(message[0:1])
        sender = depad_TLS(message[1:NAME_LEN+1])
        receiver = depad_TLS(message[NAME_LEN+1:NAME_LEN*2+1])
        content = message[NAME_LEN*2+1:len(message)-SIG_LEN]
        signature = message[len(message)-SIG_LEN]
        return (msg_type, sender, receiver, content, signature)


def pad_TLS(length, raw):
    plength = length - (len(raw) % length)
    return raw + chr(plength) * plength

def depad_TLS(padded):
    return padded[:len(padded)-ord(padded[-1])]