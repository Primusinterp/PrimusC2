terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
      cloudflare = {
        source = "cloudflare/cloudflare"
    }

  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}
