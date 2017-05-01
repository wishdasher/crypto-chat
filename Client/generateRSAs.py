from Crypto.PublicKey import RSA
from Crypto import Random

f = open('RSA-pairs.txt', 'w')

if __name__ == "__main__":
    for i in range (1, 21):
        r = RSA.generate(1024)
        private = r.exportKey('PEM')
        public = (r.publickey()).exportKey('PEM')
        f.write(str(i) + '\n' + private + '\n' + public + '\n\n')
