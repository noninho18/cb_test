import ssh2
import ssh2.session
import socket
import gnupg
import hashlib
import os
import sys
import time
import matplotlib.pyplot as plt
import concurrent.futures
from multiprocessing import Pool

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))
sys.path.append(base_dir)

from card_check.analysis import card_checker

from ssh2.sftp import LIBSSH2_FXF_READ, LIBSSH2_SFTP_S_IRUSR


hostname = '172.18.247.58'
port = 22
username = "elion"
remote_files = ["credit_card_numbers.txt","metadata.txt"]
local_files = remote_files

gpg = gnupg.GPG(gnupghome='./.gnupg')
gpg.encoding = 'utf-8'

input_data = gpg.gen_key_input(name_email = 'elion_hashani@hotmail.fr', passphrase='elion', key_type = 'RSA', key_length = 1024)
key = gpg.gen_key(input_data)

def download_file_sftp(hostname, port, username, remote_files, local_files):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))

    session = ssh2.session.Session()
    session.handshake(sock)
    
    print("Handshake successful. Attempting to authenticate...")
    
    try:
        session.userauth_password(username, username)
        print("Authentication successful")
    except ssh2.exceptions.FileError as e:
        print("File error during authentication:", e)
        raise
    except Exception as e:
        print("Authentication failed:", e)
        raise
    
    sftp = session.sftp_init()
    
    for remote_file in remote_files:
        remote_handle = sftp.open(remote_file, LIBSSH2_FXF_READ, LIBSSH2_SFTP_S_IRUSR)

        file_content = b""
        with remote_handle:
            while True:
                bytes_read, data = remote_handle.read(1000000)
                if not data:
                    break
                file_content += data
        
        gpg = gnupg.GPG()
        encrypted_data = gpg.encrypt(file_content, recipients=['elion_hashani@hotmail.fr'], symmetric=True, passphrase='elion')
        
        if encrypted_data.ok:
            with open(remote_file + '.gpg', 'wb') as f:
                f.write(encrypted_data.data)
            print("File encrypted and downloaded successfully!")
        else:
            print("Encryption failed:", encrypted_data.status)
            print("Error message:", encrypted_data.stderr)
        remote_handle.close()
    
    
def upload_file(file_path, metadata, passphrase):
    with open(metadata, 'rb') as f:
        data = f.read()
    data_decrypt = gpg.decrypt(data, passphrase=passphrase)
    if data_decrypt.ok:
        offsets = data_decrypt.data.decode('utf-8').split("\r\n")[:-1]
        offset = int(offsets[0])
        lengths = [int(length) for length in offsets[2:]]

    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = gpg.decrypt(encrypted_data, passphrase=passphrase)

    if decrypted_data.ok:
        decrypted_file_path = file_path[:-4] 
        with open(decrypted_file_path, 'wb') as f:
            L = decrypted_data.data.decode('utf-8').split("\r\n")[:-1]
            
            milestones, times, true_cards = analysis(L)

            # Plotting the results
            plt.plot(milestones, times, marker='o')
            plt.xlabel('Number of Elements')
            plt.ylabel('Time (seconds)')
            plt.title('Runtime Analysis')
            plt.grid(True)
            plt.savefig('graph.png')
            plt.show()
            
            for line in L[:-1]:
                hashed_line = hashlib.sha256(line.encode('utf-8')).hexdigest()
                hashed_line_bytes = bytes(hashed_line, 'utf-8')
                prepend_hash = os.urandom(offset).hex()
                append_hash = os.urandom(900-offset-len(hashed_line_bytes)).hex()
                full_hash = prepend_hash.encode('utf-8') + hashed_line_bytes + append_hash.encode('utf-8')
                f.write(full_hash + b'\r\n')
            hashed_line = hashlib.sha256(L[-1].encode('utf-8')).hexdigest()
            hashed_line_bytes = bytes(hashed_line, 'utf-8')
            prepend_hash = os.urandom(offset).hex()
            append_hash = os.urandom(900-offset-len(hashed_line_bytes)).hex()
            full_hash = prepend_hash.encode('utf-8') + hashed_line_bytes + append_hash.encode('utf-8')
            f.write(full_hash + b'\r\n')
        print("File decrypted successfully!")
        return decrypted_file_path
    else:
        print("Decryption failed:", decrypted_data.status)
        print("Error message:", decrypted_data.stderr)
        return None
    
def analysis(L):
    milestones = [1000,5000,10000,25000,50000,75000,100000]
    times = []
    for i in milestones:
        print(f"Starting the process for a list of {i} elements !\n")
        start_time = time.time()
        results,true_cards, true_cards_list = card_checker(L[:i])
        end_time = time.time()
        elapsed_time = end_time - start_time
        times.append(elapsed_time)
        print(f"Time taken for {i} elements: {elapsed_time} seconds")
    return milestones, times, true_cards


if __name__ == "__main__":
    # download_file_sftp(hostname, port, username, remote_files, local_files)
    upload_file('credit_card_numbers.txt.gpg','metadata.txt.gpg','elion')