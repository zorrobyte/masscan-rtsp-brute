# Description

This script captures the first image of an RTSP stream from a list of IP addresses, using `masscan` to automatically find open RTSP streams and `ffmpeg` to capture the image. The script tries each RTSP route and each set of credentials until a stream is found, and saves the captured image to a folder with the current date and time as the name. The script is threaded for performance, and `ffmpeg` is set to timeout after 30 seconds if it is unable to access the stream.

# Usage

python capture_rtsp_image.py [OPTIONS]


## Options

- `-h`, `--help`: Show the help message and exit
- `--ip_addresses_file TEXT`: Text file containing a list of IP addresses (one per line) (optional)
- `--rtsp_routes_file TEXT`: Text file containing a list of RTSP routes (one per line)
- `--credentials_file TEXT`: Text file containing a list of usernames and passwords (one per line, separated by a colon)
- `--ports TEXT`: Comma-separated list of ports to scan for RTSP streams
- `--timeout INTEGER`: Timeout for the `masscan` scan (in milliseconds)
- `--range TEXT`: Range of IP addresses to scan (e.g. 192.168.1.1-192.168.1.255)

## Examples

Scan for open RTSP streams on ports 554 and 8554, using a timeout of 1000 milliseconds, and try each RTSP route and each set of credentials for each IP address until a stream is found:

`python capture_rtsp_image.py --rtsp_routes_file routes.txt --credentials_file credentials.txt --ports 554,8554 --timeout 1000`

Scan for open RTSP streams on ports 554 and 8554 in the range 192.168.1.1 to 192.168.1.255, using a timeout of 1000 milliseconds, and try each RTSP route and each set of credentials for each IP address until a stream is found:

`python capture_rtsp_image.py --rtsp_routes_file routes.txt --credentials_file credentials.txt --ports 554,8554 --timeout 1000 --range 192.168.1.1-192.168.1.255`

Use the IP addresses in the `ip_addresses.txt` file, and try each RTSP route and each set of credentials for each IP address until a stream is found:

`python capture_rtsp_image.py --ip_addresses_file ip_addresses.txt --rtsp_routes_file routes.txt --credentials_file credentials.txt`

# Dependencies

- `masscan`: To find open RTSP streams on the specified ports
- `ffmpeg`: To capture the first frame of the RTSP stream

# Notes

- The script assumes that `masscan` and `ffmpeg` are installed and available in the PATH.
- The script creates a folder to store the captured images, using the current date and time as the folder name. The folder is created in the `images` folder in the current working directory
- Please note that the code in this repository is untested and may contain errors or bugs. Use the code at your own risk and thoroughly test it before using it in any production environments. The authors of this repository do not provide any warranties or guarantees regarding the performance or reliability of the code.

# Legal Disclaimer 
The information provided in this GitHub repository is for informational and educational purposes only. The authors of this repository do not endorse or recommend the use of the scripts or code contained in this repository for any illegal or unauthorized purposes. The authors of this repository shall not be held liable for any damages or consequences resulting from the use of the scripts or code contained in this repository. The use of the scripts or code contained in this repository is at the user's own risk, and the user is solely responsible for compliance with all applicable laws and regulations, including any requirements for obtaining written permission before conducting security testing on any systems or networks. The authors of this repository do not provide any warranties or guarantees, express or implied, regarding the scripts or code contained in this repository or their performance. By using the scripts or code contained in this repository, the user confirms that they have read and understood this disclaimer, and that they will use the scripts or code in a responsible and legal manner.
