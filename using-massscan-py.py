import os
import subprocess
import tempfile
import argparse
import datetime
import concurrent.futures
import masscan

def capture_image(ip_address, rtsp_route, username, password, image_folder):
    # Construct the RTSP URL
    rtsp_url = f"{rtsp_route}/{ip_address}"

    # Use ffmpeg to capture the first frame of the stream to a temporary file, including the username and password if provided
    ffmpeg_args = ["ffmpeg", "-y", "-timeout", "30", "-i", rtsp_url, "-vframes", "1", "-threads", "4"]
    if username:
        ffmpeg_args += ["-user", username]
    if password:
        ffmpeg_args += ["-passwd", password]
    with tempfile.NamedTemporaryFile() as image_file:
        ffmpeg_args += [image_file.name]
        ffmpeg_output = subprocess.run(ffmpeg_args, capture_output=True).stdout

        # Check if the image was successfully captured
        if "Invalid data found" not in ffmpeg_output:
            # Save the image to the image folder
            image_path = os.path.join(image_folder, f"{ip_address}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_file.read())

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("ip_addresses_file", nargs="?", help="Text file containing a list of IP addresses (one per line)")
parser.add_argument("rtsp_routes_file", help="Text file containing a list of RTSP routes (one per line)")
parser.add_argument("credentials_file", help="Text file containing a list of usernames and passwords (one per line, separated by a colon)")
parser.add_argument("-p", "--ports", required=True, help="Comma-separated list of ports to scan for RTSP streams")
parser.add_argument("-t", "--timeout", type=int, default=1000, help="Timeout for the masscan scan (in milliseconds)")
parser.add_argument("--range", help="Range of IP addresses to scan (e.g. 192.168.1.1-192.168.1.255)")
args = parser.parse_args()

# Read the list of RTSP routes from the specified text file
with open(args.rtsp_routes_file) as f:
    rtsp_routes = f.read().splitlines()

# Read the list of usernames and passwords from the specified text file
with open(args.credentials_file) as f:
    credentials = [(line.split(":")[0], line.split(":")[1]) for line in f.read().splitlines()]

# Create a folder to store the captured images, using the current date and time as the folder name
now = datetime.datetime.now()
image_folder = os.path.join("images", now.strftime("%Y-%m-%d_%H-%M-%S"))
os.makedirs(image_folder, exist_ok=True)

# If an IP addresses file was specified, read the list of IP addresses from the file
if args.ip_addresses_file:
    with open(args.ip_addresses_file) as f:
        ip_addresses = f.read().splitlines()

# Otherwise, use masscan to scan for open RTSP streams on the specified ports
else:
    # Construct the masscan command-line arguments
    masscan_args = ["masscan", "-p", args.ports, "--max-rate", "1000", "--wait", str(args.timeout)]
    if args.range:
        masscan_args += ["--range", args.range]

    # Scan for open RTSP streams using masscan
    scanner = masscan.PortScanner()
    scanner.scan(arguments=' '.join(masscan_args))

    # Extract the list of IP addresses with open RTSP streams
    ip_addresses = [host for host in scanner.all_hosts if scanner[host]['tcp'].get(args.ports)]

# Create a thread pool
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # Try each RTSP route and each set of credentials until a stream is found
    for rtsp_route in rtsp_routes:
        for username, password in credentials:
            # Submit a task for each IP address to capture an image from the RTSP stream
            for ip_address in ip_addresses:
                executor.submit(capture_image, ip_address, rtsp_route, username, password, image_folder)
