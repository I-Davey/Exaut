from __important.PluginInterface import PluginInterface
from __important.PluginInterface import Types as T
import base64
import hashlib
import time
from Crypto.Cipher import AES
import json
import os

class sejda_verify(PluginInterface):
    load = True
    type_types = {"__Name":"Sejda Registration"}

    callname = "sejda_verify"
    hooks_handler = ["log"]
    Popups = object

    


    def load_self(self, hooks):
        self.logger = hooks["log"]
        self.salt = "ldsi82734x76%%%%6((NBV@#$%bdnmsda&$$dsvdsytt6%%^&*(((*&^%$FVBnjhgfrstyus8duyhdudyt%$%^^^^^%$$$$%^^%$987";
        self.secret = "k1876213tgv23jnbvc23%^&^%$#))(**&&^^%$$%^&***&^%$#savdafsfdrqtyuiwuqgefqwtyuigvdsakdjastd5$#$%^&&^%$swqSDFGHFDSD"
        self.key =  "8A7F1955-742C-407A-975B-D7A9EFE87F40"
        return True


    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self) -> bool:

    
        expires = time.time() * 1000 + 31536000000
        expires = int(expires)
        data_unencrypted = {
            "key": self.key,
            "expires": expires
            };
        token = self.encrypt(self.secret, data_unencrypted)
        prefs = os.path.join(os.getenv('APPDATA'), "sejda-desktop", "prefs.json") 
        current_prefs = {}
        with open(prefs, 'r') as f:
            current_prefs = json.load(f)

        current_prefs['licenseExpires'] = expires
        current_prefs['licenseToken'] = token
        current_prefs['licenseKey'] = self.key


        #writes to file
        with open(prefs, 'w') as f:
            json.dump(current_prefs, f)
        expires_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires/1000))
        self.logger.success(f"Successfully registered Sejda Desktop until {expires_str}")


    def keytospec(self, key):
        #salt + key
        combined = self.salt + key
        #get bytes
        combined = combined.encode('utf-8')
        #/*    */     MessageDigest sha = MessageDigest.getInstance("SHA-1");

        sha = hashlib.sha1()
        sha.update(combined)
        combined_sha = sha.digest()
        combined_sha = combined_sha[:16]
        return combined_sha



    def decrypt(self, key, encryptedvalue):
        key = self.keytospec(key)
        cipher = AES.new(key, AES.MODE_ECB)
        encryptedvalue = base64.b64decode(encryptedvalue)
        decrypted = cipher.decrypt(encryptedvalue)
        #decrypted = b'{"key":"8A7F1955-742C-407A-975B-D7A9EFE87F44","expires":1675307908000}\n\n\n\n\n\n\n\n\n\n'
        #remove b' for string comparison
        return decrypted


    def encrypt(self, key, value):
        #output has to perfectly match data['token'], data must also be aligned to block size
        #ValueError: Data must be aligned to block boundary in ECB mode
        key = self.keytospec(key)
        cipher = AES.new(key, AES.MODE_ECB)
        value = json.dumps(value)
        #remove space after : and ,
        value = value.replace(" ", "")
        
        
        value = value.encode('utf-8')
        #pad with newlines
        value = value + b'\n' * (16 - len(value) % 16)


        encrypted = cipher.encrypt(value)
        encrypted = base64.b64encode(encrypted)
        #parse as string for comparison
        encrypted = encrypted.decode('utf-8')
        #
        return encrypted

        #decode base64
