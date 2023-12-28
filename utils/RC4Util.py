import codecs

#Copyright (c) 2017 Manoj Pandey

class RC4:
    MOD = 256
    def KSA(self,key):
        key_length = len(key)
        S = list(range(self.MOD))  
        j = 0
        for i in range(self.MOD):
            j = (j + S[i] + key[i % key_length]) % self.MOD
            S[i], S[j] = S[j], S[i]  

        return S

    def PRGA(self ,S):
        i = 0
        j = 0
        while True:
            i = (i + 1) % self.MOD
            j = (j + S[i]) % self.MOD

            S[i], S[j] = S[j], S[i]  #
            K = S[(S[i] + S[j]) % self.MOD]
            yield K
        
    def get_keystream(self ,key):
        S = self.KSA(key)
        return self.PRGA(S)


    def encrypt_logic(self,key, text):

        key = [ord(c) for c in key]
        keystream = self.get_keystream(key)

        res = []
        for c in text:
            val = ("%02X" % (c ^ next(keystream))) 
            res.append(val)
        return ''.join(res)


    def obf(self,key, plaintext):
        plaintext = [ord(c) for c in plaintext]
        return self.encrypt_logic(key, plaintext)


    def deobf(self,key, ciphertext):
        ciphertext = codecs.decode(ciphertext, 'hex_codec')
        res = self.encrypt_logic(key, ciphertext)
        return codecs.decode(res, 'hex_codec').decode('utf-8')
    

