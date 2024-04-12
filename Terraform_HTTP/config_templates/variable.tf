variable "api_token" {
  description = "DigitalOcean API token"
  default = "DigitalOcean_API_Token"
}

variable "wireguard_private_key" {
  description = "WireGuard private key"
  default = [
    "SERVER-PRIVATE-KEY "
    ]
}


variable "pubkeys" {
  description = "WireGuard clients pubkeys"
  default = [
    "CLIENT-PUB-KEY"
  ]
}



variable "cloudflare_api_token" {
  type        = string
  description = "cloudflare api token"
  default = "CLoudflare_API_Token"
}
