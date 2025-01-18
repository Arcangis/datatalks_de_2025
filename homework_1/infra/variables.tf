variable "bucket_name" {
  description   = "Bucket Name"
  type          = string
}

variable "redshift_cluster" {
  description   = "Redshift Cluster Name"
  type          = string
}

variable "redshift_database" {
  description   = "Redshift Database Name"
  type          = string
}

variable "redshift_username" {
  description   = "Redshift Masters Username"
  type          = string
}

variable "redshift_password" {
  description   = "Redshift Password"
  type          = string
}