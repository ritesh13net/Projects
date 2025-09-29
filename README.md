Project: Remote File Downloader using Paramiko library

This script uses the Paramiko library to connect to a remote server over SSH. It first verifies if the file exists on the remote server using an ls command. If the file exists, it opens an SFTP session and downloads the file to the local machine. The script also uses the sys module to take command-line arguments for hostname, port, username, password, remote file path, and local file path. Error handling is included, and the SSH connection is always closed at the end.
