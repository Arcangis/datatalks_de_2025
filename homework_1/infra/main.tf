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

resource "aws_dynamodb_table" "datatalks_de_dynamodb" {
  name             = var.dynamodb_name
  hash_key         = "UUID"
  read_capacity    = 10
  write_capacity   = 10 
  attribute {
    name = "UUID"
    type = "S"
  }
}
