Project: Remote File Downloader using Paramiko

This Python project allows you to securely connect to a remote server via SSH and download files using SFTP. It uses the paramiko library for SSH/SFTP operations and sys for handling command-line arguments. The script checks if the file exists on the remote server before downloading and handles errors gracefully.

🔹 Features:
Connects to remote servers via SSH
Validates file existence using remote ls command
Downloads files securely using SFTP
Accepts command-line arguments (hostname, port, username, password, remote file path, local file path)
Includes error handling and ensures proper connection closure



