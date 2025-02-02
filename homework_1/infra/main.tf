provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "datatalks_de_s3" {
  bucket = var.bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_lifecycle_configuration" "datatalks_de_lifecycle" {
  bucket = aws_s3_bucket.datatalks_de_s3.bucket

  rule {
    id = "delete_incomplete_multipart_upload"
    status = "Enabled"
    abort_incomplete_multipart_upload  {
      days_after_initiation = 1
    }
  }
  
  depends_on = [
    aws_s3_bucket.datatalks_de_s3 
  ]
}

resource "aws_redshift_cluster" "datatalks_de_redshift" {
  cluster_identifier  = var.redshift_cluster
  database_name       = var.redshift_database
  master_username     = var.redshift_username
  master_password     = var.redshift_password
  skip_final_snapshot = true 
  node_type           = "dc2.large"
  cluster_type        = "single-node"
}