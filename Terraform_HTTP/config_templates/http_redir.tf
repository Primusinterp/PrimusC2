provider "digitalocean" {
  token = var.api_token
}

resource "digitalocean_ssh_key" "default" {
  name       = "digiocean-key"
  public_key = file("~/.ssh/id_rsa.pub")
}


# Droplet
resource "digitalocean_droplet" "redirector" {
  image              = "ubuntu-20-04-x64"
  name               = "C2-Redirector"
  region             = "FRA1"
  size               = "s-1vcpu-1gb"
  monitoring         = true
  private_networking = true
  ssh_keys = [digitalocean_ssh_key.default.fingerprint ]


  connection {
    type        = "ssh"
    user        = "root"
    private_key = file("~/.ssh/id_rsa")
    host        = digitalocean_droplet.redirector.ipv4_address
    }

  provisioner "file" {
    source      = "redir"
    destination = "/opt/redir"
  }


  provisioner "remote-exec" {
  inline = [
    "sed -i -r 's/^#.*_forward.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf",
    "sed -i -r 's/^#.*[.]forward.*/net.ipv6.conf.all.forwarding=1/' /etc/sysctl.conf",
    "sysctl -p",
    "echo 1 > /proc/sys/net/ipv4/ip_forward",
    "echo 1 > /proc/sys/net/ipv6/conf/all/forwarding"
    ]
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /opt/redir/http_script.sh",
      "bash /opt/redir/http_script.sh",
      "sleep 5",
      "/bin/bash -c 'cd /opt/redir && nohup screen -S Caddy -dm docker-compose up'",
      "sleep 1"
      
    ]

  }

  provisioner "file" {
  content = local.server_template
  destination = "/etc/wireguard/wg0.conf"
  }


  provisioner "remote-exec" {
    inline = [
      "systemctl enable wg-quick@wg0",
      "systemctl start wg-quick@wg0",
      "sleep 1"
    ]
}
    
}

output "droplet_ip_address" {
  value = digitalocean_droplet.redirector.ipv4_address
}

resource "digitalocean_firewall" "redirector" {
  name = "22-80-443-51820"

  droplet_ids = [digitalocean_droplet.redirector.id]

    inbound_rule {
      protocol         = "tcp"
      port_range       = "22"
      source_addresses = ["0.0.0.0/0", "::/0"]
  }

    inbound_rule {
      protocol         = "tcp"
      port_range       = "443"
      source_addresses = ["0.0.0.0/0", "::/0"]
  }

    inbound_rule {
    protocol         = "udp"
    port_range       = "51820"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

    inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

      
}


data "cloudflare_zone" "this" {
  name = "DOMAIN"
}

resource "cloudflare_record" "foobar" {
  zone_id = data.cloudflare_zone.this.id
  name    = "SUB"
  value   = digitalocean_droplet.redirector.ipv4_address
  type    = "A"
  proxied = false
}

output "record" {
  value = cloudflare_record.foobar.hostname
}

output "metadata" {
  value       = cloudflare_record.foobar.metadata
  sensitive   = false
}

