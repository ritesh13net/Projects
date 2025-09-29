import sys
import paramiko

def download_file(hostname, port, username, password, remote_filepath, local_filepath):
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=port, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command('ls ' + remote_filepath)
        read_stdout = stdout.read()
        if len(read_stdout) > 0:
            remote_filepath = read_stdout.split()[0].strip()
            sftp = ssh.open_sftp()
            sftp.get(remote_filepath, local_filepath)
            sftp.close()

            # print(f"File downloaded to {local_filepath}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()


if __name__ == "__main__":
    hostname = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    remote_filepath = sys.argv[5]
    local_filepath = sys.argv[6]

    download_file(hostname, port, username, password, remote_filepath, local_filepath)

