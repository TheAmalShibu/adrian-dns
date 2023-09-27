from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

# Nginx sites-enabled directory
nginx_sites_enabled_dir = '/etc/nginx/sites-enabled/'

# Variable to store the current configuration
current_config = None

@app.route('/')
def index():
    return render_template('index.html', current_config=current_config)

@app.route('/configure-proxy', methods=['POST'])
def configure_proxy():
    global current_config  # Use the global variable to store the current configuration
    domain = request.form.get('domain')
    ip = request.form.get('ip')

    # Create a subdomain for the input domain
    subdomain = f"{domain.split('.')[0]}.syst3mburn3r.tech"
    current_config = {'domain': domain, 'ip': ip, 'subdomain': subdomain}

    # Create Nginx configuration for the subdomain
    config = f"""
    server {{
        listen 80;
        server_name {subdomain};

        location / {{
            proxy_pass http://{ip}:80;
            proxy_set_header Host {domain};
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }}
    }}
    """

    # Write the Nginx configuration to a file in sites-enabled
    nginx_config_path = f'{nginx_sites_enabled_dir}{subdomain}'
    with open(nginx_config_path, 'w') as config_file:
        config_file.write(config)

    # Reload Nginx to apply the new configuration
    subprocess.run(['sudo', 'nginx', '-s', 'reload'])

    # Run the DNS update using nsupdate
    dns_update(subdomain, ip)

    return redirect(url_for('index'))

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

