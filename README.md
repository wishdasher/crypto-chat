The crypto-chat extends the provided chatroom program extended with security features. Most of these do not directly concern the user, as they happen automatically. However, there are a couple elements that do differ from the provided chatroom program that do demand notice:

- User files now hold the user’s private RSA key as well. New users must make sure they include this in their json file—otherwise, they will not be able to decrypt any messages.

- There is a file of public RSA keys of all users that is available to everybody. Make sure new users add their public keys to this list. In the real world, a certificate authority would issue certificates that certify the public keys.

- Upon creating a chat room, the user automatically join said chatroom. This aids proper RSA key distribution functionality. Moreover, we see this as a design feature, not just a side-effect: who creates a chat room and then doesn’t want to join it immediately? 

- If the user switches from chat room A to B, but then rejoins A, they will only be able to see messages sent in the time they were gone. Messages predating that will not be visible. This is a conscious choice thought by us to be more user-friendly. To see old messages, the user may scroll up in the terminal.

- However, if the user closes the chat program, reopens it, and joins A, they will be able to see all backlogged messages as long as the server has not disconnected. 

- Proposal design changes are explained in the proposal_design_changes.pdf file.

