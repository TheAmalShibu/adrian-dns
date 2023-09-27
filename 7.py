from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
import re  # Import the re module for regular expressions

app = Flask(__name__)

# Nginx sites-enabled directory
nginx_sites_enabled_dir = '/etc/nginx/sites-enabled/'

# Variable to store the current configuration
current_config = None

@app.route('/')
def index():
    global current_config
    # Clear the current_config when rendering the index page
    current_config = None
    return render_template('index.html', current_config=current_config)

@app.route('/configure-proxy', methods=['POST'])
def configure_proxy():
    global current_config
    domain = request.form.get('domain')
    ip = request.form.get('ip')
    port = request.form.get('port')

    # Determine the protocol (http:// or https://) based on the input URL
    protocol = "http"
    match = re.match(r'^(https?://)', domain)
    if match:
        protocol = match.group(1)[:-3]  # Remove the trailing "://"
        domain = domain.replace(match.group(1), "")

    # Create a subdomain for the input domain
    if domain.startswith("www."):
        subdomain = domain.split('.')[1]  # Use the second part of the domain as subdomain
    else:
        subdomain = domain.split('.')[0]

    subdomain = f"{subdomain}.syst3mburn3r.tech"
    current_config = {'domain': domain, 'ip': ip, 'subdomain': subdomain, 'port': port}

    # Check if the configuration file already exists
    config_path = os.path.join(nginx_sites_enabled_dir, subdomain)
    if os.path.isfile(config_path):
        # Configuration file already exists, so overwrite it
        with open(config_path, 'w') as config_file:
            config = f"""
            server {{
                listen {port or '80'};  # Use the provided port or default to 80
                server_name {subdomain};

                location / {{
                    proxy_pass {protocol}://{ip}:{port or '80'};  # Use the provided port or default to 80
                    proxy_set_header Host {domain};
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                }}
            }}
            """
            config_file.write(config)

        # Reload Nginx to apply the new configuration
        subprocess.run(['sudo', 'nginx', '-s', 'reload'])

        # Run the DNS update using nsupdate
        dns_update(subdomain, ip)

    else:
        # Configuration file doesn't exist, create a new one
        config = f"""
        server {{
            listen {port or '80'};  # Use the provided port or default to 80
            server_name {subdomain};

            location / {{
                proxy_pass {protocol}://{ip}:{port or '80'};  # Use the provided port or default to 80
                proxy_set_header Host {domain};
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }}
        }}
        """

        # Write the Nginx configuration to a new file in sites-enabled
        with open(config_path, 'w') as config_file:
            config_file.write(config)

        # Reload Nginx to apply the new configuration
        subprocess.run(['sudo', 'nginx', '-s', 'reload'])

        # Run the DNS update using nsupdate
        dns_update(subdomain, ip)

    # Redirect to the result page
    return redirect(url_for('result'))

def dns_update(subdomain, ip):
    # Define the nsupdate commands as a string
    nsupdate_commands = f"""
    server 135.181.25.212
    zone syst3mburn3r.tech.
    update add {subdomain}. 300 IN A {"135.181.25.212"}
    send
    """

    # Run the nsupdate commands using subprocess
    try:
        subprocess.run(['nsupdate', '-k', '/var/www/html/skip.key'], input=nsupdate_commands, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"DNS update failed: {e}")
    else:
        print("DNS update successful")

@app.route('/result')
def result():
    return render_template('result.html', current_config=current_config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

