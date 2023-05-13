

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




  provisioner "file" {
    source      = "script.sh"
    destination = "/tmp/script.sh"
  }

    connection {
    type        = "ssh"
    user        = "root"
    private_key = file("~/.ssh/id_rsa")
    host        = digitalocean_droplet.redirector.ipv4_address
    }
    
    provisioner "remote-exec" {
      inline = [
        "chmod +x /tmp/script.sh"
    ]
  }

    
}

output "droplet_ip_address" {
  value = digitalocean_droplet.redirector.ipv4_address
}

resource "digitalocean_firewall" "redirector" {
  name = "only-22-LPORT"

  droplet_ids = [digitalocean_droplet.redirector.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "LPORT"
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

